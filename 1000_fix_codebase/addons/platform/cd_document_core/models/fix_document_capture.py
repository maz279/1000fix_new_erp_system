# cd_document_core — M24 capture audit, second pass (19 Nov 2026).
#
# The 13 Nov pass gave every M24 sub-module page a button, but the records
# the M24 spec (§5, §8, §9, §10.1) says a person captures on several pages
# had no model at all, and one existing capture broke a hard rule:
#
#   page 1  fix.physical.record          FR-DMS-013, AUT-DMS-20: where a paper
#                                        original is kept, by whom, and its
#                                        evidenced destruction.
#           fix.document.integrity.check T-13, AUT-DMS-19: a sweep that re-hashes
#                                        stored bytes against the fingerprint.
#   page 2  template governance          FR-DMS-021, BRU-DMS-09: a template is
#                                        approved by a Document Controller who
#                                        did not write it; a change is a new
#                                        version, never an edit.
#   page 3  fix.document.class           FR-DMS-004, BRU-DMS-01: the class
#                                        taxonomy with mandatory metadata.
#           fix.document.exception       FR-DMS-006, BRU-DMS-08, AUT-DMS-03:
#                                        the unclassifiable-capture queue.
#   page 4  fix.document.distribution    FR-DMS-019: a published controlled
#                                        document sent to named people, each
#                                        acknowledging with their own login.
#   page 6  fix.disposal.batch           FR-DMS-038, §8.3, SOD-23: disposal is
#                                        proposed by one officer and approved by
#                                        another. Before this a Records Officer
#                                        disposed of a document alone, with no
#                                        approval (BRU-DMS-05 / FR-DMS-038).
#           fix.retention.violation      FR-DMS-040, BRU-DMS-19, AUT-DMS-11.
#           fix.legal.hold.order         FR-DMS-036/037: a hold over a SCOPE
#                                        (class, type, business object, dates),
#                                        propagated to documents filed later.
#   page 7  fix.evidence.pack            FR-DMS-041, AUT-DMS-15: assembled,
#                                        completeness-checked, sealed.
#           fix.external.release         FR-DMS-042, BRU-DMS-13 (the registry's
#                                        "Share Token"): scoped, approved,
#                                        time-boxed, watermarked, logged.
#           fix.document.access.log      T-11, BRU-DMS-12.
#
# No new event types: outcomes go to the chatter (the event registry is a
# contract; see the area-audit playbook).
from __future__ import annotations

import base64
import hashlib
import json
import secrets
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError

# the models this file extends load first, whatever order a formatter gives
# models/__init__.py (the M20 isort trap)
from . import fix_disposal, fix_document, fix_document_template, fix_legal_hold  # noqa: F401

RECORDS_GROUP = "cd_document_core.group_document_records"
CONTROLLER_GROUP = "cd_document_core.group_document_controller"
DISPOSAL_APPROVER_GROUP = "cd_document_core.group_disposal_approver"

PARAM_RELEASE_MAX_DAYS = "cd_document_core.external_release_max_days"
DEFAULT_RELEASE_MAX_DAYS = 30
PARAM_OVER_RETENTION_GRACE = "cd_document_core.over_retention_grace_days"
DEFAULT_OVER_RETENTION_GRACE = 90

ISOLATION_TIERS = [
    ("T1", "T1 — Internal"),
    ("T2", "T2 — Branch-scoped"),
    ("T3", "T3 — Role-scoped"),
    ("T5", "T5 — Residency-classified"),
]
_TIER_RANK = {"T1": 1, "T2": 2, "T3": 3, "T5": 5}

ASSURANCE_LEVELS = [
    ("email_link", "Email link"),
    ("in_app", "In-app authenticated"),
    ("otp", "Phone OTP"),
    ("wet_scan", "Wet-ink signature, scanned"),
    ("qualified", "Provider-backed qualified signature"),
]

# Disposal runs only from an approved batch. The key carries an in-process
# object, so a JSON-RPC caller cannot put it in the context (same pattern as
# fix.guarded.mixin).
BATCH_KEY = "fix_dms_disposal_batch"
_BATCH_TOKEN = object()


def _require(env, group, what):
    if env.su or env.user.has_group(group):
        return
    raise AccessError("%s is done by a %s." % (what, env.ref(group).name))


def _require_any(env, groups, what):
    if env.su or any(env.user.has_group(g) for g in groups):
        return
    raise AccessError("%s is done by a %s." % (what, " or ".join(env.ref(g).name for g in groups)))


def _not_maker(env, makers, what):
    """Segregation of duties: whoever prepared it does not approve it."""
    if env.su:
        return
    if env.user in makers:
        raise UserError(
            "Segregation of duties: %s prepared or last changed this and cannot also %s it."
            % (env.user.name, what)
        )


def _doc_type_selection(self):
    return self.env["fix.document"]._fields["document_type"].selection


def _bytes_of(document):
    attachment = document.sudo().attachment_id
    if attachment and attachment.datas:
        try:
            return base64.b64decode(attachment.datas)
        except Exception:
            return str(attachment.datas).encode("utf-8")
    return b""


class FixDmsNumberedMixin(models.AbstractModel):
    """A readable reference stamped after create (PREFIX-00042)."""

    _name = "fix.dms.numbered.mixin"
    _description = "M24 numbered record"
    _dms_prefix = "DMS"

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if not rec.name or rec.name == "/":
                rec.sudo().write({"name": "%s-%05d" % (self._dms_prefix, rec.id)})
        return records


# =============================================================== page 3
class FixDocumentClass(models.Model):
    """One class of the document taxonomy (FR-DMS-004).

    The class decides the retention class, the minimum confidentiality tier,
    the metadata a document of the class must carry, and the signature
    assurance level an envelope over it needs (BRU-DMS-17). Written by a
    Records Officer or Document Controller, activated by a Document Controller
    who did not write it; terms freeze once active (retire and write a new
    one). Classification is enforced from the moment the first class of a
    company is active."""

    _name = "fix.document.class"
    _description = "Document Class"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "code"
    _code_unique = models.Constraint("UNIQUE (company_id, code)", "Class code must be unique")

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    code = fields.Char(required=True, size=24)
    name = fields.Char(required=True, tracking=True)
    name_bn = fields.Char(string="Name (Bengali)")
    parent_id = fields.Many2one("fix.document.class", string="Parent Class", ondelete="restrict")
    document_type = fields.Selection(
        selection=_doc_type_selection,
        required=True,
        help="The kernel document type this class governs: a document of this type is "
        "filed under this class.",
    )
    isolation_tier = fields.Selection(
        ISOLATION_TIERS,
        string="Confidentiality Tier",
        required=True,
        default="T1",
        help="The minimum tier a document of this class is filed at.",
    )
    retention_class_id = fields.Many2one(
        "fix.retention.class",
        required=True,
        ondelete="restrict",
        help="BRU-DMS-01: every document has exactly one retention class.",
    )
    template_id = fields.Many2one("fix.document.template", string="Generating Template")
    need_name_bn = fields.Boolean(string="Bengali name is mandatory")
    need_link = fields.Boolean(
        string="Business-object link is mandatory",
        help="The document must name the record it belongs to (FR-DMS-005).",
    )
    need_description = fields.Boolean(string="Description is mandatory")
    need_operating_unit = fields.Boolean(string="Branch / operating unit is mandatory")
    requires_signature = fields.Boolean()
    signature_assurance_level = fields.Selection(
        ASSURANCE_LEVELS,
        help="BRU-DMS-17: decided by the class, never by the requester. A qualified level "
        "accepts only the provider's signature.",
    )
    note = fields.Text(string="Scope / Notes")
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("retired", "Retired")],
        default="draft",
        required=True,
        tracking=True,
    )
    last_edited_by_id = fields.Many2one("res.users", string="Last Edited By", readonly=True)
    activated_by_id = fields.Many2one("res.users", string="Activated By", readonly=True, copy=False)
    activated_at = fields.Datetime(readonly=True, copy=False)

    _TERMS = (
        "company_id",
        "code",
        "document_type",
        "isolation_tier",
        "retention_class_id",
        "need_name_bn",
        "need_link",
        "need_description",
        "need_operating_unit",
        "signature_assurance_level",
        "requires_signature",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "activated_by_id",
            "activated_at",
            "last_edited_by_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(r.state != "draft" for r in self):
            locked |= set(self._TERMS)
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        _require_any(self.env, (RECORDS_GROUP, CONTROLLER_GROUP), "Writing a document class")
        records = super().create(vals_list)
        records._guarded().write({"last_edited_by_id": self.env.uid})
        return records

    def write(self, vals):
        if not self._fix_guard_open():
            terms = set(self._TERMS) & set(vals)
            for rec in self:
                if rec.state != "draft" and any(
                    rec._fix_guard_differs(n, vals[n], rec[n]) for n in terms
                ):
                    raise UserError(
                        "Class %s is %s: its terms are frozen. Retire it and write a new one."
                        % (rec.code, rec.state)
                    )
            result = super().write(vals)
            super(FixDocumentClass, self._guarded()).write({"last_edited_by_id": self.env.uid})
            return result
        return super().write(vals)

    def missing_metadata(self, document):
        """Mandatory metadata the document lacks under this class."""
        self.ensure_one()
        missing = []
        if self.need_name_bn and not document.name_bn:
            missing.append("Bengali name")
        if self.need_link and not (document.res_model and document.res_id):
            missing.append("business-object link")
        if self.need_description and not document.description:
            missing.append("description")
        if self.need_operating_unit and not document.operating_unit_id:
            missing.append("branch / operating unit")
        return missing

    def action_activate(self):
        _require(self.env, CONTROLLER_GROUP, "Activating a document class")
        for rec in self:
            if rec.state != "draft":
                raise UserError(
                    "Only a draft class is activated — %s is %s." % (rec.code, rec.state)
                )
            _not_maker(self.env, rec.create_uid | rec.last_edited_by_id, "activate")
            clash = self.search(
                [
                    ("id", "!=", rec.id),
                    ("company_id", "=", rec.company_id.id),
                    ("document_type", "=", rec.document_type),
                    ("state", "=", "active"),
                ],
                limit=1,
            )
            if clash:
                raise UserError(
                    "Class %s already governs this document type. A document has exactly one "
                    "class (BRU-DMS-01): retire %s first." % (clash.code, clash.code)
                )
            rec._guarded().write(
                {
                    "state": "active",
                    "activated_by_id": self.env.uid,
                    "activated_at": fields.Datetime.now(),
                }
            )
            rec.message_post(body="Activated by %s." % self.env.user.name)
        return True

    def action_retire(self):
        _require(self.env, CONTROLLER_GROUP, "Retiring a document class")
        for rec in self:
            if rec.state != "active":
                raise UserError(
                    "Only an active class is retired — %s is %s." % (rec.code, rec.state)
                )
            rec._guarded().write({"state": "retired"})
            rec.message_post(body="Retired by %s." % self.env.user.name)
        return True


class FixDocumentException(models.Model):
    """A capture that could not be classified (BRU-DMS-08): it is queued for a
    Records Officer, never discarded and never filed unclassified."""

    _name = "fix.document.exception"
    _description = "Classification Exception"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin", "fix.dms.numbered.mixin"]
    _order = "id desc"
    _dms_prefix = "DMS-EXC"

    name = fields.Char(default="/", readonly=True, copy=False)
    document_id = fields.Many2one("fix.document", required=True, ondelete="restrict", index=True)
    company_id = fields.Many2one(related="document_id.company_id", store=True, index=True)
    source = fields.Char(readonly=True, help="The model that filed it, or 'upload'.")
    cause = fields.Text(readonly=True)
    received_at = fields.Datetime(default=fields.Datetime.now, readonly=True)
    assigned_to_id = fields.Many2one("res.users", string="Assigned To", tracking=True)
    state = fields.Selection(
        [("open", "Open"), ("resolved", "Resolved")], default="open", required=True, tracking=True
    )
    resolved_by_id = fields.Many2one("res.users", readonly=True)
    resolved_at = fields.Datetime(readonly=True)
    resolution_note = fields.Text()
    # the Records Officer supplies the missing class and metadata here; the
    # values land on the document itself
    doc_class_id = fields.Many2one(
        related="document_id.class_id", readonly=False, string="Document Class"
    )
    doc_name_bn = fields.Char(related="document_id.name_bn", readonly=False, string="Bengali Name")
    doc_description = fields.Text(
        related="document_id.description", readonly=False, string="Description"
    )
    doc_res_model = fields.Char(
        related="document_id.res_model", readonly=False, string="Linked Model"
    )
    doc_res_id = fields.Integer(
        related="document_id.res_id", readonly=False, string="Linked Record ID"
    )
    doc_operating_unit_id = fields.Many2one(
        related="document_id.operating_unit_id", readonly=False, string="Branch"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "resolved_by_id",
            "resolved_at",
            "document_id",
            "source",
            "cause",
            "received_at",
        }

    def write(self, vals):
        if not self._fix_guard_open() and any(k.startswith("doc_") for k in vals):
            _require(self.env, RECORDS_GROUP, "Classifying a queued document")
            if any(r.state != "open" for r in self):
                raise UserError("A resolved exception is closed; its document is filed.")
        return super().write(vals)

    def action_resolve(self, note=None):
        """The Records Officer files the document once its class and mandatory
        metadata are supplied (the Exception Queue → Filed guard, §8.1)."""
        _require(self.env, RECORDS_GROUP, "Resolving a classification exception")
        for rec in self:
            if rec.state != "open":
                raise UserError("%s is already resolved." % rec.name)
            doc = rec.document_id
            cls = doc.class_id
            if not cls or cls.state != "active":
                raise UserError(
                    "Choose an ACTIVE document class for '%s' before filing it." % doc.name
                )
            if cls.document_type != doc.document_type:
                raise UserError(
                    "Class %s governs another document type; '%s' cannot be filed under it."
                    % (cls.code, doc.name)
                )
            missing = cls.missing_metadata(doc)
            if missing:
                raise UserError(
                    "'%s' still lacks the metadata class %s makes mandatory: %s."
                    % (doc.name, cls.code, ", ".join(missing))
                )
            vals = {"filing_state": "filed"}
            if not doc.retention_class_id:
                vals["retention_class_id"] = cls.retention_class_id.id
            if _TIER_RANK.get(doc.isolation_tier, 1) < _TIER_RANK.get(cls.isolation_tier, 1):
                vals["isolation_tier"] = cls.isolation_tier
            doc._guarded().write(vals)
            rec._guarded().write(
                {
                    "state": "resolved",
                    "resolved_by_id": self.env.uid,
                    "resolved_at": fields.Datetime.now(),
                    "resolution_note": (note or rec.resolution_note or "").strip() or False,
                }
            )
            doc.message_post(
                body="Filed under class %s by %s (%s)." % (cls.code, self.env.user.name, rec.name)
            )
        return True


# ============================================ fix.document: classification,
# propagation of scoped holds, disposal only through an approved batch
class FixDocumentCapture(models.Model):
    _inherit = "fix.document"

    class_id = fields.Many2one(
        "fix.document.class",
        string="Document Class",
        index=True,
        tracking=True,
        ondelete="restrict",
    )
    filing_state = fields.Selection(
        [("filed", "Filed"), ("exception", "In Exception Queue")],
        default="filed",
        required=True,
        tracking=True,
        help="A capture that cannot be classified waits in the exception queue (BRU-DMS-08).",
    )
    physical_record_ids = fields.One2many("fix.physical.record", "document_id")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"filing_state"}

    @api.model
    def _dms_classification_on(self, company_id):
        return bool(
            self.env["fix.document.class"]
            .sudo()
            .search_count([("company_id", "=", company_id), ("state", "=", "active")], limit=1)
        )

    @api.model
    def _dms_class_for(self, company_id, document_type):
        return (
            self.env["fix.document.class"]
            .sudo()
            .search(
                [
                    ("company_id", "=", company_id),
                    ("document_type", "=", document_type),
                    ("state", "=", "active"),
                ],
                limit=1,
            )
        )

    @api.model_create_multi
    def create(self, vals_list):
        company = self.env.company.id
        for vals in vals_list:
            cid = vals.get("company_id") or company
            if vals.get("template_id"):
                template = self.env["fix.document.template"].sudo().browse(vals["template_id"])
                # FR-DMS-021: a template CHANGE needs approval before use, and a
                # retired version generates nothing. A first version loaded before
                # governance (cd_hr_core's Form 6 templates) still generates; it
                # shows as Draft until a Document Controller approves it.
                if template.state == "retired" or (
                    template.state == "draft" and template.previous_id
                ):
                    raise UserError(
                        "Template %s v%s is %s: a document is generated only from the "
                        "approved version, never from an unapproved change or a retired "
                        "one (FR-DMS-021, BRU-DMS-09)."
                        % (template.code, template.version, template.state)
                    )
            if vals.get("class_id"):
                continue
            cls = self._dms_class_for(cid, vals.get("document_type") or "other")
            if cls:
                vals["class_id"] = cls.id
                if not vals.get("retention_class_id"):
                    vals["retention_class_id"] = cls.retention_class_id.id
                if _TIER_RANK.get(vals.get("isolation_tier") or "T1", 1) < _TIER_RANK.get(
                    cls.isolation_tier, 1
                ):
                    vals["isolation_tier"] = cls.isolation_tier
        records = super().create(vals_list)
        records._dms_route_unclassified()
        records._dms_apply_scoped_holds()
        return records

    def _dms_route_unclassified(self):
        """BRU-DMS-08: a document that cannot be classified, or lacks its
        class's mandatory metadata, is filed into the exception queue."""
        Exception_ = self.env["fix.document.exception"].sudo()
        for rec in self:
            if rec.state == "destroyed" or not self._dms_classification_on(rec.company_id.id):
                continue
            cls = rec.class_id
            if not cls:
                cause = "No active document class governs type '%s'." % dict(
                    rec._fields["document_type"].selection
                ).get(rec.document_type, rec.document_type)
            else:
                missing = cls.missing_metadata(rec)
                if not missing:
                    continue
                cause = "Class %s needs: %s." % (cls.code, ", ".join(missing))
            rec._guarded().write({"filing_state": "exception"})
            Exception_.create(
                {"document_id": rec.id, "source": rec.res_model or "upload", "cause": cause}
            )
            rec.message_post(body="Not filed — queued for a Records Officer: %s" % cause)

    def _dms_apply_scoped_holds(self):
        """FR-DMS-036: a hold over a scope also catches documents filed later."""
        orders = self.env["fix.legal.hold.order"].sudo().search([("state", "=", "applied")])
        for order in orders:
            hits = self.filtered(lambda d, o=order: o._matches(d))
            if hits:
                order._hold_documents(hits)

    def action_dispose(self, method: str = "secure_wipe"):
        """FR-DMS-038 / SOD-23 / BRU-DMS-05: a document is disposed only by an
        APPROVED disposal batch — one officer proposes, another approves. A
        lone Records Officer could dispose of a document before this pass."""
        if self.env.context.get(BATCH_KEY) is not _BATCH_TOKEN:
            raise UserError(
                "A document is disposed only through an approved Disposal Batch: a Records "
                "Officer proposes it and a Disposal Approver who did not prepare it approves "
                "it (FR-DMS-038, SOD-23). Use + Disposal Batch on Retention & Holds."
            )
        return super().action_dispose(method)

    def action_release_hold(self, reason: str = ""):
        """A document under several matters is released matter by matter on the
        Legal Holds register: releasing all of them with one reason would lift
        holds nobody decided to lift (BRU-DMS-04)."""
        for rec in self:
            if (
                self.env["fix.legal.hold"]
                .sudo()
                .search_count([("document_id", "=", rec.id), ("state", "=", "held")])
                > 1
            ):
                raise UserError(
                    "'%s' is held under more than one matter. Release each matter on the Legal "
                    "Holds register." % rec.name
                )
        return super().action_release_hold(reason)


# =============================================================== page 1
class FixPhysicalRecord(models.Model):
    """A paper original that must be kept besides its digital copy
    (FR-DMS-013): where it is, who holds it, its condition, and its evidenced
    destruction once the retention of its document has run."""

    _name = "fix.physical.record"
    _description = "Physical Record (Paper Original)"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin", "fix.dms.numbered.mixin"]
    _order = "id desc"
    _dms_prefix = "PHY"

    name = fields.Char(default="/", readonly=True, copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    document_id = fields.Many2one(
        "fix.document",
        string="Digital Copy",
        required=True,
        ondelete="restrict",
        index=True,
        help="The filed digital record of this original; the two are never confused.",
    )
    location = fields.Char(
        required=True, tracking=True, help="Branch store room, cabinet, offsite archive…"
    )
    box_ref = fields.Char(string="Box / File Reference", tracking=True)
    custodian_id = fields.Many2one(
        "res.users", required=True, tracking=True, default=lambda self: self.env.user
    )
    received_on = fields.Date(required=True, default=fields.Date.context_today)
    condition = fields.Selection(
        [("good", "Good"), ("fair", "Fair"), ("poor", "Poor"), ("damaged", "Damaged")],
        default="good",
        required=True,
        tracking=True,
    )
    destruction_due_on = fields.Date(
        compute="_compute_due", store=True, help="The retention expiry of the digital copy."
    )
    evidence_file = fields.Binary(string="Destruction Evidence (upload)", store=False)
    evidence_filename = fields.Char(store=False)
    destruction_evidence_id = fields.Many2one("fix.document", readonly=True, ondelete="restrict")
    state = fields.Selection(
        [("in_custody", "In Custody"), ("destroyed", "Destroyed")],
        default="in_custody",
        required=True,
        tracking=True,
    )
    destroyed_on = fields.Date(readonly=True)
    destroyed_by_id = fields.Many2one("res.users", readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "destroyed_on",
            "destroyed_by_id",
            "destruction_evidence_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and all(r.state == "destroyed" for r in self):
            locked |= {
                "document_id",
                "location",
                "box_ref",
                "custodian_id",
                "condition",
                "received_on",
                "evidence_file",
            }
        return locked

    @api.depends("document_id.retention_expires")
    def _compute_due(self):
        for rec in self:
            rec.destruction_due_on = rec.document_id.retention_expires

    @api.model_create_multi
    def create(self, vals_list):
        _require(self.env, RECORDS_GROUP, "Registering a paper original")
        files = [
            (v.pop("evidence_file", None), v.pop("evidence_filename", None)) for v in vals_list
        ]
        records = super().create(vals_list)
        for rec, (data, fname) in zip(records, files, strict=True):
            if data:
                rec._file_evidence(data, fname)
        return records

    def write(self, vals):
        data = vals.pop("evidence_file", None)
        fname = vals.pop("evidence_filename", None)
        if not self._fix_guard_open() and {"location", "custodian_id", "box_ref"} & set(vals):
            _require(self.env, RECORDS_GROUP, "Moving a paper original")
            if any(r.state == "destroyed" for r in self):
                raise UserError("A destroyed original has no location or custodian to change.")
        result = super().write(vals) if vals else True
        if data:
            for rec in self:
                rec._file_evidence(data, fname)
        return result

    def _file_evidence(self, data, fname):
        self.ensure_one()
        if self.state == "destroyed":
            raise UserError("%s is already destroyed; its evidence is on file." % self.name)
        doc = (
            self.env["fix.document"]
            .sudo()
            .attach(
                name=fname or "Destruction evidence — %s" % self.name,
                datas=data,
                document_type="destruction_certificate",
                res_model="fix.physical.record",
                res_id=self.id,
            )
        )
        self._guarded().write({"destruction_evidence_id": doc.id})

    def action_record_destruction(self):
        """AUT-DMS-20: the original is destroyed only once its retention has
        run, never while held, and only with evidence on file."""
        _require(self.env, RECORDS_GROUP, "Recording the destruction of a paper original")
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.state != "in_custody":
                raise UserError("%s is already destroyed." % rec.name)
            doc = rec.document_id
            if doc.legal_hold:
                raise UserError(
                    "The document of %s is under legal hold: its original cannot be destroyed."
                    % rec.name
                )
            if doc.state not in ("expired", "pending_destruction", "destroyed") and not (
                rec.destruction_due_on and rec.destruction_due_on <= today
            ):
                raise UserError(
                    "The retention of %s has not run (due %s): destroying the original now "
                    "would be a missing-early violation."
                    % (rec.name, rec.destruction_due_on or "—")
                )
            if not rec.destruction_evidence_id:
                raise UserError(
                    "Upload the destruction evidence (shredding certificate, photograph) on %s "
                    "first." % rec.name
                )
            rec._guarded().write(
                {"state": "destroyed", "destroyed_on": today, "destroyed_by_id": self.env.uid}
            )
            rec.message_post(
                body="Original destroyed; evidence %s." % rec.destruction_evidence_id.name
            )
        return True

    @api.model
    def cron_destruction_due(self):
        """AUT-DMS-20: the custodian is told when an original falls due."""
        today = fields.Date.today()
        due = self.search(
            [
                ("state", "=", "in_custody"),
                ("destruction_due_on", "!=", False),
                ("destruction_due_on", "<=", today),
            ]
        )
        todo = self.env.ref("mail.mail_activity_data_todo", raise_if_not_found=False)
        count = 0
        for rec in due:
            if rec.activity_ids:
                continue
            rec.activity_schedule(
                activity_type_id=todo.id if todo else False,
                summary="Destroy paper original %s" % rec.name,
                note="Retention ran on %s. Destroy it, upload the evidence and record the destruction."
                % rec.destruction_due_on,
                user_id=rec.custodian_id.id,
            )
            count += 1
        return count


class FixDocumentIntegrityCheck(models.Model):
    """A sweep that re-hashes every stored document against its fingerprint
    (T-13, AUT-DMS-19). Creating one runs it; a weekly job runs one too."""

    _name = "fix.document.integrity.check"
    _description = "Integrity Sweep"
    _inherit = ["mail.thread", "fix.guarded.mixin", "fix.dms.numbered.mixin"]
    _order = "id desc"
    _dms_prefix = "INTEGRITY"

    name = fields.Char(default="/", readonly=True, copy=False)
    note = fields.Text(string="Why this sweep")
    retention_class_id = fields.Many2one(
        "fix.retention.class", string="Only this class", help="Empty: every document."
    )
    run_at = fields.Datetime(readonly=True)
    run_by_id = fields.Many2one("res.users", readonly=True)
    documents_checked = fields.Integer(readonly=True)
    divergences_found = fields.Integer(readonly=True)
    line_ids = fields.One2many("fix.document.integrity.divergence", "check_id", readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "run_at",
            "run_by_id",
            "documents_checked",
            "divergences_found",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self:
            locked |= {"note", "retention_class_id"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        _require_any(self.env, (RECORDS_GROUP, "base.group_system"), "Running an integrity sweep")
        records = super().create(vals_list)
        for rec in records:
            rec._run()
        return records

    def write(self, vals):
        if not self._fix_guard_open() and {"note", "retention_class_id"} & set(vals):
            raise UserError("A sweep that has run is a record: start a new one.")
        return super().write(vals)

    def _run(self):
        self.ensure_one()
        Doc = self.env["fix.document"].sudo().with_context(active_test=False)
        domain = [("state", "!=", "destroyed"), ("checksum_sha256", "!=", False)]
        if self.retention_class_id:
            domain.append(("retention_class_id", "=", self.retention_class_id.id))
        docs = Doc.search(domain)
        Line = self.env["fix.document.integrity.divergence"].sudo()
        bad = 0
        for doc in docs:
            found = hashlib.sha256(_bytes_of(doc)).hexdigest()
            if found != doc.checksum_sha256:
                bad += 1
                Line.create(
                    {
                        "check_id": self.id,
                        "document_id": doc.id,
                        "expected_hash": doc.checksum_sha256,
                        "found_hash": found,
                    }
                )
                doc.message_post(
                    body="Integrity divergence found by %s: stored bytes no longer match "
                    "the fingerprint." % self.name
                )
        # stamped by the system: a sweep's result is never the runner's to write
        self.sudo()._guarded().write(
            {
                "run_at": fields.Datetime.now(),
                "run_by_id": self.env.uid,
                "documents_checked": len(docs),
                "divergences_found": bad,
            }
        )
        self.sudo().message_post(
            body="%d document(s) verified, %d divergence(s)%s."
            % (len(docs), bad, " — escalate to the CTO" if bad else "")
        )

    @api.model
    def cron_integrity_sweep(self):
        return self.sudo().create({"note": "Scheduled sweep (AUT-DMS-19)"}).id


class FixDocumentIntegrityDivergence(models.Model):
    _name = "fix.document.integrity.divergence"
    _description = "Integrity Divergence"
    _order = "id"

    check_id = fields.Many2one(
        "fix.document.integrity.check", required=True, ondelete="cascade", index=True
    )
    document_id = fields.Many2one("fix.document", required=True, ondelete="restrict")
    expected_hash = fields.Char(readonly=True)
    found_hash = fields.Char(readonly=True)


# =============================================================== page 2
class FixDocumentTemplateGovernance(models.Model):
    """FR-DMS-021 / BRU-DMS-09: a template version is approved by a Document
    Controller who did not write it, frozen once approved, and changed only by
    a new version; approving a version retires the previous one."""

    _name = "fix.document.template"
    _inherit = ["fix.document.template", "fix.guarded.mixin"]
    _code_unique = models.Constraint(
        "UNIQUE (code, version)", "Template code and version must be unique"
    )

    version = fields.Integer(default=1, required=True, readonly=True, copy=False)
    state = fields.Selection(
        [("draft", "Draft"), ("approved", "Approved"), ("retired", "Retired")],
        default="draft",
        required=True,
        tracking=True,
        copy=False,
    )
    previous_id = fields.Many2one(
        "fix.document.template", string="Replaces", readonly=True, copy=False
    )
    last_edited_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    approved_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    approved_on = fields.Date(readonly=True, copy=False)

    _TERMS = (
        "code",
        "name",
        "name_bn",
        "document_type",
        "report_ref",
        "bilingual",
        "requires_approval",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "version",
            "previous_id",
            "last_edited_by_id",
            "approved_by_id",
            "approved_on",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(r.state != "draft" for r in self):
            locked |= set(self._TERMS)
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._guarded().write({"last_edited_by_id": self.env.uid})
        return records

    def write(self, vals):
        if not self._fix_guard_open():
            terms = set(self._TERMS) & set(vals)
            for rec in self:
                if rec.state != "draft" and any(
                    rec._fix_guard_differs(n, vals[n], rec[n]) for n in terms
                ):
                    raise UserError(
                        "Template %s v%d is %s: it is never edited. Start a new version."
                        % (rec.code, rec.version, rec.state)
                    )
            result = super().write(vals)
            if terms:
                super(FixDocumentTemplateGovernance, self._guarded()).write(
                    {"last_edited_by_id": self.env.uid}
                )
            return result
        return super().write(vals)

    def action_approve(self):
        _require(self.env, CONTROLLER_GROUP, "Approving a template version")
        for rec in self:
            if rec.state != "draft":
                raise UserError(
                    "Only a draft version is approved — %s v%d is %s."
                    % (rec.code, rec.version, rec.state)
                )
            _not_maker(self.env, rec.create_uid | rec.last_edited_by_id, "approve")
            older = self.search(
                [("id", "!=", rec.id), ("code", "=", rec.code), ("state", "=", "approved")]
            )
            older._guarded().write({"state": "retired"})
            rec._guarded().write(
                {
                    "state": "approved",
                    "approved_by_id": self.env.uid,
                    "approved_on": fields.Date.context_today(rec),
                }
            )
            rec.message_post(body="Version %d approved by %s." % (rec.version, self.env.user.name))
        return True

    def action_new_version(self):
        """Copy an approved version into the next draft (BRU-DMS-09: a
        generated document stays bound to the version it was made from)."""
        drafts = self.browse()
        for rec in self:
            if rec.state != "approved":
                raise UserError("A new version starts from the APPROVED version of %s." % rec.code)
            if self.search_count([("code", "=", rec.code), ("state", "=", "draft")]):
                raise UserError("%s already has a draft version in progress." % rec.code)
            top = max(self.search([("code", "=", rec.code)]).mapped("version") or [rec.version])
            draft = rec._guarded().copy(
                {"code": rec.code, "version": top + 1, "previous_id": rec.id}
            )
            draft._guarded().write({"last_edited_by_id": self.env.uid})
            drafts |= draft
        return {
            "reporter": "Draft version created",
            "note": ", ".join("%s v%d" % (d.code, d.version) for d in drafts),
        }

    def action_retire(self):
        _require(self.env, CONTROLLER_GROUP, "Retiring a template")
        for rec in self:
            if rec.state != "approved":
                raise UserError("Only an approved version is retired.")
            rec._guarded().write({"state": "retired"})
        return True


# =============================================================== page 4
class FixDocumentDistribution(models.Model):
    """FR-DMS-019: a published controlled document distributed to named
    people, each of whom acknowledges it with their own login."""

    _name = "fix.document.distribution"
    _description = "Controlled Document Distribution"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin", "fix.dms.numbered.mixin"]
    _order = "id desc"
    _dms_prefix = "DIST"

    name = fields.Char(default="/", readonly=True, copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    document_id = fields.Many2one(
        "fix.document", string="Controlled Document", required=True, ondelete="restrict", index=True
    )
    recipient_ids = fields.Many2many("res.users", string="Recipients")
    due_on = fields.Date(string="Acknowledge By")
    note = fields.Text(string="Why they must read it")
    state = fields.Selection(
        [("draft", "Draft"), ("distributed", "Distributed"), ("closed", "Closed")],
        default="draft",
        required=True,
        tracking=True,
    )
    distributed_by_id = fields.Many2one("res.users", readonly=True)
    distributed_at = fields.Datetime(readonly=True)
    ack_ids = fields.One2many("fix.document.acknowledgement", "distribution_id", readonly=True)
    recipient_count = fields.Integer(compute="_compute_progress")
    acknowledged_count = fields.Integer(compute="_compute_progress")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "distributed_by_id", "distributed_at"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(r.state != "draft" for r in self):
            locked |= {"document_id", "recipient_ids", "due_on"}
        return locked

    def write(self, vals):
        sent = any(r.state != "draft" for r in self)
        if sent and not self._fix_guard_open() and {"document_id", "recipient_ids"} & set(vals):
            raise UserError(
                "A distribution that has gone out cannot change its document or recipients."
            )
        return super().write(vals)

    @api.depends("ack_ids.state", "recipient_ids")
    def _compute_progress(self):
        for rec in self:
            rec.recipient_count = len(rec.ack_ids) or len(rec.recipient_ids)
            rec.acknowledged_count = len(rec.ack_ids.filtered(lambda a: a.state == "acknowledged"))

    def action_distribute(self):
        Ack = self.env["fix.document.acknowledgement"].sudo()
        todo = self.env.ref("mail.mail_activity_data_todo", raise_if_not_found=False)
        for rec in self:
            doc = rec.document_id
            if not (
                self.env.su
                or self.env.user.has_group(CONTROLLER_GROUP)
                or self.env.user == doc.create_uid
            ):
                raise AccessError(
                    "A controlled document is distributed by its author or a Document Controller."
                )
            if rec.state != "draft":
                raise UserError("%s has already gone out." % rec.name)
            if not doc.is_controlled or doc.control_state != "published" or not doc.is_current:
                raise UserError(
                    "Only the PUBLISHED, CURRENT version of a controlled document is distributed "
                    "— '%s' v%s is %s (BRU-DMS-11)." % (doc.name, doc.version, doc.control_state)
                )
            if not rec.recipient_ids:
                raise UserError("Name at least one recipient.")
            for user in rec.recipient_ids:
                Ack.create({"distribution_id": rec.id, "user_id": user.id})
                if todo:
                    rec.activity_schedule(
                        activity_type_id=todo.id,
                        summary="Read and acknowledge %s v%s" % (doc.name, doc.version),
                        user_id=user.id,
                        date_deadline=rec.due_on or fields.Date.context_today(rec),
                    )
            rec._guarded().write(
                {
                    "state": "distributed",
                    "distributed_by_id": self.env.uid,
                    "distributed_at": fields.Datetime.now(),
                }
            )
            rec.message_post(body="Distributed to %d recipient(s)." % len(rec.recipient_ids))
        return True


class FixDocumentAcknowledgement(models.Model):
    _name = "fix.document.acknowledgement"
    _description = "Controlled Document Acknowledgement"
    _inherit = ["fix.guarded.mixin"]
    _order = "distribution_id desc, id"

    distribution_id = fields.Many2one(
        "fix.document.distribution", required=True, ondelete="cascade", index=True
    )
    document_id = fields.Many2one(related="distribution_id.document_id", store=True)
    company_id = fields.Many2one(related="distribution_id.company_id", store=True)
    user_id = fields.Many2one("res.users", string="Recipient", required=True, readonly=True)
    state = fields.Selection(
        [("pending", "Pending"), ("acknowledged", "Acknowledged")], default="pending", required=True
    )
    acknowledged_at = fields.Datetime(readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "acknowledged_at",
            "user_id",
            "distribution_id",
        }

    def action_acknowledge(self):
        for ack in self:
            if not self.env.su and ack.user_id != self.env.user:
                raise UserError("%s acknowledges with their own login." % ack.user_id.name)
            if ack.state != "pending":
                raise UserError("Already acknowledged.")
            doc = ack.document_id
            if not doc.is_current or doc.control_state != "published":
                raise UserError(
                    "'%s' v%s has been superseded: acknowledge the current version instead."
                    % (doc.name, doc.version)
                )
            ack._guarded().write(
                {"state": "acknowledged", "acknowledged_at": fields.Datetime.now()}
            )
            dist = ack.distribution_id
            dist.sudo().activity_ids.filtered(
                lambda a, u=ack.user_id: a.user_id == u
            ).action_feedback(feedback="Acknowledged")
            if all(a.state == "acknowledged" for a in dist.ack_ids):
                dist.sudo()._guarded().write({"state": "closed"})
                dist.sudo().message_post(body="Every recipient has acknowledged.")
        return True


# =============================================================== page 6
class FixDisposalBatch(models.Model):
    """§8.3: PROPOSED → UNDER REVIEW → APPROVED → EXECUTING → COMPLETED, or
    FAILED with nothing disposed. The officer who prepares a batch cannot
    approve it (SOD-23)."""

    _name = "fix.disposal.batch"
    _description = "Disposal Batch"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin", "fix.dms.numbered.mixin"]
    _order = "id desc"
    _dms_prefix = "DSP-BATCH"

    name = fields.Char(default="/", readonly=True, copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    retention_class_id = fields.Many2one("fix.retention.class", required=True, ondelete="restrict")
    cutoff_on = fields.Date(
        string="Retention Expired On or Before", required=True, default=fields.Date.context_today
    )
    method = fields.Selection(
        [
            ("secure_wipe", "Secure Wipe"),
            ("physical_shredding", "Physical Shredding"),
            ("degaussing", "Degaussing"),
        ],
        default="secure_wipe",
        required=True,
    )
    note = fields.Text()
    state = fields.Selection(
        [
            ("proposed", "Proposed"),
            ("under_review", "Under Review"),
            ("approved", "Approved"),
            ("completed", "Completed"),
            ("failed", "Failed"),
            ("rejected", "Rejected"),
        ],
        default="proposed",
        required=True,
        tracking=True,
    )
    prepared_by_id = fields.Many2one("res.users", readonly=True)
    document_ids = fields.Many2many(
        "fix.document",
        "fix_disposal_batch_document_rel",
        "batch_id",
        "document_id",
        string="Eligible Documents",
        readonly=True,
    )
    excluded_held_ids = fields.Many2many(
        "fix.document",
        "fix_disposal_batch_held_rel",
        "batch_id",
        "document_id",
        string="Excluded (on hold)",
        readonly=True,
    )
    proposed_count = fields.Integer(compute="_compute_counts")
    excluded_held_count = fields.Integer(compute="_compute_counts")
    approved_by_id = fields.Many2one("res.users", readonly=True)
    approved_at = fields.Datetime(readonly=True)
    executed_at = fields.Datetime(readonly=True)
    certificate_doc_id = fields.Many2one("fix.document", string="Batch Certificate", readonly=True)
    outcome_note = fields.Text(readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "prepared_by_id",
            "document_ids",
            "excluded_held_ids",
            "approved_by_id",
            "approved_at",
            "executed_at",
            "certificate_doc_id",
            "outcome_note",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(r.state != "proposed" for r in self):
            locked |= {"retention_class_id", "cutoff_on", "method", "company_id"}
        return locked

    @api.depends("document_ids", "excluded_held_ids")
    def _compute_counts(self):
        for rec in self:
            rec.proposed_count = len(rec.document_ids)
            rec.excluded_held_count = len(rec.excluded_held_ids)

    @api.model_create_multi
    def create(self, vals_list):
        _require(self.env, RECORDS_GROUP, "Preparing a disposal batch")
        records = super().create(vals_list)
        records._guarded().write({"prepared_by_id": self.env.uid})
        records._propose()
        return records

    def write(self, vals):
        if not self._fix_guard_open() and {
            "retention_class_id",
            "cutoff_on",
            "method",
            "company_id",
        } & set(vals):
            if any(r.state != "proposed" for r in self):
                raise UserError("A batch under review or beyond is frozen.")
            result = super().write(vals)
            self._propose()
            return result
        return super().write(vals)

    def _eligible(self):
        self.ensure_one()
        return (
            self.env["fix.document"]
            .sudo()
            .search(
                [
                    ("company_id", "=", self.company_id.id),
                    ("retention_class_id", "=", self.retention_class_id.id),
                    ("state", "in", ("expired", "pending_destruction")),
                    # a hold blanks the retention date (the clock stops), so a held
                    # expired document is matched by its hold to be listed as excluded
                    "|",
                    ("legal_hold", "=", True),
                    ("retention_expires", "<=", self.cutoff_on),
                ]
            )
        )

    def _propose(self):
        for rec in self:
            pool = rec._eligible()
            held = pool.filtered("legal_hold")
            rec._guarded().write(
                {
                    "document_ids": [(6, 0, (pool - held).ids)],
                    "excluded_held_ids": [(6, 0, held.ids)],
                }
            )

    def action_refresh(self):
        for rec in self:
            if rec.state != "proposed":
                raise UserError("Only a proposed batch is recomputed.")
        self._propose()
        return True

    def action_submit(self):
        _require(self.env, RECORDS_GROUP, "Submitting a disposal batch")
        for rec in self:
            if rec.state != "proposed":
                raise UserError("%s is %s." % (rec.name, rec.state))
            rec._propose()
            if not rec.document_ids:
                raise UserError("%s has no eligible document: nothing to approve." % rec.name)
            rec._guarded().write({"state": "under_review"})
            rec.message_post(
                body="Submitted: %d document(s), %d excluded on hold."
                % (rec.proposed_count, rec.excluded_held_count)
            )
        return True

    def action_approve(self):
        _require(self.env, DISPOSAL_APPROVER_GROUP, "Approving a disposal batch")
        for rec in self:
            if rec.state != "under_review":
                raise UserError(
                    "Only a batch under review is approved — %s is %s." % (rec.name, rec.state)
                )
            _not_maker(self.env, rec.prepared_by_id | rec.create_uid, "approve")
            rec._guarded().write(
                {
                    "state": "approved",
                    "approved_by_id": self.env.uid,
                    "approved_at": fields.Datetime.now(),
                }
            )
            rec.message_post(body="Approved by %s." % self.env.user.name)
        return True

    def action_reject(self, reason: str = ""):
        _require(self.env, DISPOSAL_APPROVER_GROUP, "Rejecting a disposal batch")
        if not (reason or "").strip():
            raise UserError("State why the batch is rejected.")
        for rec in self:
            if rec.state != "under_review":
                raise UserError("Only a batch under review is rejected.")
            rec._guarded().write({"state": "rejected", "outcome_note": reason.strip()})
            rec.message_post(body="Rejected by %s: %s" % (self.env.user.name, reason.strip()))
        return True

    def action_execute(self):
        """AUT-DMS-10: the system executes an approved batch all-or-nothing.
        A document held since approval fails the whole batch — partial
        disposal is impossible (§8.3)."""
        _require_any(
            self.env, (RECORDS_GROUP, DISPOSAL_APPROVER_GROUP), "Executing a disposal batch"
        )
        for rec in self:
            if rec.state != "approved":
                raise UserError(
                    "Only an APPROVED batch is executed — %s is %s." % (rec.name, rec.state)
                )
            docs = rec.document_ids.sudo()
            blocked = docs.filtered(
                lambda d: d.legal_hold or d.state not in ("expired", "pending_destruction")
            )
            if blocked:
                rec._guarded().write(
                    {
                        "state": "failed",
                        "outcome_note": "Nothing disposed. Changed since approval (held or no longer "
                        "expired): %s. Prepare a new batch." % ", ".join(blocked.mapped("name")),
                    }
                )
                rec.message_post(body=rec.outcome_note)
                continue
            try:
                with self.env.cr.savepoint():
                    docs.with_user(self.env.user).sudo().with_context(
                        **{BATCH_KEY: _BATCH_TOKEN}
                    ).action_dispose(rec.method)
                    self.env["fix.disposal.record"].sudo().search(
                        [("document_id", "in", docs.ids), ("batch_id", "=", False)]
                    ).write({"batch_id": rec.id})
                    manifest = json.dumps(
                        {
                            "batch": rec.name,
                            "class": rec.retention_class_id.code,
                            "approved_by": rec.approved_by_id.name,
                            "executed_by": self.env.user.name,
                            "documents": [
                                {
                                    "id": d.id,
                                    "name": d.name,
                                    "expired": str(d.retention_expires or ""),
                                }
                                for d in docs
                            ],
                        },
                        sort_keys=True,
                    ).encode("utf-8")
                    certificate = (
                        self.env["fix.document"]
                        .sudo()
                        .attach(
                            name="Disposal Batch Certificate — %s" % rec.name,
                            datas=base64.b64encode(manifest),
                            document_type="destruction_certificate",
                            res_model="fix.disposal.batch",
                            res_id=rec.id,
                        )
                    )
            except Exception as exc:  # roll back the batch, never dispose partially
                self.env.invalidate_all()
                rec._guarded().write(
                    {"state": "failed", "outcome_note": "Rolled back, nothing disposed: %s" % exc}
                )
                rec.message_post(body=rec.outcome_note)
                continue
            rec._guarded().write(
                {
                    "state": "completed",
                    "executed_at": fields.Datetime.now(),
                    "certificate_doc_id": certificate.id,
                    "outcome_note": "%d document(s) disposed." % len(docs),
                }
            )
            rec.message_post(
                body="Executed: %d document(s) disposed, certificate %s."
                % (len(docs), certificate.name)
            )
        return True


class FixDisposalRecordBatch(models.Model):
    _inherit = "fix.disposal.record"

    batch_id = fields.Many2one("fix.disposal.batch", readonly=True, index=True, ondelete="restrict")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"batch_id"}


class FixRetentionViolation(models.Model):
    """FR-DMS-040 / BRU-DMS-19: retained too long, or gone too early. Raised by
    the nightly scan or by a Records Officer; investigated and closed with a
    note."""

    _name = "fix.retention.violation"
    _description = "Retention Violation"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin", "fix.dms.numbered.mixin"]
    _order = "id desc"
    _dms_prefix = "RV"

    name = fields.Char(default="/", readonly=True, copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    document_id = fields.Many2one("fix.document", required=True, ondelete="restrict", index=True)
    retention_class_id = fields.Many2one(related="document_id.retention_class_id", store=True)
    violation_type = fields.Selection(
        [
            ("over_retained", "Retained beyond schedule"),
            ("missing_early", "Missing before schedule"),
        ],
        required=True,
    )
    detected_on = fields.Date(default=fields.Date.context_today, readonly=True)
    raised_by = fields.Selection(
        [("scan", "Nightly scan"), ("manual", "Records Officer")], default="manual", readonly=True
    )
    detail = fields.Text(required=True)
    state = fields.Selection(
        [("open", "Open"), ("investigating", "Investigating"), ("closed", "Closed")],
        default="open",
        required=True,
        tracking=True,
    )
    investigation_note = fields.Text(readonly=True)
    closed_by_id = fields.Many2one("res.users", readonly=True)
    closed_on = fields.Date(readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "investigation_note",
            "closed_by_id",
            "closed_on",
            "raised_by",
            "detected_on",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self:
            locked |= {"document_id", "violation_type"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        _require(self.env, RECORDS_GROUP, "Raising a retention violation")
        return super().create(vals_list)

    def action_investigate(self, note: str = ""):
        _require(self.env, RECORDS_GROUP, "Investigating a retention violation")
        if not (note or "").strip():
            raise UserError("Record what the investigation is looking at.")
        for rec in self:
            if rec.state != "open":
                raise UserError("%s is %s." % (rec.name, rec.state))
            rec._guarded().write({"state": "investigating", "investigation_note": note.strip()})
        return True

    def action_close(self, note: str = ""):
        _require(self.env, RECORDS_GROUP, "Closing a retention violation")
        if not (note or "").strip():
            raise UserError("Record the cause and what was done (BRU-DMS-19).")
        for rec in self:
            if rec.state == "closed":
                raise UserError("%s is already closed." % rec.name)
            prior = rec.investigation_note or ""
            rec._guarded().write(
                {
                    "state": "closed",
                    "investigation_note": (prior + "\n" if prior else "")
                    + "Closed: "
                    + note.strip(),
                    "closed_by_id": self.env.uid,
                    "closed_on": fields.Date.context_today(rec),
                }
            )
        return True

    @api.model
    def cron_retention_scan(self):
        """AUT-DMS-11: both directions. Over-retained: expired, unheld and not
        disposed long after its date. Missing early: archived or emptied while
        its retention still runs, with no disposal on the register."""
        Doc = self.env["fix.document"].sudo().with_context(active_test=False)
        today = fields.Date.today()
        grace = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(PARAM_OVER_RETENTION_GRACE, DEFAULT_OVER_RETENTION_GRACE)
        )
        found = []
        for doc in Doc.search(
            [
                ("state", "in", ("expired", "pending_destruction")),
                ("legal_hold", "=", False),
                ("retention_expires", "!=", False),
                ("retention_expires", "<", today - timedelta(days=grace)),
            ]
        ):
            found.append(
                (
                    doc,
                    "over_retained",
                    "Retention ran on %s; not disposed after %d days."
                    % (doc.retention_expires, grace),
                )
            )
        disposed = set(self.env["fix.disposal.record"].sudo().search([]).mapped("document_id").ids)
        for doc in Doc.search([("state", "!=", "destroyed")]):
            if doc.id in disposed:
                continue
            running = not doc.retention_expires or doc.retention_expires > today
            if not running:
                continue
            if not doc.active:
                found.append(
                    (
                        doc,
                        "missing_early",
                        "Archived while its retention runs (until %s)."
                        % (doc.retention_expires or "open-ended"),
                    )
                )
            elif not doc.attachment_id or not doc.attachment_id.file_size:
                found.append((doc, "missing_early", "Its file is gone while its retention runs."))
        made = 0
        for doc, vtype, detail in found:
            if self.sudo().search_count(
                [
                    ("document_id", "=", doc.id),
                    ("violation_type", "=", vtype),
                    ("state", "!=", "closed"),
                ]
            ):
                continue
            self.sudo().create(
                {
                    "company_id": doc.company_id.id,
                    "document_id": doc.id,
                    "violation_type": vtype,
                    "detail": detail,
                }
            )._guarded().write({"raised_by": "scan"})
            made += 1
        return made


class FixLegalHoldOrder(models.Model):
    """FR-DMS-036/037: a hold over a SCOPE — a class, a type, one business
    object, a filing period — placed on every matching document at once
    (all or nothing) and on every matching document filed while it is in
    force. Released matter by matter, with the authority recorded."""

    _name = "fix.legal.hold.order"
    _description = "Legal Hold Order (scoped)"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin", "fix.dms.numbered.mixin"]
    _order = "id desc"
    _dms_prefix = "HOLD"

    name = fields.Char(default="/", readonly=True, copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    matter_ref = fields.Char(required=True, tracking=True, help="Case, notice or inquiry.")
    instructed_by = fields.Char(
        required=True, help="By whose instruction: counsel, regulator, the GRC matter owner."
    )
    instruction_ref = fields.Char(string="Instruction Reference")
    instructed_on = fields.Date(required=True, default=fields.Date.context_today)
    scope_retention_class_id = fields.Many2one(
        "fix.retention.class", string="Scope: Retention Class"
    )
    scope_document_type = fields.Selection(
        selection=_doc_type_selection, string="Scope: Document Type"
    )
    scope_res_model = fields.Char(string="Scope: Business Object Model")
    scope_res_id = fields.Integer(string="Scope: Business Object ID")
    scope_date_from = fields.Date(string="Scope: Filed From")
    scope_date_to = fields.Date(string="Scope: Filed To")
    state = fields.Selection(
        [("draft", "Draft"), ("applied", "In Force"), ("released", "Released")],
        default="draft",
        required=True,
        tracking=True,
    )
    applied_by_id = fields.Many2one("res.users", readonly=True)
    applied_on = fields.Date(readonly=True)
    hold_ids = fields.One2many("fix.legal.hold", "order_id", readonly=True)
    document_count = fields.Integer(compute="_compute_count")
    released_by_id = fields.Many2one("res.users", readonly=True)
    released_on = fields.Date(readonly=True)
    release_reason = fields.Text(readonly=True)

    _SCOPE = (
        "scope_retention_class_id",
        "scope_document_type",
        "scope_res_model",
        "scope_res_id",
        "scope_date_from",
        "scope_date_to",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "applied_by_id",
            "applied_on",
            "released_by_id",
            "released_on",
            "release_reason",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(r.state != "draft" for r in self):
            locked |= set(self._SCOPE) | {
                "matter_ref",
                "instructed_by",
                "instruction_ref",
                "instructed_on",
                "company_id",
            }
        return locked

    def write(self, vals):
        frozen = (set(self._SCOPE) | {"matter_ref", "instructed_by"}) & set(vals)
        if frozen and not self._fix_guard_open() and any(r.state != "draft" for r in self):
            raise UserError("A hold in force keeps the scope and matter it was applied with.")
        return super().write(vals)

    @api.depends("hold_ids.state")
    def _compute_count(self):
        for rec in self:
            rec.document_count = len(rec.hold_ids.filtered(lambda h: h.state == "held"))

    def _domain(self):
        self.ensure_one()
        dom = [("company_id", "=", self.company_id.id), ("state", "!=", "destroyed")]
        if self.scope_retention_class_id:
            dom.append(("retention_class_id", "=", self.scope_retention_class_id.id))
        if self.scope_document_type:
            dom.append(("document_type", "=", self.scope_document_type))
        if self.scope_res_model:
            dom.append(("res_model", "=", self.scope_res_model))
        if self.scope_res_id:
            dom.append(("res_id", "=", self.scope_res_id))
        if self.scope_date_from:
            dom.append(("create_date", ">=", fields.Datetime.to_datetime(self.scope_date_from)))
        if self.scope_date_to:
            dom.append(
                (
                    "create_date",
                    "<",
                    fields.Datetime.to_datetime(self.scope_date_to) + timedelta(days=1),
                )
            )
        return dom

    def _matches(self, doc):
        self.ensure_one()
        return bool(doc.filtered_domain(self._domain()))

    def _hold_documents(self, docs):
        """Place this matter's hold on each document. A document already held
        under another matter gets this matter's register row too, so it stays
        held until every matter is released."""
        self.ensure_one()
        Hold = self.env["fix.legal.hold"].sudo()
        for doc in docs:
            if Hold.search_count(
                [("order_id", "=", self.id), ("document_id", "=", doc.id), ("state", "=", "held")]
            ):
                continue
            if not doc.legal_hold:
                doc.sudo()._guarded().write(
                    {"legal_hold": True, "legal_hold_reason": self.matter_ref}
                )
            Hold.create(
                {
                    "document_id": doc.id,
                    "order_id": self.id,
                    "matter_ref": self.matter_ref,
                    "placed_by_id": self.applied_by_id.id or self.env.uid,
                    "placed_on": fields.Date.context_today(self),
                }
            )
            doc.sudo().message_post(body="Held under %s (%s)." % (self.matter_ref, self.name))

    def action_apply(self):
        _require(self.env, RECORDS_GROUP, "Placing a legal hold")
        for rec in self:
            if rec.state != "draft":
                raise UserError("%s is already %s." % (rec.name, rec.state))
            if not any(rec[f] for f in self._SCOPE):
                raise UserError(
                    "Define the scope (class, type, business object or filing period): a hold "
                    "over everything is not a scope."
                )
            rec._guarded().write(
                {
                    "state": "applied",
                    "applied_by_id": self.env.uid,
                    "applied_on": fields.Date.context_today(rec),
                }
            )
            docs = self.env["fix.document"].sudo().search(rec._domain())
            rec._hold_documents(docs)
            rec.message_post(body="In force over %d document(s)." % len(docs))
        return True

    def action_release(self, reason: str = ""):
        _require(self.env, RECORDS_GROUP, "Releasing a legal hold")
        if not (reason or "").strip():
            raise UserError("State the authority and reason for the release (FR-DMS-037).")
        for rec in self:
            if rec.state != "applied":
                raise UserError("%s is not in force." % rec.name)
            for hold in rec.hold_ids.filtered(lambda h: h.state == "held"):
                hold._release_one(reason)
            rec._guarded().write(
                {
                    "state": "released",
                    "released_by_id": self.env.uid,
                    "released_on": fields.Date.context_today(rec),
                    "release_reason": reason.strip(),
                }
            )
        return True


class FixLegalHoldMatter(models.Model):
    _inherit = "fix.legal.hold"

    order_id = fields.Many2one(
        "fix.legal.hold.order", string="Hold Order", readonly=True, index=True, ondelete="restrict"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"order_id"}

    def _release_one(self, reason):
        """Release this register row; the document stays held while any other
        matter still holds it (BRU-DMS-04)."""
        self.ensure_one()
        today = fields.Date.context_today(self)
        self.sudo()._guarded().write(
            {
                "state": "released",
                "released_by_id": self.env.uid,
                "released_on": today,
                "release_reason": reason.strip(),
            }
        )
        doc = self.document_id.sudo()
        others = self.sudo().search([("document_id", "=", doc.id), ("state", "=", "held")])
        if others:
            doc._guarded().write({"legal_hold_reason": others[0].matter_ref})
        else:
            doc._guarded().write({"legal_hold": False, "legal_hold_reason": False})
        doc.message_post(
            body="Hold %s released by %s: %s"
            % (self.matter_ref, self.env.user.name, reason.strip())
        )

    def action_release(self, reason: str = ""):
        """Release this matter only (the register row), not every hold the
        document carries."""
        _require(self.env, RECORDS_GROUP, "Releasing a legal hold")
        if not (reason or "").strip():
            raise UserError("State why the hold is released — the release is part of the record.")
        for rec in self:
            if rec.state != "held":
                raise UserError("Hold %s was already released." % rec.matter_ref)
            rec._release_one(reason)
        return True


# =============================================================== page 7
PACK_PURPOSES = [
    ("claim", "Warranty / insurance claim"),
    ("audit", "Audit"),
    ("dispute", "Customer dispute"),
    ("regulatory", "Regulatory request"),
]


class FixEvidencePack(models.Model):
    """FR-DMS-041 / AUT-DMS-15: documents about one subject, checked against
    the composition the purpose needs, sealed with a hash over a manifest of
    their fingerprints. An incomplete pack says so and names what is missing
    (AC-11) — never silently partial."""

    _name = "fix.evidence.pack"
    _description = "Evidence Pack"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin", "fix.dms.numbered.mixin"]
    _order = "id desc"
    _dms_prefix = "EVP"

    name = fields.Char(default="/", readonly=True, copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    purpose = fields.Selection(PACK_PURPOSES, required=True)
    subject_label = fields.Char(
        string="Subject", required=True, help="e.g. Claim WC-0012, ISO surveillance audit 2026"
    )
    subject_model = fields.Char(string="Subject Model", help="e.g. fix.warranty.claim")
    subject_id = fields.Integer(string="Subject Record ID")
    requested_by_id = fields.Many2one(
        "res.users", readonly=True, default=lambda self: self.env.user
    )
    requirement_ids = fields.One2many(
        "fix.evidence.pack.requirement", "pack_id", string="Required Composition"
    )
    document_ids = fields.Many2many(
        "fix.document",
        "fix_evidence_pack_document_rel",
        "pack_id",
        "document_id",
        string="Documents",
    )
    state = fields.Selection(
        [("draft", "Draft"), ("sealed", "Sealed")], default="draft", required=True, tracking=True
    )
    completeness_state = fields.Selection(
        [("complete", "Complete"), ("incomplete", "Incomplete")], readonly=True
    )
    missing_items = fields.Text(readonly=True)
    manifest_json = fields.Text(readonly=True)
    sealed_hash = fields.Char(readonly=True)
    manifest_doc_id = fields.Many2one("fix.document", string="Manifest", readonly=True)
    assembled_at = fields.Datetime(readonly=True)
    assembly_seconds = fields.Integer(
        readonly=True, help="KPI-C24-04: request to seal, target under 5 minutes."
    )
    verified_at = fields.Datetime(readonly=True)
    verification_result = fields.Selection(
        [("intact", "Intact"), ("broken", "Broken")], readonly=True
    )

    _SEALED = {
        "document_ids",
        "requirement_ids",
        "purpose",
        "subject_label",
        "subject_model",
        "subject_id",
        "company_id",
    }

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "completeness_state",
            "missing_items",
            "manifest_json",
            "sealed_hash",
            "manifest_doc_id",
            "assembled_at",
            "assembly_seconds",
            "verified_at",
            "verification_result",
            "requested_by_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(r.state != "draft" for r in self):
            locked |= self._SEALED
        return locked

    def write(self, vals):
        sealed = self._SEALED & set(vals) and any(r.state != "draft" for r in self)
        if sealed and not self._fix_guard_open():
            raise UserError("A sealed pack is evidence: assemble a new one.")
        return super().write(vals)

    def action_collect(self):
        """Add every filed document linked to the subject record."""
        for rec in self:
            if rec.state != "draft":
                raise UserError("%s is sealed." % rec.name)
            if not (rec.subject_model and rec.subject_id):
                raise UserError("Name the subject model and record to collect from.")
            docs = self.env["fix.document"].search(
                [
                    ("res_model", "=", rec.subject_model),
                    ("res_id", "=", rec.subject_id),
                    ("state", "!=", "destroyed"),
                ]
            )
            rec.write({"document_ids": [(4, d.id) for d in docs]})
            rec.message_post(body="%d document(s) collected from the subject." % len(docs))
        return True

    def _manifest(self):
        self.ensure_one()
        return [
            {
                "id": d.id,
                "name": d.name,
                "type": d.document_type,
                "version": d.version,
                "sha256": d.sudo().checksum_sha256 or hashlib.sha256(_bytes_of(d)).hexdigest(),
            }
            for d in self.document_ids.sorted("id")
        ]

    def action_assemble(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("%s is already sealed." % rec.name)
            if not rec.document_ids:
                raise UserError("A pack needs at least one document.")
            destroyed = rec.document_ids.filtered(lambda d: d.state == "destroyed")
            if destroyed:
                raise UserError(
                    "Disposed documents cannot be evidence: %s."
                    % ", ".join(destroyed.mapped("name"))
                )
            labels = dict(self.env["fix.document"]._fields["document_type"].selection)
            missing = []
            for req in rec.requirement_ids:
                have = len(
                    rec.document_ids.filtered(lambda d, t=req.document_type: d.document_type == t)
                )
                if have < (req.min_count or 1):
                    missing.append(
                        "%s: %d of %d"
                        % (
                            labels.get(req.document_type, req.document_type),
                            have,
                            req.min_count or 1,
                        )
                    )
            manifest = {
                "pack": rec.name,
                "purpose": rec.purpose,
                "subject": rec.subject_label,
                "subject_ref": "%s,%s" % (rec.subject_model or "", rec.subject_id or ""),
                "documents": rec._manifest(),
                "missing": missing,
            }
            body = json.dumps(manifest, sort_keys=True, ensure_ascii=False)
            sealed = hashlib.sha256(body.encode("utf-8")).hexdigest()
            manifest_doc = (
                self.env["fix.document"]
                .sudo()
                .attach(
                    name="Evidence Pack Manifest — %s" % rec.name,
                    datas=base64.b64encode(body.encode("utf-8")),
                    document_type="evidence_pack",
                    res_model="fix.evidence.pack",
                    res_id=rec.id,
                )
            )
            now = fields.Datetime.now()
            rec._guarded().write(
                {
                    "state": "sealed",
                    "completeness_state": "incomplete" if missing else "complete",
                    "missing_items": "\n".join(missing) or False,
                    "manifest_json": body,
                    "sealed_hash": sealed,
                    "manifest_doc_id": manifest_doc.id,
                    "assembled_at": now,
                    "assembly_seconds": int((now - rec.create_date).total_seconds())
                    if rec.create_date
                    else 0,
                }
            )
            rec.message_post(
                body="Sealed (%s) — hash %s%s"
                % (
                    "INCOMPLETE" if missing else "complete",
                    sealed,
                    "; missing: " + "; ".join(missing) if missing else "",
                )
            )
        return True

    def action_verify(self):
        """Re-hash the documents against the sealed manifest."""
        for rec in self:
            if rec.state != "sealed":
                raise UserError("Only a sealed pack is verified.")
            stored = json.loads(rec.manifest_json or "{}")
            ok = (
                hashlib.sha256((rec.manifest_json or "").encode("utf-8")).hexdigest()
                == rec.sealed_hash
            )
            if ok:
                for item in stored.get("documents", []):
                    doc = (
                        self.env["fix.document"]
                        .sudo()
                        .with_context(active_test=False)
                        .browse(item["id"])
                        .exists()
                    )
                    if not doc or hashlib.sha256(_bytes_of(doc)).hexdigest() != item["sha256"]:
                        ok = False
                        break
            rec._guarded().write(
                {
                    "verified_at": fields.Datetime.now(),
                    "verification_result": "intact" if ok else "broken",
                }
            )
            rec.message_post(
                body="Verification: %s."
                % ("intact" if ok else "BROKEN — a document changed or is gone")
            )
        return True


class FixEvidencePackRequirement(models.Model):
    _name = "fix.evidence.pack.requirement"
    _description = "Evidence Pack Required Item"

    pack_id = fields.Many2one("fix.evidence.pack", required=True, ondelete="cascade", index=True)
    document_type = fields.Selection(selection=_doc_type_selection, required=True)
    min_count = fields.Integer(string="At Least", default=1)
    note = fields.Char()

    def _check_open(self):
        if not self.env.su and any(r.pack_id.state != "draft" for r in self):
            raise UserError("A sealed pack's composition is evidence.")

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._check_open()
        return records

    def write(self, vals):
        self._check_open()
        return super().write(vals)

    def unlink(self):
        self._check_open()
        return super().unlink()


class FixExternalRelease(models.Model):
    """FR-DMS-042 / BRU-DMS-13 (the registry's "Share Token"): a scoped,
    approved, time-boxed release to an outside party. The link works only
    while granted and unexpired; every access is logged; PDFs and images are
    watermarked with the release on each copy served."""

    _name = "fix.external.release"
    _description = "Controlled External Release"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin", "fix.dms.numbered.mixin"]
    _order = "id desc"
    _dms_prefix = "REL"

    name = fields.Char(default="/", readonly=True, copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    partner_id = fields.Many2one("res.partner", string="External Party", required=True)
    purpose = fields.Text(required=True)
    pack_id = fields.Many2one("fix.evidence.pack", string="Evidence Pack", ondelete="restrict")
    document_ids = fields.Many2many(
        "fix.document",
        "fix_external_release_document_rel",
        "release_id",
        "document_id",
        string="Documents",
    )
    expires_on = fields.Date(required=True)
    watermark = fields.Boolean(default=True, help="Stamp each served PDF/image with the release.")
    requested_by_id = fields.Many2one(
        "res.users", readonly=True, default=lambda self: self.env.user
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("requested", "Awaiting Approval"),
            ("granted", "Granted"),
            ("expired", "Expired"),
            ("revoked", "Revoked"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    approved_by_id = fields.Many2one("res.users", readonly=True)
    granted_at = fields.Datetime(readonly=True)
    access_token = fields.Char(readonly=True, copy=False, index=True, groups="base.group_user")
    access_url = fields.Char(compute="_compute_url")
    revoked_by_id = fields.Many2one("res.users", readonly=True)
    revoked_at = fields.Datetime(readonly=True)
    revoke_reason = fields.Text(readonly=True)
    access_log_ids = fields.One2many("fix.document.access.log", "release_id", readonly=True)
    access_count = fields.Integer(compute="_compute_access")

    _SCOPE = {"partner_id", "pack_id", "document_ids", "expires_on", "watermark", "company_id"}

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "approved_by_id",
            "granted_at",
            "access_token",
            "revoked_by_id",
            "revoked_at",
            "revoke_reason",
            "requested_by_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(r.state != "draft" for r in self):
            locked |= self._SCOPE | {"purpose"}
        return locked

    def write(self, vals):
        scoped = (self._SCOPE | {"purpose"}) & set(vals)
        if scoped and not self._fix_guard_open() and any(r.state != "draft" for r in self):
            raise UserError("A requested release keeps the scope it was approved on.")
        return super().write(vals)

    @api.depends("access_token", "state")
    def _compute_url(self):
        base = self.env["ir.config_parameter"].sudo().get_param("web.base.url", "")
        for rec in self:
            token = rec.sudo().access_token
            rec.access_url = (
                "%s/dms/release/%s" % (base, token) if token and rec.state == "granted" else False
            )

    @api.depends("access_log_ids")
    def _compute_access(self):
        for rec in self:
            rec.access_count = len(rec.access_log_ids)

    def _released_documents(self):
        self.ensure_one()
        return (
            self.pack_id.document_ids | self.pack_id.manifest_doc_id | self.document_ids
        ).filtered(lambda d: d.state != "destroyed")

    def _check_scope(self):
        max_days = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(PARAM_RELEASE_MAX_DAYS, DEFAULT_RELEASE_MAX_DAYS)
        )
        today = fields.Date.context_today(self)
        for rec in self:
            if not (rec.pack_id or rec.document_ids):
                raise UserError("Scope the release: an evidence pack or named documents.")
            if rec.pack_id and rec.pack_id.state != "sealed":
                raise UserError("Only a SEALED evidence pack is released.")
            if not rec.expires_on or rec.expires_on <= today:
                raise UserError("The release must expire in the future.")
            if rec.expires_on > today + timedelta(days=max_days):
                raise UserError(
                    "A release lasts at most %d days (%s); this one runs to %s."
                    % (max_days, PARAM_RELEASE_MAX_DAYS, rec.expires_on)
                )
            t5 = rec.sudo()._released_documents().filtered(lambda d: d.isolation_tier == "T5")
            if t5:
                raise UserError(
                    "T5 documents need a named allow-list and step-up access; they are not released "
                    "by link: %s." % ", ".join(t5.mapped("name"))
                )

    def action_request(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("%s is %s." % (rec.name, rec.state))
            rec._check_scope()
            rec._guarded().write({"state": "requested"})
        return True

    def action_grant(self):
        _require_any(self.env, (RECORDS_GROUP, CONTROLLER_GROUP), "Approving an external release")
        for rec in self:
            if rec.state != "requested":
                raise UserError(
                    "Only a requested release is approved — %s is %s." % (rec.name, rec.state)
                )
            _not_maker(self.env, rec.requested_by_id | rec.create_uid, "approve")
            rec._check_scope()
            rec._guarded().write(
                {
                    "state": "granted",
                    "approved_by_id": self.env.uid,
                    "granted_at": fields.Datetime.now(),
                    "access_token": secrets.token_urlsafe(32),
                }
            )
            self.env["fix.document.access.log"].sudo().create(
                [
                    {
                        "document_id": d.id,
                        "release_id": rec.id,
                        "action": "release",
                        "actor_id": self.env.uid,
                        "external_party_id": rec.partner_id.id,
                        "purpose": rec.purpose,
                    }
                    for d in rec.sudo()._released_documents()
                ]
            )
            rec.message_post(body="Granted by %s until %s." % (self.env.user.name, rec.expires_on))
        return True

    def action_revoke(self, reason: str = ""):
        if not (reason or "").strip():
            raise UserError("State why the release is revoked.")
        for rec in self:
            if not (
                self.env.su
                or self.env.user.has_group(RECORDS_GROUP)
                or self.env.user == rec.requested_by_id
            ):
                raise AccessError("A release is revoked by its requester or a Records Officer.")
            if rec.state not in ("requested", "granted"):
                raise UserError("%s is %s." % (rec.name, rec.state))
            rec._guarded().write(
                {
                    "state": "revoked",
                    "revoked_by_id": self.env.uid,
                    "revoked_at": fields.Datetime.now(),
                    "revoke_reason": reason.strip(),
                    "access_token": False,
                }
            )
        return True

    @api.model
    def cron_expire_releases(self):
        """AUT-DMS-17: access ends by itself at expiry."""
        today = fields.Date.today()
        stale = self.sudo().search([("state", "=", "granted"), ("expires_on", "<", today)])
        for rec in stale:
            rec._guarded().write({"state": "expired", "access_token": False})
            rec.message_post(
                body="Expired on %s: %d access(es) were made." % (rec.expires_on, rec.access_count)
            )
        return len(stale)

    @api.model
    def _resolve_token(self, token):
        """The public route's one lookup (sudo): a granted, unexpired release."""
        if not token or len(token) < 20:
            return self.browse()
        rec = self.sudo().search([("access_token", "=", token), ("state", "=", "granted")], limit=1)
        if rec and rec.expires_on < fields.Date.context_today(rec):
            return self.browse()
        return rec


class FixDocumentAccessLog(models.Model):
    """T-11 / BRU-DMS-12: who read what, when, from where, and under which
    release. Written by the system only."""

    _name = "fix.document.access.log"
    _description = "Document Access Log"
    _order = "id desc"

    document_id = fields.Many2one("fix.document", required=True, ondelete="restrict", index=True)
    release_id = fields.Many2one("fix.external.release", ondelete="restrict", index=True)
    actor_id = fields.Many2one("res.users", string="Actor")
    external_party_id = fields.Many2one("res.partner")
    action = fields.Selection(
        [("view", "View"), ("download", "Download"), ("print", "Print"), ("release", "Release")],
        required=True,
    )
    at = fields.Datetime(default=fields.Datetime.now, required=True)
    ip_or_device = fields.Char()
    purpose = fields.Char()

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.su:
            raise AccessError("The access log is written by the system only.")
        return super().create(vals_list)

    def write(self, vals):
        raise UserError("The access log is append-only.")

    def unlink(self):
        raise UserError("The access log is append-only.")
