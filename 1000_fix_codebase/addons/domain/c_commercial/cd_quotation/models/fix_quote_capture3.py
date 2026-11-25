# M36 capture audit, third pass (2026-11-19): the spec items pass 2 left as
# "not built", each now with its capture or its automation.
#
#   p3  FR-QTE-013        version comparison, in customer-readable language
#   p2  FR-QTE-021/022    bulk estate quotation from a corporate asset upload,
#                         per-asset lines with a site / department / cost
#                         centre breakdown
#   p5  FR-QTE-034, T-05  the customer's one-screen approval link: a signed,
#                         expiring token; the page shows no cost or margin and
#                         accepts only on the code sent to the customer's phone
#   p5  FR-QTE-040,       expiry reminders (T-2 / T-1 days) on the customer's
#       AUT-QTE-04/05     channel and a follow-up when unviewed after 24 hours
#   p2  AUT-QTE-10,       a renewal quotation drafted for a contract inside its
#       BRU-QTE-18        renewal lead time
import re
import secrets
from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish

from .fix_quotation import dhaka_today
from .fix_quote_with_customer import CHANNELS
from .fix_tender_boq import _canon, _number, read_rows

REMINDER_DAYS = (2, 1)  # AUT-QTE-05: T-48h and T-24h, by Dhaka date
UNVIEWED_HOURS = 24  # AUT-QTE-04
APPROVAL_PATH = "/quote/view/%s"


def estate_column(header):
    """The estate field an asset-upload header names, or None."""
    h = _canon(header)
    if not h:
        return None
    if h in ("asset", "asset tag", "asset no", "asset id", "serial", "serial no", "tag"):
        return "asset_ref"
    if h.startswith("description") or h in ("item", "equipment", "model"):
        return "description"
    if h in ("site", "location", "branch", "office"):
        return "site_name"
    if h in ("department", "dept"):
        return "department"
    if h in ("cost centre", "cost center", "cost centre code", "cc"):
        return "cost_centre"
    if h in ("qty", "quantity"):
        return "quantity"
    if h in ("unit price", "price", "rate", "unit rate"):
        return "unit_price"
    return None


def parse_estate(rows):
    """(lines, errors) from an asset upload: one priced line per asset."""
    header, cols = None, {}
    for idx, row in enumerate(rows[:15]):
        found = {}
        for pos, cell in enumerate(row or []):
            key = estate_column(cell)
            if key and key not in found:
                found[key] = pos
        if {"description", "unit_price"} <= set(found):
            header, cols = idx, found
            break
    if header is None:
        return [], [
            "No header row names the asset columns: Description and Unit Price are required; "
            "Asset Tag, Site, Department, Cost Centre and Quantity are read when present."
        ]
    lines, errors = [], []

    def cell(row, key):
        pos = cols.get(key)
        return row[pos] if pos is not None and pos < len(row) else None

    for idx, row in enumerate(rows[header + 1 :], start=header + 2):
        row = list(row or [])
        if not any(str(v).strip() for v in row if v is not None):
            continue
        text = {
            k: str(cell(row, k)).strip() if cell(row, k) is not None else ""
            for k in ("asset_ref", "description", "site_name", "department", "cost_centre")
        }
        try:
            qty = _number(cell(row, "quantity"))
            price = _number(cell(row, "unit_price"))
        except ValueError:
            errors.append("Row %d: the quantity or unit price is not a number." % idx)
            continue
        if not text["description"]:
            errors.append("Row %d: the description is empty." % idx)
            continue
        if price is None or price < 0:
            errors.append(
                "Row %d (%s): give a unit price of zero or more." % (idx, text["description"])
            )
            continue
        qty = 1.0 if qty is None else qty
        if qty <= 0:
            errors.append(
                "Row %d (%s): the quantity must be above zero." % (idx, text["description"])
            )
            continue
        lines.append(dict(text, quantity=qty, unit_price=price))
    if not lines and not errors:
        errors.append("The upload has no asset rows under its header.")
    return lines, errors


class FixQuotationLineEstate(models.Model):
    _inherit = "fix.quotation.line"

    # FR-QTE-021/022: the corporate dimensions of an estate line
    asset_ref = fields.Char(string="Asset Tag / Serial")
    site_name = fields.Char(string="Site")
    department = fields.Char()
    cost_centre = fields.Char(string="Cost Centre")


class FixQuotationCapture3(models.Model):
    _inherit = "fix.quotation"

    # ---- FR-QTE-022: the estate upload --------------------------------------
    estate_file = fields.Binary(
        string="Asset Upload (.xlsx / .csv)",
        attachment=True,
        copy=False,
        help="One row per asset: Description and Unit Price, with Asset Tag, Site, "
        "Department, Cost Centre and Quantity when known.",
    )
    estate_filename = fields.Char(string="Upload File Name", copy=False)
    estate_breakdown = fields.Text(
        string="Breakdown by Site / Department / Cost Centre", compute="_compute_estate_breakdown"
    )
    # ---- FR-QTE-013: the comparison with the version this one replaced -------
    version_diff = fields.Text(
        string="What Changed from the Previous Version", compute="_compute_version_diff"
    )
    # ---- T-05: the customer's approval link ----------------------------------
    access_token = fields.Char(copy=False, index=True, groups="base.group_system")
    approval_link_sent_at = fields.Datetime(readonly=True, copy=False)
    approval_link_channel = fields.Selection(
        CHANNELS, string="Approval Link Sent By", compute="_compute_link_inputs"
    )
    approval_link_recipient = fields.Char(string="Send To", compute="_compute_link_inputs")
    # ---- AUT-QTE-04/05 ----------------------------------------------------------
    unviewed_followup_at = fields.Datetime(readonly=True, copy=False)
    reminders_sent = fields.Char(readonly=True, copy=False, help="The T-n reminders already sent.")

    def _compute_link_inputs(self):
        for rec in self:
            rec.approval_link_channel = False
            rec.approval_link_recipient = False

    # ---- breakdown ---------------------------------------------------------------
    @api.depends(
        "line_ids.subtotal", "line_ids.site_name", "line_ids.department", "line_ids.cost_centre"
    )
    def _compute_estate_breakdown(self):
        for rec in self:
            priced = rec.line_ids.filtered(lambda ln: not ln.display_type)
            if not any(
                priced.mapped("site_name")
                + priced.mapped("department")
                + priced.mapped("cost_centre")
            ):
                rec.estate_breakdown = False
                continue
            out = []
            for label, fname in (
                ("Site", "site_name"),
                ("Department", "department"),
                ("Cost centre", "cost_centre"),
            ):
                totals = {}
                for ln in priced:
                    key = ln[fname] or _("(not given)")
                    count, amount = totals.get(key, (0, 0.0))
                    totals[key] = (count + 1, amount + (ln.subtotal or 0.0))
                out.append("%s:" % label)
                out += [
                    "  %s - %d asset(s), BDT %.2f" % (k, n, amt)
                    for k, (n, amt) in sorted(totals.items())
                ]
            rec.estate_breakdown = "\n".join(out)

    # ---- version comparison ---------------------------------------------------------
    @api.depends("parent_version_id", "line_ids", "value", "valid_until", "discount_amount")
    def _compute_version_diff(self):
        for rec in self:
            rec.version_diff = rec._diff_with_parent()

    def _diff_with_parent(self):
        self.ensure_one()
        old = self.parent_version_id.sudo()
        if not old:
            return False
        new = self.sudo()
        out = []
        if abs((old.value or 0.0) - (new.value or 0.0)) > 0.005:
            out.append(
                "Price before VAT: BDT %.2f in v%d, BDT %.2f now (%+.2f)."
                % (
                    old.value or 0.0,
                    old.version,
                    new.value or 0.0,
                    (new.value or 0.0) - (old.value or 0.0),
                )
            )
        if abs((old.discount_amount or 0.0) - (new.discount_amount or 0.0)) > 0.005:
            out.append(
                "Overall discount: BDT %.2f before, BDT %.2f now."
                % (old.discount_amount or 0.0, new.discount_amount or 0.0)
            )
        if old.valid_until != new.valid_until:
            out.append(
                "Valid until: %s before, %s now." % (old.valid_until or "-", new.valid_until or "-")
            )

        def lines(q):
            return {
                (ln.description or "").strip(): ln
                for ln in q.line_ids.filtered(lambda r: not r.display_type)
            }

        before, after = lines(old), lines(new)
        for name in sorted(set(after) - set(before)):
            ln = after[name]
            out.append("Added: %s (%g x BDT %.2f)." % (name, ln.quantity, ln.unit_price))
        for name in sorted(set(before) - set(after)):
            out.append("Removed: %s." % name)
        for name in sorted(set(before) & set(after)):
            a, b = before[name], after[name]
            if abs((a.quantity or 0) - (b.quantity or 0)) > 0.0001:
                out.append("%s: quantity %g before, %g now." % (name, a.quantity, b.quantity))
            if abs((a.unit_price or 0) - (b.unit_price or 0)) > 0.005:
                out.append(
                    "%s: unit price BDT %.2f before, BDT %.2f now."
                    % (name, a.unit_price, b.unit_price)
                )
        if "term_ids" in new._fields:
            t_old = {(t.text_en or "").strip() for t in old.term_ids}
            t_new = {(t.text_en or "").strip() for t in new.term_ids}
            out += ["New term: %s" % t for t in sorted(t_new - t_old)]
            out += ["Term dropped: %s" % t for t in sorted(t_old - t_new)]
        return "\n".join(out) or _("No change in price, lines, validity or terms.")

    def action_record_version_comparison(self):
        """Keep the comparison shown to the customer on the quotation's record."""
        for rec in self:
            if not rec.parent_version_id:
                raise UserError(
                    _("Version %d of %s has no previous version.") % (rec.version, rec.name)
                )
            rec.sudo().message_post(
                author_id=self.env.user.partner_id.id,
                body=_("Compared with v%(v)d:\n%(d)s")
                % {"v": rec.parent_version_id.version, "d": rec._diff_with_parent()},
            )
        return {"warning": False}

    # ---- estate upload ------------------------------------------------------------------
    def _estate_lines(self, raw, filename):
        rows, errors = parse_estate(read_rows(raw, filename or ""))
        if errors:
            raise UserError(_("The asset upload cannot be read: %s") % " ".join(errors[:8]))
        commands, current = [], None
        for row in sorted(rows, key=lambda r: (r["site_name"], r["department"], r["asset_ref"])):
            if row["site_name"] != current:
                current = row["site_name"]
                commands.append(
                    (
                        0,
                        0,
                        {
                            "display_type": "line_section",
                            "description": current or _("Site not given"),
                        },
                    )
                )
            label = row["description"]
            if row["asset_ref"]:
                label = "%s [%s]" % (label, row["asset_ref"])
            commands.append(
                (
                    0,
                    0,
                    {
                        "line_type": "service",
                        "description": label,
                        "quantity": row["quantity"],
                        "unit_price": row["unit_price"],
                        "asset_ref": row["asset_ref"] or False,
                        "site_name": row["site_name"] or False,
                        "department": row["department"] or False,
                        "cost_centre": row["cost_centre"] or False,
                    },
                )
            )
        return commands

    @api.model_create_multi
    def create(self, vals_list):
        import base64

        for vals in vals_list:
            if vals.get("estate_file") and not vals.get("line_ids"):
                raw = vals["estate_file"]
                raw = base64.b64decode(raw) if isinstance(raw, str | bytes) else raw
                vals["line_ids"] = self._estate_lines(raw, vals.get("estate_filename") or "")
        return super().create(vals_list)

    def action_import_estate(self):
        """Replace a draft's lines with the uploaded asset list."""
        for rec in self:
            if rec.state != "draft" or rec.approval_state == "pending":
                raise UserError(_("Only a draft not awaiting approval takes a new asset list."))
            att = (
                self.env["ir.attachment"]
                .sudo()
                .search(
                    [
                        ("res_model", "=", rec._name),
                        ("res_id", "=", rec.id),
                        ("res_field", "=", "estate_file"),
                    ],
                    limit=1,
                )
            )
            if not att or not att.raw:
                raise UserError(_("Upload the asset list on the quotation first."))
            commands = rec._estate_lines(att.raw, rec.estate_filename)
            rec.line_ids.unlink()
            rec.write({"line_ids": commands})
        return True

    # ---- customer approval link (FR-QTE-034, T-05) -----------------------------------------
    def _approval_url(self):
        self.ensure_one()
        base = self.env["ir.config_parameter"].sudo().get_param("web.base.url") or ""
        return base.rstrip("/") + APPROVAL_PATH % self.sudo().access_token

    def action_send_approval_link(self, channel=None, recipient=None):
        """Issue the customer's one-screen approval link on a channel: a
        fresh token (an earlier link stops working), recorded as a delivery."""
        if channel not in dict(CHANNELS) or channel in ("counter", "phone"):
            raise UserError(
                _(
                    "Choose a channel a link can travel on (portal, app, WhatsApp, SMS, email, on-site)."
                )
            )
        today = dhaka_today(self)
        Delivery = self.env["fix.quotation.delivery"]
        out = {}
        for rec in self:
            if rec.state != "sent":
                raise UserError(_("Issue the quotation to the customer first."))
            if not rec.valid_until or rec.valid_until < today:
                raise UserError(_("Quotation %s is past its validity: revise it.") % rec.name)
            rec.sudo().write(
                {
                    "access_token": secrets.token_urlsafe(24),
                    "approval_link_sent_at": fields.Datetime.now(),
                }
            )
            url = rec._approval_url()
            Delivery.create(
                {
                    "quotation_id": rec.id,
                    "channel": channel,
                    "recipient": (recipient or "").strip() or False,
                    "delivery_ref": url,
                    "note": _("Customer approval link"),
                }
            )
            out = {"link": url}
        return out

    @api.model
    def _from_token(self, token):
        """The quotation a link names, or an empty set. Constant-time compare."""
        if not token or not re.fullmatch(r"[A-Za-z0-9_-]{20,64}", token):
            return self.browse()
        quote = self.sudo().search([("access_token", "=", token)], limit=1)
        if quote and secrets.compare_digest(quote.access_token or "", token):
            return quote
        return self.browse()

    def _record_view(self):
        """FR-QTE-039: the customer opened the link."""
        self.ensure_one()
        delivery = self.sudo().delivery_ids.filtered(
            lambda d: d.delivery_ref and d.delivery_ref.endswith(self.sudo().access_token or "#")
        )[:1]
        if delivery:
            now = fields.Datetime.now()
            delivery.write(
                {
                    "first_viewed_at": delivery.first_viewed_at or now,
                    "view_count": (delivery.view_count or 0) + 1,
                }
            )

    def _customer_view(self):
        """What the customer may see (BRU-QTE-13: never cost or margin)."""
        self.ensure_one()
        q = self.sudo()
        return {
            "company": q.company_id.name,
            "name": q.name,
            "version": q.version,
            "customer": q.customer_id.name,
            "state": q.state,
            "valid_until": q.valid_until,
            "currency": q.currency_id.name,
            "lines": [
                {
                    "section": bool(ln.display_type),
                    "description": ln.description,
                    "quantity": ln.quantity,
                    "unit_price": ln.unit_price,
                    "subtotal": ln.subtotal,
                }
                for ln in q.line_ids.sorted(lambda r: (r.sequence, r.id))
                if not getattr(ln, "is_optional", False)
            ],
            "value": q.value,
            "vat": q.vat_amount,
            "total": q.amount_total,
            "terms": [(t.text_en, t.text_bn) for t in q.term_ids]
            if "term_ids" in q._fields
            else [],
        }

    # ---- automations (AUT-QTE-04/05/10) --------------------------------------------------
    @api.model
    def cron_quotation_followups(self):
        """Daily, idempotent: expiry reminders at T-2 and T-1 days on the first
        channel the customer received the quotation on (stopped by any
        decision: only quotations still with the customer), and a follow-up
        task for the author when an issued quotation is unviewed for 24 h."""
        today = dhaka_today(self)
        now = fields.Datetime.now()
        todo = self.env.ref("mail.mail_activity_data_todo", raise_if_not_found=False)
        sent = self.sudo().search([("state", "=", "sent")])
        reminded = 0
        for q in sent:
            if q.valid_until:
                days = (q.valid_until - today).days
                done = set(filter(None, (q.reminders_sent or "").split(",")))
                if days in REMINDER_DAYS and str(days) not in done:
                    first = q.delivery_ids.sorted(lambda d: (d.sent_at, d.id))[:1]
                    self.env["fix.quotation.delivery"].sudo().create(
                        {
                            "quotation_id": q.id,
                            "channel": first.channel or "sms",
                            "recipient": first.recipient or False,
                            "note": _("Expiry reminder: valid %d more day(s)") % days,
                        }
                    )
                    q._guarded().write({"reminders_sent": ",".join(sorted(done | {str(days)}))})
                    publish(
                        self.env,
                        "quotation.reminder_due",
                        "fix.quotation",
                        q.id,
                        {
                            "quotation": q.name,
                            "version": q.version,
                            "days_left": days,
                            "channel": first.channel or "sms",
                        },
                    )
                    reminded += 1
            viewed = any(q.delivery_ids.mapped("first_viewed_at"))
            if (
                not viewed
                and not q.unviewed_followup_at
                and q.sent_at
                and q.sent_at <= now - timedelta(hours=UNVIEWED_HOURS)
            ):
                q.activity_schedule(
                    activity_type_id=todo.id if todo else False,
                    summary=_("Quotation not viewed in 24 hours: follow up"),
                    note=_("Re-send %s on another channel or call the customer (AUT-QTE-04).")
                    % q.name,
                    user_id=q.create_uid.id,
                )
                q._guarded().write({"unviewed_followup_at": now})
        return reminded

    @api.model
    def cron_renewal_quotations(self):
        """AUT-QTE-10 / BRU-QTE-18: a contract in force, inside its renewal
        lead time, with no renewal quotation and no renewal term yet, gets a
        draft renewal quotation in its owner's name, and the owner a task."""
        if "fix.contract" not in self.env:
            return 0
        today = dhaka_today(self)
        todo = self.env.ref("mail.mail_activity_data_todo", raise_if_not_found=False)
        made = 0
        contracts = (
            self.env["fix.contract"]
            .sudo()
            .search(
                [
                    ("state", "in", ("active", "expiring")),
                    ("family", "in", ("amc", "ramc", "managed")),
                ]
            )
        )
        for contract in contracts:
            lead = contract.renewal_lead_days or 90
            if contract.date_end - timedelta(days=lead) > today:
                continue
            if self.sudo().search_count(
                [("renewal_of_contract_id", "=", contract.id), ("state", "!=", "cancelled")]
            ):
                continue
            if contract.renewal_ids.filtered(lambda r: r.state not in ("terminated", "expired")):
                continue
            owner = (
                contract.create_uid
                if contract.create_uid and contract.create_uid.active
                else self.env.user
            )
            months = max(1, round((contract.date_end - contract.date_start).days / 30.44))
            quote = (
                self.with_user(owner)
                .sudo()
                .create(
                    {
                        "renewal_of_contract_id": contract.id,
                        "contract_months": months,
                        "valid_until": max(contract.date_end, today + timedelta(days=7)),
                    }
                )
            )
            quote.activity_schedule(
                activity_type_id=todo.id if todo else False,
                summary=_("Renewal quotation drafted: cost it and submit it"),
                note=_("Contract %(c)s ends %(d)s (BRU-QTE-18).")
                % {"c": contract.code, "d": contract.date_end},
                user_id=owner.id,
            )
            made += 1
        return made
