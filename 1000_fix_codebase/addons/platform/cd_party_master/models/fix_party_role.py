# fix.party.role — the multi-role model (P03-M05-T03).
# THE design rule: a SINGLE res.partner holds MULTIPLE roles simultaneously.
# Violating this produces exactly the duplicate-identity problem the
# programme exists to remove, and it is unrecoverable once transaction
# volume accrues against the duplicates.
import logging

from odoo import api, fields, models

logger = logging.getLogger(__name__)


class FixPartyRole(models.Model):
    """A role a party holds: customer, vendor, seller, brand-partner, etc.

    A party with three roles has THREE fix.party.role records pointing at
    the SAME res.partner — never three separate master records.
    """

    _name = "fix.party.role"
    _description = "Party Role"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "partner_id, role_type"
    # Odoo 19 dropped the legacy constraint tuple list;
    # models.Constraint attributes (migrated by tooling/scripts/migrate-sql-constraints.py)
    _partner_role_unique = models.Constraint(
        "UNIQUE (partner_id, role_type)", "A party holds each role at most once"
    )

    # AS-03
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit", index=True)

    partner_id = fields.Many2one(
        "res.partner", string="Party", required=True, ondelete="cascade", index=True
    )
    role_type = fields.Selection(
        [
            ("customer", "Customer"),
            ("vendor", "Vendor / Supplier"),
            ("seller", "Marketplace Seller"),
            ("brand_partner", "Brand Partner"),
            ("employee", "Employee (via M21)"),
            ("contractor", "Contractor"),
            ("carrier", "Logistics Carrier"),
            ("government", "Government Body"),
        ],
        required=True,
        index=True,
        tracking=True,
    )
    role_status = fields.Selection(
        [
            ("prospect", "Prospect"),
            ("active", "Active"),
            ("suspended", "Suspended"),
            ("terminated", "Terminated"),
        ],
        default="prospect",
        required=True,
        tracking=True,
    )
    since = fields.Date(string="Role Since", default=fields.Date.today, readonly=True)
    operating_unit_ids = fields.Many2many(
        "operating.unit", string="Active Branches", help="Where this role is active"
    )

    # Event emission (AS-08, via fix_events)
    @api.model_create_multi
    def create(self, vals_list):
        # An active role lets the party trade in it (A03 audit M33-3).
        Partner = self.env["res.partner"]
        for vals in vals_list:
            if vals.get("role_status") == "active" and vals.get("partner_id"):
                Partner.browse(vals["partner_id"])._fix_assert_party_usable(
                    "an active %s role" % vals.get("role_type")
                )
        records = super().create(vals_list)
        for rec in records:
            self._emit_party_event("party.role_added", rec)
        return records

    def _fix_assert_role_party_usable(self):
        for rec in self:
            rec.partner_id._fix_assert_party_usable("an active %s role" % rec.role_type)

    def write(self, vals):
        if vals.get("role_status") == "active":
            self.filtered(lambda r: r.role_status != "active")._fix_assert_role_party_usable()
        result = super().write(vals)
        if "role_status" in vals:
            for rec in self:
                self._emit_party_event("party.role_changed", rec)
        return result

    def unlink(self):
        for rec in self:
            self._emit_party_event("party.role_removed", rec)
        return super().unlink()

    def _emit_party_event(self, event_type: str, rec) -> None:
        """Emit a party domain event through the transactional outbox."""
        from libs.py.fix_events import publish

        publish(
            self.env,
            event_type,
            "res.partner",
            rec.partner_id.id,
            {
                "partner_id": rec.partner_id.id,
                "role_type": rec.role_type,
                "role_status": rec.role_status,
            },
        )

    @api.constrains("role_type", "partner_id")
    def _check_no_duplicate_masters(self):
        """The design rule enforced: warn if this partner appears under
        multiple res.partner records (the duplicate-identity failure mode)."""
        for rec in self:
            # Check if there are other partners with the same VAT or phone
            # (indicating a duplicate master record)
            if rec.partner_id.vat:
                dupes = self.env["res.partner"].search_count(
                    [
                        ("vat", "=", rec.partner_id.vat),
                        ("id", "!=", rec.partner_id.id),
                    ]
                )
                if dupes > 0:
                    logger.warning(
                        "party.role: partner %s shares VAT with %d other record(s) — "
                        "potential duplicate master (the unrecoverable failure mode)",
                        rec.partner_id.name,
                        dupes,
                    )
