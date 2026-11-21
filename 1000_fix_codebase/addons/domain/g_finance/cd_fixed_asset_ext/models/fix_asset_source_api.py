# fix_asset_source_api — A05 FIN-15 / M13-14 / M13-15: the M49 API another
# module (M13 rental fleet) uses to put a unit on the register, read its book
# value and start its disposal by route. M49 stays the ledger of the unit's
# cost and depreciation: the rental fleet's own stored "book value" never
# aged and was never posted (FIN-15).
#
#   fix.fixed.asset._fix_capitalise_from_source(source, category, gross,
#       purchase_date, credit_account=..., | move_line=..., name=, code=,
#       operating_unit=, salvage=, life_months=, depreciate=True) -> asset
#     Idempotent on `source` (model + id). Either posts the capitalisation
#     (Dr the category's asset account / Cr `credit_account`, dated the Dhaka
#     business day) or adopts an already-posted debit `move_line` of the cost
#     on the asset account (a bill booked to it); then registers the asset
#     from that M19 seam, puts it in service and catches up its depreciation
#     from the acquisition month to the current month in ONE entry of the
#     current (open) period (`_fix_catch_up_depreciation`); the current month
#     is charged by the company's month run like every other asset.
#   asset._fix_book_value(as_of=None) -> float
#     Net book value (cost - depreciation - impairment) from POSTED events;
#     0 once disposed or not yet in service.
#   asset._fix_open_disposal(kind, reason, source=None, ewaste_route=None,
#       device_id=0, weight_kg=0.0, material=False, incident_ref=None,
#       on_date=None) -> fix.asset.disposal (draft; finance submits, the M63
#       route approves, finance posts). kind: 'transfer_resale' (retired unit
#       routed to resale stock), 'recycle', 'scrap', 'sale', 'write_off'.
from odoo import api, fields, models
from odoo.exceptions import UserError

from .fix_asset_common import add_months, money, month_start, post_entry
from .fix_fixed_asset import remaining_straight_line

DHAKA = "Asia/Dhaka"


def _dhaka_today(record):
    return fields.Date.context_today(record.with_context(tz=DHAKA))


class FixFixedAssetSourceApi(models.Model):
    _inherit = "fix.fixed.asset"

    source_model = fields.Char(string="Source Model", readonly=True, copy=False, index=True)
    source_res_id = fields.Integer(string="Source Record", readonly=True, copy=False, index=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"source_model", "source_res_id"}

    # ------------------------------------------------------------ book value
    def _fix_book_value(self, as_of=None) -> float:
        """The unit's net book value in M49 (posted events only)."""
        self.ensure_one()
        if self.state != "active":
            return 0.0
        if as_of is None:
            return money(self.book_nbv)
        from datetime import timedelta

        pos = self._position(before=as_of + timedelta(days=1))
        return money(pos["cost"] - pos["dep"] - pos["imp"])

    # ------------------------------------------------------------ capitalise
    @api.model
    def _fix_capitalise_from_source(
        self,
        source,
        category,
        gross,
        purchase_date,
        credit_account=None,
        move_line=None,
        name=None,
        code=None,
        operating_unit=None,
        salvage=None,
        life_months=None,
        depreciate=True,
    ):
        source.ensure_one()
        Asset = self.sudo()
        existing = Asset.search(
            [("source_model", "=", source._name), ("source_res_id", "=", source.id)], limit=1
        )
        if existing:
            return self.browse(existing.id)
        category = category.sudo()
        if not category:
            raise UserError(
                self.env._("Capitalising %s needs an asset category.", source.display_name)
            )
        gross = money(gross)
        if gross <= 0:
            raise UserError(self.env._("%s has no cost to capitalise.", source.display_name))
        if not (category.asset_account_id and category.journal_id):
            raise UserError(
                self.env._(
                    "Configure the asset account and journal of category %s first.", category.name
                )
            )
        company = (
            (source.company_id if "company_id" in source._fields and source.company_id else None)
            or category.company_id
            or self.env.company
        )
        ou = operating_unit or (
            source.operating_unit_id if "operating_unit_id" in source._fields else None
        )
        label = "Capitalise %s" % (name or source.display_name)
        if move_line:
            line = move_line.sudo()
            if (
                line.parent_state != "posted"
                or line.account_id != category.asset_account_id
                or abs(money(line.balance) - gross) > 0.005
            ):
                raise UserError(
                    self.env._(
                        "%s does not carry the cost of %s: a posted debit of %s on %s is "
                        "required.",
                        line.display_name,
                        source.display_name,
                        gross,
                        category.asset_account_id.display_name,
                    )
                )
            move = line.move_id
        else:
            if not credit_account:
                raise UserError(
                    self.env._(
                        "Capitalising %s posts Dr %s: name the account the cost is credited "
                        "from (credit_account), or the posted journal item that carries it.",
                        source.display_name,
                        category.asset_account_id.display_name,
                    )
                )
            move = post_entry(
                self.env(su=True),
                company,
                category.journal_id,
                _dhaka_today(self),
                label,
                [
                    (category.asset_account_id, gross, 0.0, label),
                    (credit_account, 0.0, gross, label),
                ],
                ou or None,
            )
            line = move.line_ids.filtered(
                lambda ln: ln.account_id == category.asset_account_id and ln.debit
            )[:1]
        Seam = self.env["fix.fixed.asset.seam"].sudo()
        if Seam.search_count([("move_line_id", "=", line.id)]):
            raise UserError(
                self.env._("%s is already the source of another asset.", line.display_name)
            )
        seam_ou = ou or self.env["operating.unit"].sudo().search(
            [("company_id", "=", company.id)], limit=1
        )
        seam = Seam.create(
            {
                "company_id": company.id,
                "operating_unit_id": seam_ou.id,
                "name": label,
                "move_line_id": line.id,
                "amount": gross,
                "currency_id": company.currency_id.id,
                "asset_category": category.code,
            }
        )
        vals = {
            "company_id": company.id,
            "operating_unit_id": ou.id if ou else False,
            "name": name or source.display_name,
            "category_id": category.id,
            "gross": gross,
            "purchase_date": purchase_date,
            "seam_id": seam.id,
            "source_model": source._name,
            "source_res_id": source.id,
        }
        if code:
            vals["code"] = code
        if salvage is not None:
            vals["salvage"] = money(salvage)
        if life_months:
            vals["life_months"] = int(life_months)
        asset = Asset._guarded().create(vals)
        asset._activate_from_seam(seam, move)
        if depreciate:
            asset._fix_catch_up_depreciation()
        return self.browse(asset.id)

    def _fix_catch_up_depreciation(self):
        """Charge every month from the depreciation start up to LAST month
        that has no posted line, in ONE scoped run of the current month (its
        entry falls in the open period; each month keeps its own line, so the
        straight line over the remaining life stays right). The current month
        is the company's month run's, as for every other asset (a charge for
        it now would also refuse a disposal dated this month)."""
        Run = self.env["fix.asset.depreciation.run"].sudo()
        Line = self.env["fix.asset.depreciation.line"].sudo()
        runs = Run
        for asset in self.sudo():
            if asset.state != "active":
                continue
            current = month_start(_dhaka_today(asset))
            month = month_start(asset.depreciation_start or asset.purchase_date)
            charged = set(asset._posted_lines("book").mapped("period_start"))
            pos = asset._position()
            carrying = money(pos["cost"] - pos["dep"] - pos["imp"])
            remaining = asset.life_months - len(charged)
            plan = []
            while month < current and remaining > 0:
                if month not in charged:
                    amount = remaining_straight_line(carrying, asset.salvage or 0.0, remaining)
                    if amount <= 0:
                        break
                    plan.append((month, amount))
                    carrying = money(carrying - amount)
                    remaining -= 1
                month = add_months(month, 1)
            if not plan:
                continue
            run = Run.create(
                {
                    "company_id": asset.company_id.id,
                    "book": "book",
                    "period_start": current,
                    "asset_ids": [(6, 0, asset.ids)],
                }
            )
            Line.create(
                [
                    {
                        "run_id": run.id,
                        "asset_id": asset.id,
                        "book": "book",
                        "period_start": period,
                        "amount": amount,
                    }
                    for period, amount in plan
                ]
            )
            run._guarded().write(
                {
                    "state": "computed",
                    "note": "Capitalisation catch-up: %s month(s) %s..%s."
                    % (len(plan), plan[0][0].strftime("%Y-%m"), plan[-1][0].strftime("%Y-%m")),
                }
            )
            run.action_post()
            runs |= run
        return runs

    # ------------------------------------------------------------ dispose
    def _fix_open_disposal(
        self,
        kind,
        reason,
        source=None,
        ewaste_route=None,
        device_id=0,
        weight_kg=0.0,
        material=False,
        incident_ref=None,
        on_date=None,
    ):
        """Start (or return) this asset's disposal of `kind`, as a draft the
        M49 workflow submits, approves and posts."""
        self.ensure_one()
        asset = self.sudo()
        if asset.state != "active":
            raise UserError(self.env._("%s is not an active asset.", asset.display_name))
        Disposal = self.env["fix.asset.disposal"].sudo()
        kinds = dict(Disposal._fields["kind"].selection)
        if kind not in kinds:
            raise UserError(self.env._("Unknown disposal type %s.", kind))
        if ewaste_route is None:
            # a standalone recycling goes to M18 here; a source that hands the
            # item to M18 itself (the rental retirement event) passes False
            ewaste_route = kind == "recycle" and source is None
        terms = {
            "kind": kind,
            "reason": reason or False,
            "incident_ref": incident_ref or False,
            "ewaste_route": bool(ewaste_route),
            "ewaste_device_res_id": int(device_id or 0),
            "ewaste_weight_kg": float(weight_kg or 0.0),
            "ewaste_material": material or False,
            "date": on_date or _dhaka_today(asset),
        }
        open_ = asset.disposal_ids.filtered(lambda d: d.state in ("draft", "submitted", "approved"))
        if open_:
            disposal = open_[:1]
            if disposal.kind != kind and disposal.state != "draft":
                raise UserError(
                    self.env._(
                        "%s already has disposal %s (%s) in approval: cancel it before "
                        "starting a %s.",
                        asset.display_name,
                        disposal.name,
                        kinds[disposal.kind],
                        kinds[kind],
                    )
                )
            if disposal.state == "draft":
                disposal.write(terms)
        else:
            disposal = Disposal.create(dict(terms, asset_id=asset.id))
        if source is not None:
            disposal._guarded().write({"source_model": source._name, "source_res_id": source.id})
        return self.env["fix.asset.disposal"].browse(disposal.id)
