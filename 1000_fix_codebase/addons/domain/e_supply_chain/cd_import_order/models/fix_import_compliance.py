# fix_import_compliance — M44 trade-compliance masters (A06 remediation):
#   BRU-ITC-10  restricted / prohibited goods register and import permits;
#   BRU-ITC-12  C&F agent master (licensed, approved, active in M42);
#   BRU-ITC-13  cargo insurance cover on the import order.
#
# Which goods are restricted, which permits they need and which agents are
# licensed are DATA the user enters from the Import Policy Order, the
# agencies' notices and the agents' licences; this module asserts none of it.
# Every master row and every permit or cover is entered by an Import Officer
# and made effective by an Import Approver who did not enter it.
import re

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish

from .fix_import_common import (
    APPROVER,
    P,
    param_float,
    refuse_locked,
    require_group,
    require_other_person,
    today,
)

PARAM_INSURANCE_COVER = P + "insurance_cover_pct"  # default 100 (spec BRU-ITC-13)
# Incoterms under which transit risk (and so the insurance) is the importer's.
IMPORTER_RISK_INCOTERMS = ("fob", "exw", "cfr")
PATTERN_RE = re.compile(r"^\d{2}(\.?\d{2}){0,4}$")


def _digits(code):
    return re.sub(r"\D", "", code or "")


# =============================================================== restriction register
class FixImportRestriction(models.Model):
    """BRU-ITC-10: a prohibited or restricted classification (an HS heading
    prefix or a product), in force between its dates."""

    _name = "fix.import.restriction"
    _description = "Import Restriction"
    _order = "hs_code_pattern, date_from desc"
    _inherit = ["fix.guarded.mixin", "mail.thread"]

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    hs_code_pattern = fields.Char(
        string="HS Code / Prefix",
        help="Any HS code starting with these digits is caught (e.g. 8525 or 8525.80).",
    )
    product_id = fields.Many2one("product.product", string="Product", ondelete="restrict")
    restriction_type = fields.Selection(
        [("prohibited", "Prohibited"), ("restricted", "Restricted (permit required)")],
        required=True,
        default="restricted",
    )
    permit_type = fields.Char(string="Permit Required", help="e.g. BTRC NOC, DoE clearance")
    issuing_authority = fields.Char()
    legal_ref = fields.Char(string="Legal Reference", help="Import Policy Order schedule, SRO")
    date_from = fields.Date(string="Effective From", required=True)
    date_to = fields.Date(string="Effective To")
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("retired", "Retired")],
        required=True,
        default="draft",
        tracking=True,
    )
    activated_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    activated_on = fields.Datetime(readonly=True, copy=False)

    _FROZEN = (
        "company_id",
        "hs_code_pattern",
        "product_id",
        "restriction_type",
        "permit_type",
        "issuing_authority",
        "legal_ref",
        "date_from",
        "date_to",
    )
    _dates_ordered = models.Constraint(
        "CHECK (date_to IS NULL OR date_to >= date_from)",
        "A restriction cannot end before it starts",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "activated_by_id", "activated_on"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.state != "draft":
            locked |= set(self._FROZEN)
        return locked

    @api.constrains("hs_code_pattern", "product_id", "restriction_type", "permit_type")
    def _check_target(self):
        for rec in self:
            if not rec.hs_code_pattern and not rec.product_id:
                raise ValidationError("A restriction names an HS code prefix or a product.")
            if rec.hs_code_pattern and not PATTERN_RE.match(rec.hs_code_pattern.strip()):
                raise ValidationError(
                    "%r is not an HS code prefix (2 to 10 digits, e.g. 8525 or 8525.80)."
                    % rec.hs_code_pattern
                )
            if rec.restriction_type == "restricted" and not (rec.permit_type or "").strip():
                raise ValidationError("A restricted item names the permit it requires.")

    def write(self, vals):
        refuse_locked(
            self,
            vals,
            lambda r: set(r._FROZEN) if r.state != "draft" else set(),
            "an active restriction is frozen; record a new row and retire this one.",
        )
        return super().write(vals)

    def action_activate(self):
        require_group(self.env, APPROVER, "Activating an import restriction")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Activate a draft restriction.")
            require_other_person(rec.env, rec, "Import restriction %s" % rec.name)
            rec._guarded().write(
                {
                    "state": "active",
                    "activated_by_id": rec.env.user.id,
                    "activated_on": fields.Datetime.now(),
                }
            )
        return True

    def action_retire(self):
        require_group(self.env, APPROVER, "Retiring an import restriction")
        for rec in self:
            if rec.state != "active":
                raise UserError("Retire an active restriction.")
            end = max(today(rec), rec.date_from)
            rec._guarded().write({"state": "retired", "date_to": rec.date_to or end})
        return True

    @api.model
    def _restrictions_for(self, line, on_date):
        """Active restrictions in force on `on_date` that catch an import line."""
        company = line.order_id.company_id
        rows = self.sudo().search(
            [
                ("company_id", "=", company.id),
                ("state", "in", ("active", "retired")),
                ("date_from", "<=", on_date),
                "|",
                ("date_to", "=", False),
                ("date_to", ">=", on_date),
            ]
        )
        digits = _digits(line.hs_id.hs_code)
        products = line.hs_id.product_id
        if "product_id" in line.part_id._fields:
            products |= line.part_id.product_id
        return rows.filtered(
            lambda r: (
                (r.hs_code_pattern and digits and digits.startswith(_digits(r.hs_code_pattern)))
                or (r.product_id and r.product_id in products)
            )
        )


class FixImportPermit(models.Model):
    """The permit a restricted line needs, attached to the consignment:
    number, issuer, validity and the document, verified by an Import
    Approver who did not record it."""

    _name = "fix.import.permit"
    _description = "Import Permit"
    _order = "valid_to desc, id desc"
    _inherit = ["fix.guarded.mixin", "mail.thread"]

    order_id = fields.Many2one(
        "fix.import.order", string="Import Order", required=True, ondelete="cascade", index=True
    )
    company_id = fields.Many2one(related="order_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(
        related="order_id.operating_unit_id", store=True, index=True
    )
    restriction_id = fields.Many2one(
        "fix.import.restriction",
        string="Restriction",
        required=True,
        ondelete="restrict",
        domain=[("restriction_type", "=", "restricted")],
    )
    permit_type = fields.Char(related="restriction_id.permit_type")
    permit_no = fields.Char(string="Permit No", required=True)
    issuer = fields.Char(string="Issued By", required=True)
    issued_on = fields.Date()
    valid_to = fields.Date(string="Valid To", required=True)
    document = fields.Binary(string="Permit Document", attachment=True)
    document_name = fields.Char()
    state = fields.Selection(
        [("draft", "Draft"), ("verified", "Verified"), ("revoked", "Revoked")],
        required=True,
        default="draft",
        tracking=True,
    )
    verified_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    verified_on = fields.Datetime(readonly=True, copy=False)

    _FROZEN = (
        "order_id",
        "restriction_id",
        "permit_no",
        "issuer",
        "issued_on",
        "valid_to",
        "document",
        "document_name",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "verified_by_id", "verified_on"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.state != "draft":
            locked |= set(self._FROZEN)
        return locked

    def write(self, vals):
        refuse_locked(
            self,
            vals,
            lambda r: set(r._FROZEN) if r.state != "draft" else set(),
            "a verified permit is evidence; record a new one.",
        )
        return super().write(vals)

    def _permit_valid(self, on_date):
        self.ensure_one()
        return bool(self.state == "verified" and self.valid_to and self.valid_to >= on_date)

    def action_verify(self):
        require_group(self.env, APPROVER, "Verifying an import permit")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Verify a draft permit.")
            require_other_person(rec.env, rec, "Permit %s" % rec.permit_no)
            if not rec.document:
                raise UserError("Attach the permit document before it is verified.")
            if rec.valid_to < today(rec):
                raise UserError("Permit %s expired on %s." % (rec.permit_no, rec.valid_to))
            if rec.restriction_id.restriction_type != "restricted":
                raise UserError("A prohibited item cannot be imported under a permit.")
            rec._guarded().write(
                {
                    "state": "verified",
                    "verified_by_id": rec.env.user.id,
                    "verified_on": fields.Datetime.now(),
                }
            )
        return True

    def action_revoke(self):
        require_group(self.env, APPROVER, "Revoking an import permit")
        for rec in self:
            if rec.state != "verified":
                raise UserError("Revoke a verified permit.")
            rec._guarded().write({"state": "revoked"})
        return True


# =============================================================== C&F agent master
class FixImportCnfAgent(models.Model):
    """BRU-ITC-12: a clearing-and-forwarding agent is instructed only when it
    is licensed (licence unexpired), approved here by an Import Approver who
    did not enter it, and active as a supplier in M42."""

    _name = "fix.import.cnf.agent"
    _description = "C&F Agent"
    _order = "name"
    _inherit = ["fix.guarded.mixin", "mail.thread"]

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    supplier_id = fields.Many2one(
        "fix.supplier",
        string="M42 Supplier Record",
        required=True,
        ondelete="restrict",
        help="The agent's qualified supplier record; it must be active in M42.",
    )
    licence_no = fields.Char(string="C&F Licence No", required=True)
    licence_authority = fields.Char(string="Licensing Custom House", default="Chattogram")
    licence_expiry = fields.Date(string="Licence Expiry", required=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("approved", "Approved"),
            ("blocked", "Blocked"),
            ("expired", "Licence Expired"),
        ],
        required=True,
        default="draft",
        tracking=True,
    )
    approved_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    approved_on = fields.Datetime(readonly=True, copy=False)
    blocked_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    block_reason = fields.Char(readonly=True, copy=False)
    is_usable = fields.Boolean(string="Can Be Instructed", compute="_compute_usable")

    _FROZEN = ("company_id", "supplier_id", "licence_no", "licence_authority", "licence_expiry")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "approved_by_id",
            "approved_on",
            "blocked_by_id",
            "block_reason",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.state != "draft":
            locked |= set(self._FROZEN)
        return locked

    @api.constrains("licence_no", "company_id")
    def _check_unique_licence(self):
        for rec in self:
            if self.sudo().search_count(
                [
                    ("id", "!=", rec.id),
                    ("licence_no", "=", rec.licence_no),
                    ("company_id", "=", rec.company_id.id),
                ]
            ):
                raise ValidationError("C&F licence %s is already recorded." % rec.licence_no)

    def write(self, vals):
        refuse_locked(
            self,
            vals,
            lambda r: set(r._FROZEN) if r.state != "draft" else set(),
            "an approved agent's licence is evidence; a renewal is recorded as a new agent "
            "record and approved again.",
        )
        return super().write(vals)

    @api.depends("state", "licence_expiry", "supplier_id.status")
    def _compute_usable(self):
        day = today(self)
        for rec in self:
            rec.is_usable = bool(
                rec.state == "approved"
                and rec.licence_expiry
                and rec.licence_expiry >= day
                and rec.supplier_id.sudo().status == "active"
            )

    def _cnf_require_usable(self, what):
        if not self:
            raise UserError("%s: name the C&F agent (BRU-ITC-12)." % what)
        rec = self.sudo()
        if rec.state != "approved":
            raise UserError("%s: C&F agent %s is %s, not approved." % (what, rec.name, rec.state))
        if not rec.licence_expiry or rec.licence_expiry < today(rec):
            raise UserError(
                "%s: the licence of C&F agent %s expired on %s."
                % (what, rec.name, rec.licence_expiry)
            )
        if rec.supplier_id.status != "active":
            raise UserError(
                "%s: C&F agent %s is not active in M42 (supplier %s is %s)."
                % (what, rec.name, rec.supplier_id.name, rec.supplier_id.status)
            )

    def action_approve(self):
        require_group(self.env, APPROVER, "Approving a C&F agent")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Approve a draft agent.")
            require_other_person(rec.env, rec, "C&F agent %s" % rec.name)
            if rec.licence_expiry < today(rec):
                raise UserError("The licence of %s has expired." % rec.name)
            if rec.supplier_id.sudo().status != "active":
                raise UserError(
                    "%s must be qualified and active in M42 before it is approved (BRU-ITC-12)."
                    % rec.name
                )
            rec._guarded().write(
                {
                    "state": "approved",
                    "approved_by_id": rec.env.user.id,
                    "approved_on": fields.Datetime.now(),
                }
            )
        return True

    def action_block(self, reason=None):
        require_group(self.env, APPROVER, "Blocking a C&F agent")
        for rec in self:
            if rec.state != "approved":
                raise UserError("Block an approved agent.")
            if not (reason or "").strip():
                raise UserError("State why the agent is blocked.")
            rec._guarded().write(
                {
                    "state": "blocked",
                    "blocked_by_id": rec.env.user.id,
                    "block_reason": reason.strip(),
                }
            )
        return True

    def action_unblock(self):
        require_group(self.env, APPROVER, "Unblocking a C&F agent")
        for rec in self:
            if rec.state != "blocked":
                raise UserError("Unblock a blocked agent.")
            require_other_person(rec.env, rec, "Unblocking %s" % rec.name, rec.blocked_by_id)
            if rec.licence_expiry < today(rec):
                raise UserError("The licence of %s has expired." % rec.name)
            rec._guarded().write(
                {"state": "approved", "blocked_by_id": False, "block_reason": False}
            )
        return True

    @api.model
    def _cron_expire(self):
        """A licence past its expiry date expires (daily)."""
        lapsed = self.sudo().search(
            [("state", "=", "approved"), ("licence_expiry", "<", today(self))]
        )
        for rec in lapsed:
            rec._guarded().write({"state": "expired"})
            rec.message_post(
                body="C&F licence %s expired on %s." % (rec.licence_no, rec.licence_expiry)
            )
            publish(self.env, "import.cnf_licence_expired", self._name, rec.id, {"agent": rec.name})
        return len(lapsed)


# =============================================================== cargo insurance
class FixImportInsurance(models.Model):
    """BRU-ITC-13: the cargo insurance cover of an import order. Where the
    incoterm puts the transit risk on the importer, shipment is refused
    without valid cover of at least the consignment value (configurable
    share). The premium of the verified cover is the insurance in the CIF
    the duty cascade assesses."""

    _name = "fix.import.insurance"
    _description = "Cargo Insurance Cover"
    _order = "cover_to desc, id desc"
    _inherit = ["fix.guarded.mixin", "mail.thread"]

    order_id = fields.Many2one(
        "fix.import.order", string="Import Order", required=True, ondelete="cascade", index=True
    )
    company_id = fields.Many2one(related="order_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(
        related="order_id.operating_unit_id", store=True, index=True
    )
    insurer_id = fields.Many2one(
        "res.partner", string="Insurer", required=True, ondelete="restrict"
    )
    policy_no = fields.Char(string="Policy / Cover Note No", required=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    sum_insured = fields.Monetary(currency_field="currency_id", required=True)
    premium = fields.Monetary(currency_field="currency_id")
    cover_from = fields.Date(required=True)
    cover_to = fields.Date(required=True)
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("cancelled", "Cancelled")],
        required=True,
        default="draft",
        tracking=True,
    )
    verified_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    verified_on = fields.Datetime(readonly=True, copy=False)

    _FROZEN = (
        "order_id",
        "insurer_id",
        "policy_no",
        "currency_id",
        "sum_insured",
        "premium",
        "cover_from",
        "cover_to",
    )
    _dates_ordered = models.Constraint(
        "CHECK (cover_to >= cover_from)", "Insurance cover cannot end before it starts"
    )
    _amounts = models.Constraint(
        "CHECK (sum_insured > 0 AND premium >= 0)", "The sum insured must be positive"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "verified_by_id", "verified_on"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.state != "draft":
            locked |= set(self._FROZEN)
        return locked

    def write(self, vals):
        refuse_locked(
            self,
            vals,
            lambda r: set(r._FROZEN) if r.state != "draft" else set(),
            "verified cover is evidence; record an endorsement as a new cover.",
        )
        return super().write(vals)

    def action_verify(self):
        require_group(self.env, APPROVER, "Verifying cargo insurance")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Verify a draft cover.")
            require_other_person(rec.env, rec, "Cover %s" % rec.policy_no)
            if rec.cover_to < today(rec):
                raise UserError("Cover %s ended on %s." % (rec.policy_no, rec.cover_to))
            rec.order_id._to_order_ccy(rec.sum_insured, rec.currency_id)  # currency check
            if rec.order_id._import_cif_locked():
                raise UserError(
                    "A Bill of Entry of %s is already assessed on the recorded insurance; "
                    "verify the cover before assessment." % rec.order_id.name
                )
            rec._guarded().write(
                {
                    "state": "active",
                    "verified_by_id": rec.env.user.id,
                    "verified_on": fields.Datetime.now(),
                }
            )
        return True

    def action_cancel(self):
        require_group(self.env, APPROVER, "Cancelling cargo insurance")
        for rec in self:
            if rec.state == "cancelled":
                raise UserError("The cover is already cancelled.")
            if rec.state == "active" and rec.order_id._import_cif_locked():
                raise UserError(
                    "The cover is in an assessed Bill of Entry's CIF; it cannot be cancelled."
                )
            rec._guarded().write({"state": "cancelled"})
        return True


# =============================================================== order hooks
class FixImportOrderCompliance(models.Model):
    _inherit = "fix.import.order"

    permit_ids = fields.One2many("fix.import.permit", "order_id", string="Permits")
    insurance_ids = fields.One2many("fix.import.insurance", "order_id", string="Insurance Cover")

    def _import_active_covers(self):
        self.ensure_one()
        return self.insurance_ids.filtered(lambda i: i.state == "active")

    def _import_insurance_for_cif(self):
        """The insurance in the CIF: the verified covers' premium when the
        importer insures, else the recorded insurance cost."""
        self.ensure_one()
        covers = self._import_active_covers()
        if not covers:
            return self.insurance_cost or 0.0
        return sum(self._to_order_ccy(c.premium or 0.0, c.currency_id) for c in covers)

    def _import_check_eligibility(self, what):
        """BRU-ITC-10 / FR-ITC-009: every line is classified; a prohibited
        line is refused outright; a restricted line needs a verified,
        unexpired permit for its restriction on this order."""
        Restriction = self.env["fix.import.restriction"]
        for rec in self:
            day = today(rec)
            for line in rec.line_ids:
                if not line.hs_id:
                    raise UserError(
                        "%s: classify every line of %s first (%s has no HS)."
                        % (what, rec.name, line.part_id.display_name)
                    )
                line.sudo()._import_check_hs_of_part(what)
                for restriction in Restriction._restrictions_for(line, day):
                    if restriction.restriction_type == "prohibited":
                        raise UserError(
                            "%s: %s (HS %s) is a prohibited import (%s)."
                            % (
                                what,
                                line.part_id.display_name,
                                line.hs_id.hs_code,
                                restriction.name,
                            )
                        )
                    permits = rec.sudo().permit_ids.filtered(
                        lambda p, r=restriction, d=day: p.restriction_id == r and p._permit_valid(d)
                    )
                    if not permits:
                        raise UserError(
                            "%s: %s (HS %s) is restricted (%s): attach a verified, valid %s "
                            "permit to the order."
                            % (
                                what,
                                line.part_id.display_name,
                                line.hs_id.hs_code,
                                restriction.name,
                                restriction.permit_type,
                            )
                        )

    def _import_check_insurance(self, what):
        """BRU-ITC-13: where the incoterm puts the transit risk on the
        importer, valid cover >= the configured share of the consignment
        (CIF) value blocks nothing; a shortfall blocks shipment."""
        pct = param_float(self.env, PARAM_INSURANCE_COVER, 100.0)
        for rec in self:
            if rec.incoterm not in IMPORTER_RISK_INCOTERMS:
                continue
            day = today(rec)
            covers = rec._import_active_covers().filtered(
                lambda c, d=day: c.cover_from <= d <= c.cover_to
            )
            insured = sum(rec._to_order_ccy(c.sum_insured, c.currency_id) for c in covers)
            value = sum(rec.line_ids.mapped("cif_amount")) or rec._invoice_value()
            need = value * pct / 100.0
            if insured + 0.005 < need:
                raise UserError(
                    "%s: cargo cover of %.2f %s is below %.0f%% of the consignment value %.2f %s "
                    "(the %s incoterm puts the transit risk on the importer, BRU-ITC-13)."
                    % (
                        what,
                        insured,
                        rec.currency_id.name,
                        pct,
                        value,
                        rec.currency_id.name,
                        (rec.incoterm or "").upper(),
                    )
                )


class FixImportOrderLineCompliance(models.Model):
    _inherit = "fix.import.order.line"

    @api.constrains("hs_id", "part_id")
    def _check_not_prohibited(self):
        Restriction = self.env["fix.import.restriction"]
        for line in self:
            for r in Restriction._restrictions_for(line, today(line)):
                if r.restriction_type == "prohibited":
                    raise ValidationError(
                        "%s (HS %s) is a prohibited import (%s)."
                        % (line.part_id.display_name, line.hs_id.hs_code or "-", r.name)
                    )
