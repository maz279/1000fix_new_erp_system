# cd_inventory — the stock take-on and the pricing of uncosted stock
# (A06 ERP audit, owner decision D4, 20 Nov 2026).
#
# fix_real holds BDT 165.26M of owned stock on 17,461 on-hand lines and has
# none of it in the GL (X02). The take-on posts ONE journal entry per company
# per operating unit, Dr each stock account (by brand, D2) / Cr 300101, from
# the current on-hand quantity x unit cost of the valued ownership classes,
# writes one initial_count valuation row per bucket posted with that entry,
# and switches the company to real-time stock posting (D1) in the same
# transaction - a movement can never fall between the take-on value and the
# first real-time posting. It returns the zero-cost lines for Finance (4,685
# on fix_real); until Finance prices them (action_price_uncosted_stock: Dr
# stock / Cr 300101) they are counted, issued or written off only with an
# approval (fix_stock_posting, X19).
from __future__ import annotations

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError

from .fix_inventory_approval import VALUED_CLASSES
from .fix_stock_posting import ACCOUNT_ROLES, EPS, role_code
from .fix_valuation_suspense import dhaka_today

FINANCE_MANAGER = "account.group_account_manager"


class FixStockTakeon(models.Model):
    _inherit = "fix.inventory.valuation.suspense"

    @api.model
    def _fix_require_finance_manager(self, what):
        if not self.env.su and not self.env.user.has_group(FINANCE_MANAGER):
            raise AccessError("%s is for an Accounting Administrator (Finance manager)." % what)

    @api.model
    def action_stock_takeon(self, company_id, supersede_pending=False, reference=None):
        """Post the company's stock take-on and switch it to real-time
        posting. Refuses a second run. Rows still pending the old cut-over are
        already inside today's on-hand value: the take-on refuses while any is
        pending, unless `supersede_pending` archives them (with the take-on as
        reference) so that the old cut-over cannot bring them in again."""
        self._fix_require_finance_manager("The stock take-on")
        company = self.env["res.company"].sudo().browse(int(company_id)).exists()
        if not company:
            raise UserError("Unknown company %s." % company_id)
        # one run per company, even with two Finance managers pressing at once
        self.env.cr.execute(
            "SELECT id FROM res_company WHERE id = %s FOR UPDATE NOWAIT", (company.id,)
        )
        company.invalidate_recordset(["fix_stock_realtime_from"])
        if company.fix_stock_realtime_from:
            raise UserError(
                "%s already took its stock on (real-time posting since %s): the take-on runs once."
                % (company.name, company.fix_stock_realtime_from)
            )
        Rows = self.sudo()
        pending = Rows.search(
            [("company_id", "=", company.id), ("status", "=", "pending_gl_cutover")]
        )
        if pending and not supersede_pending:
            raise UserError(
                "%s has %d valuation entries still pending the old cut-over: today's on-hand "
                "value already contains them. Run the take-on with supersede_pending to archive "
                "them against it (nothing is cut over twice); nothing was posted."
                % (company.name, len(pending))
            )
        buckets = (
            self.env["fix.stock.onhand"]
            .sudo()
            .search(
                [
                    ("company_id", "=", company.id),
                    ("ownership_class", "in", VALUED_CLASSES),
                    ("qty", ">", 0),
                ],
                order="location_id, part_id, id",
            )
        )
        # every location's OU and every account, before anything is posted
        ou_of, unresolved = {}, []
        for loc in buckets.mapped("location_id"):
            try:
                ou_of[loc.id] = Rows._fix_location_ou(loc, company)
            except UserError:
                unresolved.append(loc.code or str(loc.id))
        if unresolved:
            raise UserError(
                "%d stock locations of %s holding valued stock have no operating unit (neither "
                "on the location nor on its branch): %s. Set them first; nothing was posted."
                % (len(unresolved), company.name, ", ".join(sorted(unresolved)[:50]))
            )
        groups, zero_cost, plan = {}, [], []
        code_cache = {}
        for bucket in buckets:
            part = bucket.part_id
            if part.id not in code_cache:
                code_cache[part.id] = Rows._fix_stock_code(part)
            code = code_cache[part.id]
            cost = bucket.unit_cost or 0.0
            value = round(bucket.qty * cost, 2)
            ou = ou_of[bucket.location_id.id]
            if cost <= EPS:
                zero_cost.append(
                    {
                        "onhand_id": bucket.id,
                        "part_id": part.id,
                        "part_number": part.part_number,
                        "location_id": bucket.location_id.id,
                        "location": bucket.location_id.code,
                        "ownership_class": bucket.ownership_class,
                        "stock_status": bucket.stock_status,
                        "qty": bucket.qty,
                    }
                )
                continue
            if abs(value) < 0.005:
                continue
            by_code = groups.setdefault(ou.id, {})
            by_code[code] = round(by_code.get(code, 0.0) + value, 2)
            plan.append((bucket, ou, code, value))
        accounts = {
            code: Rows._fix_account(company, code, "Stock (take-on)")
            for by_code in groups.values()
            for code in by_code
        }
        equity = Rows._fix_role_account(company, "takeon_equity") if groups else None
        Rows._fix_journal(company)
        ref = (reference or "").strip() or "Stock take-on %s" % company.name
        OU = self.env["operating.unit"].sudo()
        moves = {}
        for ou_id, by_code in sorted(groups.items()):
            ou = OU.browse(ou_id)
            dims = Rows._fix_dims(ou)
            total = round(sum(by_code.values()), 2)
            lines = [
                (accounts[code], "%s - stock %s" % (ref, code), value, dims)
                for code, value in sorted(by_code.items())
            ] + [(equity, "%s - opening" % ref, -total, dims)]
            moves[ou_id] = Rows._fix_gl_post(
                company,
                dhaka_today(),
                "%s / %s" % (ref, ou.name),
                lines,
                source_ref=ref,
            )
        # 17,461 rows on fix_real: no chatter message per row
        Writer = Rows.with_context(
            fix_stock_no_autopost=True,
            tracking_disable=True,
            mail_create_nolog=True,
            mail_notrack=True,
        )
        now = fields.Datetime.now()
        takeon_code = role_code(self.env, "takeon_equity")
        vals_list = []
        for bucket, ou, code, value in plan:
            vals_list.append(
                {
                    "name": "TKO-%s-%s" % (company.id, bucket.id),
                    "company_id": company.id,
                    "operating_unit_id": ou.id,
                    "location_id": bucket.location_id.id,
                    "product_id": bucket.part_id.id,
                    "quantity": bucket.qty,
                    "unit_cost": bucket.unit_cost,
                    "total_valuation": value,
                    "entry_type": "initial_count",
                    "source_ref": ref,
                    "legacy_reference": "TAKEON:%s" % bucket.id,
                    # posted with its OU's take-on entry (system rows: no user writes them)
                    "status": "posted",
                    "posted_at": now,
                    "move_id": moves[ou.id].id,
                    "stock_account_code": code,
                    "counter_account_code": takeon_code,
                }
            )
        created = Writer.create(vals_list) if vals_list else Rows.browse()
        if pending:
            pending._guarded().write(
                {
                    "status": "archived",
                    "archived_by_id": self.env.uid,
                    "archived_at": now,
                    "archive_ref": "superseded by %s" % ref,
                }
            )
        company._fix_set_realtime(now)
        summary = {
            "company_id": company.id,
            "company": company.name,
            "reference": ref,
            "moves": [
                {"operating_unit": OU.browse(o).name, "move": m.name, "amount": m.amount_total}
                for o, m in sorted(moves.items())
            ],
            "rows": len(created),
            "total_value": round(sum(v for *_x, v in plan), 2),
            "superseded_pending": len(pending),
            "zero_cost_lines": zero_cost,
            "zero_cost_count": len(zero_cost),
            "realtime_since": str(now),
        }
        return summary

    @api.model
    def action_price_uncosted_stock(self, prices, reference):
        """D4: Finance prices stock that carries no cost. prices = [{onhand_id,
        unit_cost}] of unrestricted zero-cost buckets; each is revalued to
        qty x unit_cost, Dr stock / Cr 300101 (the take-on account), through
        the ledger's own revaluation. Finance managers only."""
        self._fix_require_finance_manager("Pricing uncosted stock")
        ref = (reference or "").strip()
        if not ref:
            raise UserError("Give the Finance reference the prices come from.")
        Onhand = self.env["fix.stock.onhand"].sudo()
        counter = role_code(self.env, "takeon_equity")
        done = []
        for item in prices or []:
            bucket = Onhand.browse(int(item.get("onhand_id") or 0)).exists()
            cost = float(item.get("unit_cost") or 0.0)
            if not bucket or bucket.qty <= EPS:
                raise UserError("On-hand line %s holds no stock." % item.get("onhand_id"))
            if (bucket.unit_cost or 0.0) > EPS:
                raise UserError(
                    "%s at %s already carries a cost (%s): it is not uncosted stock."
                    % (bucket.part_id.part_number, bucket.location_id.code, bucket.unit_cost)
                )
            if (
                bucket.stock_status != "unrestricted"
                or bucket.ownership_class not in VALUED_CLASSES
            ):
                raise UserError(
                    "Only unrestricted stock of a valued class is priced here (%s at %s is %s / %s)."
                    % (
                        bucket.part_id.part_number,
                        bucket.location_id.code,
                        bucket.ownership_class,
                        bucket.stock_status,
                    )
                )
            if cost <= EPS:
                raise UserError("A price must be positive.")
            if not self._fix_realtime(bucket.company_id):
                raise UserError(
                    "%s has not taken its stock on: price stock after the take-on."
                    % bucket.company_id.name
                )
            amount = round(bucket.qty * cost, 2)
            Onhand.with_context(fix_stock_counter_account=counter)._fix_revalue(
                bucket.part_id,
                bucket.location_id,
                bucket.ownership_class,
                amount,
                "%s (%s)" % (ref, ACCOUNT_ROLES["takeon_equity"][2]),
            )
            done.append({"onhand_id": bucket.id, "unit_cost": cost, "value": amount})
        return {"priced": len(done), "lines": done, "reference": ref}


class ResCompanyRealtime(models.Model):
    _inherit = "res.company"

    def _fix_set_realtime(self, moment):
        # written only by the take-on (the field is read-only to everyone)
        self.sudo().write({"fix_stock_realtime_from": moment})
