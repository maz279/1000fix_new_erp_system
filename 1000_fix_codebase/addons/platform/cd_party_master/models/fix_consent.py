# fix.consent — the consent registry (P03-M05, M33; NT-002 companion).
# Marketing consent and channel preferences are AUDITABLE obligations, not
# profile conveniences: every grant, withdrawal and proof lives here with its
# dates. The notification dispatcher's RecipientState is the projection of
# this table — never a separate source of truth.
#
# M33 rebuild (2026-10-27), per spec BRU-CPM-08 / T-09:
#  - a GRANT is invalid without the transparency-notice version presented;
#  - withdrawal is APPEND-ONLY: the granted row is never rewritten to look
#    withdrawn — a NEW withdrawn record supersedes it and both stay forever.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

# What a consent row SAYS. Captured once; a later change is a new row.
_CONSENT_DECISION_FIELDS = {
    "purpose",
    "channel",
    "date_granted",
    "notice_version_id",
    "wording_hash",
    "proof",
    "source",
}


class FixConsent(models.Model):
    """One consent decision: what was consented, for which purpose, on which
    channel, when, against which notice version, and with what proof."""

    _name = "fix.consent"
    _description = "Consent Record"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "partner_id, purpose, channel, date_granted desc"

    def _fix_guarded_fields(self) -> set:
        # The append-only rule was a comment: rewriting a withdrawn row to
        # 'granted' turned consent_check from refused to allowed (A03 audit).
        # Under the GDPR Art. 7 / PDPO 2025 burden of proof, a consent row the
        # business can edit proves nothing.
        return super()._fix_guarded_fields() | {
            "state",
            "date_withdrawn",
            "supersedes_id",
            "superseded_by_id",
        }

    def _fix_form_locked_fields(self) -> set:
        # Captured once: on an existing row the decision fields are history.
        locked = super()._fix_form_locked_fields()
        return locked | _CONSENT_DECISION_FIELDS if self else locked

    def write(self, vals):
        if not self._fix_guard_open():
            changed = {
                name
                for rec in self
                for name in _CONSENT_DECISION_FIELDS & set(vals)
                if rec._fix_guard_differs(name, vals[name], rec[name])
            }
            if changed:
                raise UserError(
                    "A consent record cannot be edited once captured (%s). Record "
                    "a new consent, or withdraw this one." % ", ".join(sorted(changed))
                )
        return super().write(vals)

    partner_id = fields.Many2one(
        "res.partner", string="Party", required=True, ondelete="cascade", index=True
    )
    purpose = fields.Selection(
        [
            ("service_updates", "Service Updates"),
            ("marketing", "Marketing"),
            ("research", "Research & Analytics"),
            ("collections", "Debt Collection"),
            ("profiling", "Profiling"),
            ("call_recording", "Call Recording"),
        ],
        string="Purpose",
        required=True,
        default="marketing",
        tracking=True,
        help="PDPA: consent attaches to a PROCESSING PURPOSE, not a profile",
    )
    channel = fields.Selection(
        [
            ("sms", "SMS"),
            ("whatsapp", "WhatsApp"),
            ("email", "Email"),
            ("push", "Push"),
            ("voice", "Voice Call"),
            ("marketing", "Marketing (all channels)"),
        ],
        string="Channel",
        required=True,
    )
    state = fields.Selection(
        [
            ("granted", "Granted"),
            ("withdrawn", "Withdrawn"),
            ("superseded", "Superseded (withdrawn later)"),
            ("expired", "Expired"),
        ],
        string="State",
        required=True,
        default="granted",
        tracking=True,
    )
    date_granted = fields.Datetime(string="Granted At", default=fields.Datetime.now)
    date_withdrawn = fields.Datetime(string="Withdrawn At", readonly=True)
    # BRU-CPM-08: the notice version PRESENTED at capture — without it the
    # consent is not valid consent.
    notice_version_id = fields.Many2one(
        "fix.transparency.notice",
        string="Notice Version",
        tracking=True,
        help="The transparency-notice version shown when this consent was "
        "captured; a grant without it is invalid (BRU-CPM-08)",
    )
    wording_hash = fields.Char(
        string="Wording Hash",
        help="Hash of the exact wording accepted, for dispute evidence",
    )
    # T-09 append-only chain: a withdrawal record points at the grant it
    # supersedes; the grant points back at its withdrawal.
    supersedes_id = fields.Many2one(
        "fix.consent",
        string="Supersedes",
        readonly=True,
        index=True,
        help="The granted record this withdrawal supersedes (append-only chain)",
    )
    superseded_by_id = fields.Many2one(
        "fix.consent",
        string="Superseded By",
        readonly=True,
        index=True,
    )
    proof = fields.Char(
        string="Proof Reference",
        help="Where the consent came from: signed form ID, "
        "OTP-verified session, legacy import batch — "
        "an unverifiable grant is not a grant",
    )
    source = fields.Selection(
        [
            ("web", "Web Portal"),
            ("otp", "OTP-Verified"),
            ("form", "Paper Form"),
            ("legacy", "Legacy Import"),
            ("agent", "Agent Captured"),
        ],
        string="Source",
        default="web",
    )
    company_id = fields.Many2one(
        "res.company", string="Company", required=True, default=lambda self: self.env.company
    )

    def action_withdraw(self):
        """Withdraw today by APPENDING a new record — the original grant keeps
        its exact captured state (marked superseded by link, never rewritten),
        so the auditable trail outlives the account (BTRC/DND + PDPA T-09)."""
        for consent in self:
            if consent.state != "granted":
                raise ValidationError(
                    "Only a granted consent can be withdrawn — this record is %s" % consent.state
                )
            withdrawal = self._guarded().create(
                {
                    "partner_id": consent.partner_id.id,
                    "purpose": consent.purpose,
                    "channel": consent.channel,
                    "state": "withdrawn",
                    "date_granted": consent.date_granted,
                    "date_withdrawn": fields.Datetime.now(),
                    "notice_version_id": consent.notice_version_id.id,
                    "supersedes_id": consent.id,
                    "source": consent.source,
                    "proof": consent.proof,
                    "company_id": consent.company_id.id,
                }
            )
            consent._guarded().write({"superseded_by_id": withdrawal.id, "state": "superseded"})
            self._emit_consent_event("consent.withdrawn", withdrawal)
            # AUT-CPM-06: the withdrawal is recorded in the processing record
            self.env["fix.processing.record"]._record_from_consent(withdrawal, "consent_withdrawal")
        return True

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if rec.state == "granted":
                self._emit_consent_event("consent.captured", rec)
                self.env["fix.processing.record"]._record_from_consent(rec, "consent_capture")
        return records

    def _emit_consent_event(self, event_type: str, rec) -> None:
        from libs.py.fix_events import publish

        publish(
            self.env,
            event_type,
            "res.partner",
            rec.partner_id.id,
            {
                "purpose": rec.purpose,
                "channel": rec.channel,
                "state": rec.state,
                "notice_version": rec.notice_version_id.version or None,
            },
        )

    @api.constrains("state", "proof", "notice_version_id")
    def _check_proof_and_notice_on_grant(self):
        for consent in self:
            if consent.state != "granted":
                continue
            if not consent.proof:
                raise ValidationError(
                    "A granted consent needs its proof reference — "
                    "an unverifiable grant is not a grant"
                )
            if not consent.notice_version_id:
                raise ValidationError(
                    "A granted consent must record the transparency-notice version "
                    "presented at capture (BRU-CPM-08) — consent without a notice "
                    "version is not valid consent"
                )
