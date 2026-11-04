# fix_ewaste_compliance - M18 regulatory and money records (A05 audit P2/E10).
#
# M18-13/14: the module had no transfer manifest, no Basel prior-informed-
# consent record, no DoE registration and no money at all (buy-back, recycler
# fee, material-recovery income). These are records with a lifecycle, each
# decided by someone other than its creator:
#  - fix.ewaste.manifest: the Form-1 transfer note, issued by the batch
#    dispatch itself (never typed), with its hazmat declaration;
#  - fix.ewaste.basel.pic: prior informed consent for a cross-border transfer;
#  - fix.ewaste.registration: the company's DoE e-waste registration and EPR
#    target, under which DoE returns are filed;
#  - fix.ewaste.settlement: incentive / recycler fee / recovery income, routed
#    through M63 to the finance approver and handed to finance by event.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish

from . import ewaste_common as c

_LOG_COLUMNS = frozenset({"id", "create_uid", "create_date", "write_uid", "write_date"})
UN_NUMBERS = {"li_ion": "UN3480", "li_po": "UN3480", "nimh": "UN3496", "lead_acid": "UN2800"}


class FixApprovalMatrixEwaste(models.Model):
    _inherit = "fix.approval.matrix"

    # A05 audit E5/E11: the M18 approvals routed through M63
    decision_domain = fields.Selection(
        selection_add=[
            ("ewaste_recycler", "E-Waste Recycler Registration"),
            ("ewaste_settlement", "E-Waste Incentive / Recycler Fee / Recovery Income"),
        ],
        ondelete={"ewaste_recycler": "cascade", "ewaste_settlement": "cascade"},
    )


class FixEwasteManifest(models.Model):
    """S.R.O. 187/2021 Form-1 transfer manifest, issued at batch dispatch."""

    _name = "fix.ewaste.manifest"
    _description = "E-Waste Transfer Manifest (Form-1)"
    _inherit = ["fix.guarded.mixin"]
    _order = "issued_on desc, id desc"

    name = fields.Char(required=True, default="New", readonly=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    batch_id = fields.Many2one(
        "fix.ewaste.batch", required=True, ondelete="restrict", readonly=True
    )
    partner_id = fields.Many2one("fix.ewaste.partner", readonly=True, ondelete="restrict")
    licence_no = fields.Char(readonly=True)
    licence_valid_to = fields.Date(readonly=True)
    destination_country_id = fields.Many2one("res.country", readonly=True)
    basel_pic_id = fields.Many2one("fix.ewaste.basel.pic", readonly=True)
    line_ids = fields.One2many("fix.ewaste.manifest.line", "manifest_id", readonly=True)
    total_weight_kg = fields.Float(readonly=True)
    item_count = fields.Integer(readonly=True)
    hazardous = fields.Boolean(readonly=True)
    hazmat_declaration = fields.Text(readonly=True)
    issued_on = fields.Date(readonly=True)
    issued_by_id = fields.Many2one("res.users", readonly=True)

    def _fix_guarded_fields(self) -> set:
        return set(super()._fix_guarded_fields()) | set(self._fields) - {
            "id",
            "display_name",
            "create_uid",
            "create_date",
            "write_uid",
            "write_date",
        }

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_open():
            raise UserError("A transfer manifest is issued by the batch dispatch, never typed.")
        return super().create(vals_list)

    @api.model
    def _fix_issue_for(self, batch):
        """Snapshot the batch as it leaves (trusted service path)."""
        partner = batch.partner_id
        lines = [
            (
                0,
                0,
                {
                    "collection_id": item.id,
                    "description": item.name,
                    "material_type": item.material_type,
                    "weight_kg": item.weight_kg,
                    "wipe_certificate_id": item.wipe_certificate_id.id or False,
                },
            )
            for item in batch.collection_ids
        ] + [
            (
                0,
                0,
                {
                    "battery_id": bat.id,
                    "description": bat.name,
                    "material_type": "battery",
                    "weight_kg": bat.weight_kg,
                    "hazardous": True,
                    "un_number": UN_NUMBERS.get(bat.chemistry, "UN3480"),
                    "swollen_cell": bat.swollen_cell,
                },
            )
            for bat in batch.battery_ids
        ]
        hazardous = bool(batch.battery_ids)
        declaration = False
        if hazardous:
            declaration = (
                "Hazardous consignment: %d battery item(s), %.3f kg, %s. Terminals insulated "
                "and inspected; swollen cells packed in vermiculite."
                % (
                    len(batch.battery_ids),
                    sum(batch.battery_ids.mapped("weight_kg")),
                    ", ".join(
                        sorted({UN_NUMBERS.get(b.chemistry, "UN3480") for b in batch.battery_ids})
                    ),
                )
            )
        manifest = (
            self.sudo()
            ._guarded()
            .create(
                {
                    "name": self.env["ir.sequence"].sudo().next_by_code("fix.ewaste.manifest")
                    or "EMAN/New",
                    "company_id": batch.company_id.id,
                    "batch_id": batch.id,
                    "partner_id": partner.id,
                    "licence_no": partner.certificate_no,
                    "licence_valid_to": partner.valid_to,
                    "destination_country_id": batch.destination_country_id.id or False,
                    "basel_pic_id": batch.basel_pic_id.id or False,
                    "line_ids": lines,
                    "total_weight_kg": batch.weight_kg,
                    "item_count": len(lines),
                    "hazardous": hazardous,
                    "hazmat_declaration": declaration,
                    "issued_on": c.today(self.env),
                    "issued_by_id": self.env.uid,
                }
            )
        )
        # never hand back a record that still carries the guard token
        return self.browse(manifest.id)


class FixEwasteManifestLine(models.Model):
    _name = "fix.ewaste.manifest.line"
    _description = "E-Waste Manifest Line"
    _inherit = ["fix.guarded.mixin"]

    manifest_id = fields.Many2one(
        "fix.ewaste.manifest", required=True, ondelete="cascade", index=True
    )
    company_id = fields.Many2one(related="manifest_id.company_id", store=True)
    collection_id = fields.Many2one("fix.ewaste.collection", ondelete="restrict")
    battery_id = fields.Many2one("fix.ewaste.battery", ondelete="restrict")
    description = fields.Char()
    material_type = fields.Char()
    weight_kg = fields.Float()
    hazardous = fields.Boolean()
    un_number = fields.Char()
    swollen_cell = fields.Boolean()
    wipe_certificate_id = fields.Many2one("fix.data.wipe.certificate", ondelete="restrict")

    def _fix_guarded_fields(self) -> set:
        return set(super()._fix_guarded_fields()) | {
            "manifest_id",
            "collection_id",
            "battery_id",
            "description",
            "material_type",
            "weight_kg",
            "hazardous",
            "un_number",
            "swollen_cell",
            "wipe_certificate_id",
        }

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_open():
            raise UserError("Manifest lines are written by the batch dispatch.")
        return super().create(vals_list)


class _FixEwasteLicenceRecord(models.AbstractModel):
    """A dated authorisation recorded by one compliance user and confirmed by
    another (four eyes), frozen once confirmed, expired by cron."""

    _name = "fix.ewaste.licence.record"
    _description = "E-Waste Dated Authorisation"
    _inherit = ["mail.thread", "fix.guarded.mixin"]

    _CONFIRMED_STATE = "active"
    _EDITABLE_AFTER = frozenset({"notes"})

    valid_from = fields.Date()
    valid_to = fields.Date()
    evidence_attachment_id = fields.Many2one("ir.attachment", ondelete="restrict")
    confirmed_by_id = fields.Many2one("res.users", readonly=True)
    confirmed_on = fields.Date(readonly=True)
    notes = fields.Text()

    def _fix_guarded_fields(self) -> set:
        return set(super()._fix_guarded_fields()) | {"state", "confirmed_by_id", "confirmed_on"}

    def _fix_frozen_names(self):
        if self.state == "draft":
            return set()
        return {
            n
            for n, f in self._fields.items()
            if f.store
            and not f.readonly
            and n not in _LOG_COLUMNS
            and f.type != "one2many"
            and n not in self._EDITABLE_AFTER
            and not n.startswith(("message_", "activity_"))
        }

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        for rec in self:
            locked |= rec._fix_frozen_names()
        return locked

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self:
                changed = c.changed_fields(rec, vals, rec._fix_frozen_names())
                if changed:
                    c.frozen_refuse(rec, changed, "is %s" % rec.state)
        return super().write(vals)

    def _fix_confirm(self, group, label, required):
        c.require_group(self.env, group, label, "confirm %s" % self._description)
        today = c.today(self.env)
        for rec in self:
            if rec.state != "draft":
                raise UserError("%s is not a draft." % rec.display_name)
            if not self.env.su and rec.create_uid == self.env.user:
                raise UserError("You recorded %s: another officer confirms it." % rec.display_name)
            missing = [rec._fields[n].string for n in required if not rec[n]]
            if missing:
                raise UserError("%s needs: %s." % (rec.display_name, ", ".join(missing)))
            if rec.valid_to and rec.valid_to < today:
                raise UserError("%s is already out of date." % rec.display_name)
            rec._guarded().write(
                {
                    "state": self._CONFIRMED_STATE,
                    "confirmed_by_id": self.env.uid,
                    "confirmed_on": today,
                }
            )

    @api.model
    def _fix_expire(self, today):
        lapsed = self.sudo().search(
            [
                ("state", "=", self._CONFIRMED_STATE),
                ("valid_to", "!=", False),
                ("valid_to", "<", today),
            ]
        )
        for rec in lapsed:
            rec._guarded().write({"state": "expired"})
            c.notify(
                rec,
                "%s expired" % self._description,
                "%s expired on %s." % (rec.display_name, rec.valid_to),
                c.G_COMPLIANCE,
            )
        return lapsed


class FixEwasteBaselPic(models.Model):
    """Basel Convention prior informed consent for a cross-border transfer
    (BRU-ESG-06; all e-waste since 1 January 2025)."""

    _name = "fix.ewaste.basel.pic"
    _description = "Basel Prior Informed Consent"
    _inherit = ["fix.ewaste.licence.record"]
    _order = "valid_to desc, id desc"
    _CONFIRMED_STATE = "consented"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    partner_id = fields.Many2one(
        "fix.ewaste.partner", string="Importing Recycler", required=True, ondelete="restrict"
    )
    destination_country_id = fields.Many2one("res.country", required=True)
    importing_authority = fields.Char(string="Competent Authority of Import")
    consent_ref = fields.Char(string="Consent Reference")
    max_weight_kg = fields.Float(string="Consented Quantity (kg)")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("consented", "Consented"),
            ("expired", "Expired"),
            ("withdrawn", "Withdrawn"),
        ],
        required=True,
        default="draft",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.ewaste.basel.pic")
                    or "EPIC/New"
                )
        return super().create(vals_list)

    def action_record_consent(self):
        self._fix_confirm(
            c.G_COMPLIANCE,
            "E-Waste Compliance Officer",
            ("consent_ref", "evidence_attachment_id", "valid_to", "importing_authority"),
        )
        return True

    def action_withdraw(self):
        c.require_group(
            self.env, c.G_COMPLIANCE, "E-Waste Compliance Officer", "withdraw a consent"
        )
        for rec in self:
            if rec.state != "consented":
                raise UserError("Only a consented PIC is withdrawn.")
            rec._guarded().write({"state": "withdrawn"})
        return True


class FixEwasteRegistration(models.Model):
    """The company's DoE e-waste registration (Hazardous Waste (E-waste)
    Management Rules 2021) and its EPR collection target (FR-ESG-016)."""

    _name = "fix.ewaste.registration"
    _description = "DoE E-Waste Registration"
    _inherit = ["fix.ewaste.licence.record"]
    _order = "valid_to desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    authority = fields.Selection(
        [("doe", "Department of Environment"), ("btrc", "BTRC")], required=True, default="doe"
    )
    role = fields.Selection(
        [
            ("collection_centre", "Collection Centre"),
            ("repairer", "Repairer / Refurbisher"),
            ("dismantler", "Dismantler"),
            ("recycler", "Recycler"),
            ("producer", "Producer (EPR)"),
        ],
        required=True,
        default="collection_centre",
    )
    registration_no = fields.Char()
    issuing_office = fields.Char()
    management_plan_ref = fields.Char(string="E-Waste Management Plan Ref")
    epr_target_pct = fields.Float(string="EPR Collection Target %")
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("expired", "Expired")],
        required=True,
        default="draft",
    )

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_open():
            c.require_group(
                self.env, c.G_COMPLIANCE, "E-Waste Compliance Officer", "record a DoE registration"
            )
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.ewaste.registration")
                    or "EREG/New"
                )
        return super().create(vals_list)

    def action_activate(self):
        self._fix_confirm(
            c.G_COMPLIANCE,
            "E-Waste Compliance Officer",
            ("registration_no", "evidence_attachment_id", "valid_to"),
        )
        return True

    @api.model
    def _fix_active_for(self, company, authority):
        today = c.today(self.env)
        return self.sudo().search(
            [
                ("company_id", "=", company.id),
                ("authority", "=", authority),
                ("state", "=", "active"),
                "|",
                ("valid_to", "=", False),
                ("valid_to", ">=", today),
            ],
            limit=1,
        )


class FixEwasteSettlement(models.Model):
    """Money in M18 (M18-13 / E10): a customer buy-back incentive, a recycler
    fee, or material-recovery income. Approved through M63 by the finance
    approver (amount and payee pinned), then handed to finance by event: the
    GL posting is finance's (cd_gl_ext is being changed by A08)."""

    _name = "fix.ewaste.settlement"
    _description = "E-Waste Incentive / Recycler Fee / Recovery Income"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.approvable.mixin"]
    _order = "id desc"

    _approval_domain = "ewaste_settlement"
    _approval_apply_method = "action_approve_settlement"
    _approval_group = c.G_FINANCE
    _approval_routed = True

    name = fields.Char(required=True, default="New", readonly=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    kind = fields.Selection(
        [
            ("incentive", "Customer Buy-back / Incentive"),
            ("recycler_fee", "Recycler Fee (we pay)"),
            ("recovery_income", "Material-Recovery Income (we receive)"),
        ],
        required=True,
        default="incentive",
    )
    collection_id = fields.Many2one("fix.ewaste.collection", ondelete="restrict")
    batch_id = fields.Many2one("fix.ewaste.batch", ondelete="restrict")
    partner_id = fields.Many2one("res.partner", string="Payee / Payer", required=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    amount = fields.Monetary(currency_field="currency_id", required=True)
    rate_per_kg = fields.Monetary(currency_field="currency_id")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("approved", "Approved - Handed to Finance"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        default="draft",
    )
    approved_by_id = fields.Many2one("res.users", readonly=True)
    approved_on = fields.Datetime(readonly=True)
    notes = fields.Text()

    _TERMS = frozenset(
        {
            "kind",
            "collection_id",
            "batch_id",
            "partner_id",
            "currency_id",
            "amount",
            "rate_per_kg",
            "company_id",
        }
    )

    _amount_positive = models.Constraint("CHECK (amount > 0)", "An amount is positive")

    def _fix_guarded_fields(self) -> set:
        return set(super()._fix_guarded_fields()) | {"state", "approved_by_id", "approved_on"}

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self and any(r.state != "draft" for r in self):
            locked |= self._TERMS
        return locked

    def _approval_amount(self) -> float:
        return abs(self.amount or 0.0) if len(self) == 1 else 0.0

    def _approval_needed(self) -> bool:
        self.ensure_one()
        return self.state == "draft"

    def _approval_pinned_fields(self) -> set:
        return set(super()._approval_pinned_fields()) | {"kind", "collection_id", "batch_id"}

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.ewaste.settlement")
                    or "ESET/New"
                )
        recs = super().create(vals_list)
        recs._check_basis()
        return recs

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self:
                if rec.state != "draft":
                    changed = c.changed_fields(rec, vals, self._TERMS)
                    if changed:
                        c.frozen_refuse(rec, changed, "is %s" % rec.state)
        res = super().write(vals)
        if self._TERMS & set(vals):
            self._check_basis()
        return res

    def _check_basis(self):
        for rec in self:
            if rec.kind == "incentive":
                if not rec.collection_id or rec.batch_id:
                    raise ValidationError("An incentive is paid for one collection.")
                if rec.partner_id != rec.collection_id.customer_id:
                    raise ValidationError("An incentive is paid to the collection's customer.")
                others = self.sudo().search_count(
                    [
                        ("id", "!=", rec.id),
                        ("kind", "=", "incentive"),
                        ("collection_id", "=", rec.collection_id.id),
                        ("state", "!=", "cancelled"),
                    ]
                )
                if others:
                    raise ValidationError(
                        "Collection %s already has an incentive." % rec.collection_id.name
                    )
            else:
                if not rec.batch_id or rec.collection_id:
                    raise ValidationError("A recycler fee or income belongs to one batch.")
                contact = rec.batch_id.partner_id.partner_id
                if contact and rec.partner_id != contact:
                    raise ValidationError(
                        "The recycler fee or income is with the batch's recycler (%s)."
                        % contact.name
                    )

    def action_approve_settlement(self):
        """Apply the routed approval (M63) and hand the money to finance."""
        self._approval_assert_routed()
        c.require_group(
            self.env, c.G_FINANCE, "E-Waste Finance Approver (CFO)", "approve e-waste money"
        )
        for rec in self:
            if rec.state != "draft":
                raise UserError("%s is not a draft." % rec.name)
            if rec.kind == "incentive" and rec.collection_id.state == "collected":
                # BRU-ESG-13: an incentive only on confirmed physical receipt,
                # i.e. once the item has been assessed
                raise UserError(
                    "Collection %s is not assessed yet: an incentive is paid on confirmed "
                    "receipt (triage)." % rec.collection_id.name
                )
            if rec.kind != "incentive" and rec.batch_id.state not in ("received", "processed"):
                raise UserError(
                    "Batch %s has not reached the recycler: its fee or income is approved "
                    "on the recycler's receipt." % rec.batch_id.name
                )
            rec._guarded().write(
                {
                    "state": "approved",
                    "approved_by_id": self.env.uid,
                    "approved_on": fields.Datetime.now(),
                }
            )
            publish(
                rec.env,
                "ewaste.settlement_approved",
                "fix.ewaste.settlement",
                rec.id,
                {
                    "kind": rec.kind,
                    "amount": rec.amount,
                    "currency": rec.currency_id.name,
                    "partner_id": rec.partner_id.id,
                    "collection_id": rec.collection_id.id or None,
                    "batch_id": rec.batch_id.id or None,
                    "company_id": rec.company_id.id,
                    "direction": "in" if rec.kind == "recovery_income" else "out",
                },
            )
        return True

    def action_cancel(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft is cancelled; finance reverses an approved one.")
            if rec.approval_state == "pending":
                rec.action_recall_approval()
            rec._guarded().write({"state": "cancelled"})
        return True
