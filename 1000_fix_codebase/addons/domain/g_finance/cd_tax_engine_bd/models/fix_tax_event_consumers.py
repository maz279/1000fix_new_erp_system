# cd_tax_engine_bd — M51-F10 (A08, 2026-11): the tax events reach the risk and
# compliance registers.
#
# M51 publishes its domain events (vat_return.prepared/filed/filed_online,
# mushak.registered, tax_challan.deposited, withholding_certificate.issued,
# vat_subledger.reconciled/variance_detected, vat_return.amended, and — since
# this change — tax.notice.overdue from the deadline cron), but NOTHING outside
# the module consumed them: a sub-ledger variance, an overdue NBR notice and a
# filed 9.1 all stopped at the outbox, so the board's M60 risk view and the
# compliance register held none of them (spec 12.2/12.3 name M23/M60 as the
# consumers).
#
# The consumers are declared in THIS module (data/fix_tax_event_consumers.xml)
# and write to the registers READ-ONLY through the event relay: one OPEN
# fix.risk.register entry per variance / per notice (the risk function scores
# and closes it), and the filed return's NBR acknowledgement evidences and
# discharges the period's fix.compliance.obligation.occurrence (BRU-GRC-12: an
# evidenced discharge, never a bare tick). When the GRC stack is not installed
# the consumers no-op with a reason instead of dead-lettering the event.
#
# Every consumer is idempotent (the relay may redeliver): the risk entries are
# found by their name and never duplicated, and a discharged occurrence is no
# longer 'scheduled' so a replay discharges nothing.
from odoo import api, models
from odoo.exceptions import AccessError

# the compliance register's own convention for the VAT-return obligation (the
# M60 capture suite's fixture names it "Monthly VAT return (Mushak 9.1)")
_VAT_RETURN_OBLIGATION_MARKERS = ("mushak 9.1", "9.1", "vat return")


def _risk_entry(env, name, company, operating_unit, description):
    """Raise (or find) the ONE open M60 entry named `name` for the company.
    A redelivered event finds it; a later variance on the same subject posts
    its figures on the entry instead of opening another."""
    Risk = env["fix.risk.register"].sudo()
    existing = Risk.search([("name", "=", name), ("company_id", "=", company.id)], limit=1)
    if existing:
        existing.message_post(body=description)
        return existing
    return Risk.create(
        {
            "name": name,
            "category": "compliance",
            "company_id": company.id,
            "operating_unit_id": operating_unit.id if operating_unit else False,
            "mitigation": description,
            "state": "open",
        }
    )


class FixVatReturnTaxConsumers(models.Model):
    """M51-F10 consumers on the VAT return: the variance and the filing."""

    _inherit = "fix.vat.return"

    @api.model
    def consume_vat_subledger_variance(self, event):
        """`vat_subledger.variance_detected` (published by
        action_subledger_reconciliation) -> ONE open compliance risk entry on
        the M60 register per company and period. IRB-09: the variance is
        raised, never absorbed — now the board sees it too."""
        if not self.env.su:
            raise AccessError("The tax event consumers run from the event relay only (M51-F10).")
        if "fix.risk.register" not in self.env:
            return {"created": 0, "reason": "fix.risk.register is not installed"}
        ret = self.sudo().browse(int(event.get("aggregate_id") or 0)).exists()
        if not ret:
            return {"created": 0, "reason": "vat return %s is gone" % event.get("aggregate_id")}
        payload = event.get("payload") or {}
        description = (
            "The Mushak 9.1 for %s does not reconcile to the GL: output variance %s, "
            "input variance %s (%s). Filing stays blocked until the register and the GL "
            "agree (IRB-09: a variance is never absorbed). Event %s."
            % (
                ret.period,
                payload.get("output_variance", ret.subledger_output_variance),
                payload.get("input_variance", ret.subledger_input_variance),
                ret.subledger_notes or payload.get("status") or "variance_detected",
                event.get("event_id") or "-",
            )
        )
        return _risk_entry(
            self.env,
            "[M51] VAT sub-ledger variance %s" % ret.period,
            ret.company_id,
            ret.operating_unit_id,
            description,
        )

    @api.model
    def _vat_return_obligation(self, occurrence):
        """True when the occurrence's obligation is the company's VAT-return
        obligation: the compliance function's own naming identifies it (a
        monthly statutory obligation whose name or clause names the Mushak 9.1
        / the VAT return). Nothing is guessed: an obligation the register does
        not so name is not discharged by the tax module."""
        obligation = occurrence.obligation_id.sudo()
        text = ("%s %s" % (obligation.name or "", obligation.clause_reference or "")).lower()
        return getattr(obligation, "recurrence", False) == "monthly" and any(
            marker in text for marker in _VAT_RETURN_OBLIGATION_MARKERS
        )

    @api.model
    def consume_vat_return_filed(self, event):
        """`vat_return.filed` / `vat_return.filed_online` -> the period's
        VAT-return obligation occurrence on the compliance register is
        discharged WITH the NBR acknowledgement as its evidence (BRU-GRC-12).
        A redelivered event meets a discharged occurrence and changes nothing."""
        if not self.env.su:
            raise AccessError("The tax event consumers run from the event relay only (M51-F10).")
        if "fix.compliance.obligation.occurrence" not in self.env:
            return {"discharged": 0, "reason": "the compliance register is not installed"}
        ret = self.sudo().browse(int(event.get("aggregate_id") or 0)).exists()
        if not ret or ret.state != "filed":
            return {
                "discharged": 0,
                "reason": "vat return %s is not filed" % event.get("aggregate_id"),
            }
        payload = event.get("payload") or {}
        ack = str(payload.get("nbr_confirmation") or payload.get("token") or "").strip()
        if not ack:
            # BRU-GRC-12: without the acknowledgement there is no evidence —
            # the discharge stays the compliance officer's recorded decision
            return {"discharged": 0, "reason": "the filing carries no NBR acknowledgement"}
        Occurrence = self.env["fix.compliance.obligation.occurrence"].sudo()
        discharged = Occurrence.browse()
        for occ in Occurrence.search(
            [
                ("company_id", "=", ret.company_id.id),
                ("period", "=", ret.period),
                ("state", "=", "scheduled"),
            ]
        ):
            if not self._vat_return_obligation(occ):
                continue
            occ.write({"evidence_ref": "NBR ack %s (Mushak 9.1 %s)" % (ack, ret.period)})
            occ.action_discharge(
                note="Mushak 9.1 %s filed online; NBR acknowledgement %s (event %s)."
                % (ret.period, ack, event.get("event_id") or "-")
            )
            discharged |= occ
        return {"discharged": len(discharged), "period": ret.period}


class FixTaxNoticeTaxConsumers(models.Model):
    """M51-F10 consumer on the NBR notice: the overdue response reaches M60."""

    _inherit = "fix.tax.notice"

    @api.model
    def consume_notice_overdue(self, event):
        """`tax.notice.overdue` (published by the notice-deadline cron once a
        notice's response date passes unanswered) -> ONE open compliance risk
        entry per notice. The entry is never closed by the source: how the
        notice was answered late is the risk owner's to review."""
        if not self.env.su:
            raise AccessError("The tax event consumers run from the event relay only (M51-F10).")
        if "fix.risk.register" not in self.env:
            return {"created": 0, "reason": "fix.risk.register is not installed"}
        notice = self.sudo().browse(int(event.get("aggregate_id") or 0)).exists()
        if not notice:
            return {"created": 0, "reason": "notice %s is gone" % event.get("aggregate_id")}
        if notice.state != "open":
            return {"created": 0, "reason": "notice %s is %s" % (notice.name, notice.state)}
        payload = event.get("payload") or {}
        description = (
            "The response to NBR notice %s (%s, %s, %s) was due %s and is unanswered; "
            "owner %s; BDT %s in dispute. Event %s."
            % (
                notice.notice_ref,
                notice.name,
                notice.authority or "-",
                dict(notice._fields["tax_kind"].selection).get(notice.tax_kind, notice.tax_kind),
                payload.get("due") or notice.response_due,
                payload.get("owner") or notice.owner_id.name or "-",
                payload.get("disputed_amount", notice.disputed_amount or 0.0),
                event.get("event_id") or "-",
            )
        )
        return _risk_entry(
            self.env,
            "[M51] NBR notice %s (%s) overdue" % (notice.name, notice.notice_ref),
            notice.company_id,
            notice.operating_unit_id,
            description,
        )
