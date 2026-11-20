# M27 notifications for A02 events the specs route to M27 and nobody
# consumed (A02 ERP pass 2, X5-14, 20 Nov 2026).
#
#   sla.instance_near_breach  M01 sla.warning -> M27: the branch's Service
#                             Supervisors are e-mailed before the clock runs
#                             out (the breach consumer only acts afterwards);
#   sla.escalated             M01 fix.escalation.rule: the users the rule
#                             escalated to are e-mailed, not only given a
#                             to-do they may never open;
#   msp.service_report_published
#                             M05 AUT-RMS-10: "publish to the portal; notify
#                             the client contacts" - the client is e-mailed;
#   data_case.evaluated       M06 AUT-DTS-03 / data_case.evaluated -> M27:
#                             the customer is told the evaluation is done;
#   data_case.quote_sent      the quotation is "sent" - but nothing sent it:
#                             the customer now gets its number and amount.
#
# Everything goes through the one exit, fix.notif.delivery.queue(), so the
# consent verdict, the BTRC curfew, the provider and the evidence row apply,
# and one event queues one message per recipient and channel (dedup key).
# Staff notices are English (as the M63 approver notices); customer notices
# are bilingual. M06 messages name the case and the verdict only - never
# anything about the data (M06 confidentiality).
#
# None of the source modules is a dependency of the contact centre: their
# records are read through the registry, as fix_a02_notifications does.
from odoo import api, models
from odoo.exceptions import ValidationError

SUPERVISOR_GROUP = "cd_service_order.group_so_supervisor"

_STAFF = {
    "near_breach": {
        "subject": "SLA at risk: {record}",
        "body": "1000FiX: the {kpi} SLA of {record} is close to breach (target {target}). "
        "Act now to keep it inside its target.",
    },
    "escalated": {
        "subject": "SLA escalation: {record}",
        "body": "1000FiX: {record} reached {elapsed}% of its {kpi} SLA target and was "
        "escalated to you (rule at {threshold}%). It is in your to-do list.",
    },
}

_CUSTOMER = {
    "report": {
        "subject": {
            "en": "Your managed services report for {period}",
            "bn": "{period} মাসের আপনার পরিচালিত সেবা প্রতিবেদন",
        },
        "en": "1000FiX: your managed services report for {period} ({contract}) is published "
        "on the client portal. {summary}",
        "bn": "1000FiX: {period} মাসের ({contract}) পরিচালিত সেবা প্রতিবেদন ক্লায়েন্ট পোর্টালে "
        "প্রকাশিত হয়েছে। {summary}",
    },
    "evaluated": {
        "en": "1000FiX: the evaluation of your data recovery case {case} is complete. "
        "We will send you the quotation; call 16743 with this case number.",
        "bn": "1000FiX: আপনার ডেটা রিকভারি কেস {case}-এর মূল্যায়ন সম্পন্ন হয়েছে। "
        "কোটেশন পাঠানো হবে; এই কেস নম্বরসহ 16743-এ কল করুন।",
    },
    "quote": {
        "en": "1000FiX: quotation {quote} for data recovery case {case} is BDT {amount}. "
        "Visit the branch or call 16743 to accept it.",
        "bn": "1000FiX: ডেটা রিকভারি কেস {case}-এর কোটেশন {quote}: {amount} টাকা। "
        "গ্রহণ করতে শাখায় আসুন অথবা 16743-এ কল করুন।",
    },
}


class FixNotifDeliveryA02r2(models.Model):
    _inherit = "fix.notif.delivery"

    # ------------------------------------------------------------- helpers
    @api.model
    def _a02r2_record(self, model, res_id):
        Model = self.env.get(model) if model else None
        if Model is None or not res_id:
            return None
        try:
            return Model.sudo().browse(int(res_id)).exists() or None
        except (TypeError, ValueError):
            return None

    @api.model
    def _a02r2_email_users(self, event, kind, users, values, record):
        """E-mail each user once per event; a user with no address is
        skipped, not dead-lettered (as the M63 approver notices)."""
        text = _STAFF[kind]
        queued, skipped = 0, []
        for user in users:
            partner = user.partner_id
            if not partner:
                skipped.append("%s: no partner" % user.name)
                continue
            try:
                delivery = self.queue(
                    channel="email",
                    purpose="service_updates",
                    partner=partner,
                    body=text["body"].format(**values),
                    subject=text["subject"].format(**values),
                    lawful_basis="contract",
                    source_model=record._name if record else None,
                    source_id=record.id if record else None,
                    source_event_id=event.get("event_id"),
                    dedup_key="a02r2-%s:%s:%s" % (kind, event.get("event_id") or 0, user.id),
                    company=record.company_id
                    if record and "company_id" in record._fields
                    else None,
                )
            except ValidationError as exc:
                skipped.append("%s: %s" % (user.name, exc))
                continue
            if delivery.state != "suppressed":
                queued += 1
        return {"queued": queued, "skipped": skipped}

    @api.model
    def _a02r2_customer(self, event, kind, partner, channel, values, record, subject=None):
        if not partner:
            return {"queued": False, "reason": "no customer"}
        language = self._preferred_language(partner)
        text = _CUSTOMER[kind]
        body = (text.get(language) or text["en"]).format(**values)
        if subject:
            subject = (subject.get(language) or subject["en"]).format(**values)
        try:
            delivery = self.queue(
                channel=channel,
                purpose="service_updates",
                partner=partner,
                body=body,
                subject=subject,
                lawful_basis="contract",
                source_model=record._name,
                source_id=record.id,
                source_event_id=event.get("event_id"),
                dedup_key="a02r2-%s:%s" % (kind, event.get("event_id") or record.id),
                operating_unit=record.operating_unit_id
                if "operating_unit_id" in record._fields
                else None,
                company=record.company_id if "company_id" in record._fields else None,
            )
        except ValidationError as exc:
            if hasattr(record, "message_post"):
                record.message_post(body="Customer not notified (%s): %s" % (kind, exc))
            return {"queued": False, "reason": str(exc)}
        return {"queued": delivery.state != "suppressed", "delivery_id": delivery.id}

    # ----------------------------------------------------------------- M01 SLA
    @api.model
    def consume_sla_near_breach(self, event: dict) -> dict:
        """sla.instance_near_breach -> the branch's Service Supervisors."""
        self._m01_assert_relay()
        payload = event.get("payload") or {}
        if payload.get("res_model") != "fix.service.order":
            return {"queued": 0, "reason": "not a service-order clock"}
        order = self._a02r2_record("fix.service.order", payload.get("res_id"))
        if not order or order.state in ("delivered", "closed", "cancelled"):
            return {"queued": 0, "reason": "no open service order"}
        group = self.env.ref(SUPERVISOR_GROUP, raise_if_not_found=False)
        users = order._fix_branch_users(group) if group else self.env["res.users"]
        if not users:
            order.message_post(
                body="SLA near breach (%s): no Service Supervisor of this branch to notify."
                % (payload.get("kpi") or "resolution")
            )
            return {"queued": 0, "reason": "no supervisor"}
        values = {
            "record": order.name,
            "kpi": payload.get("kpi") or "resolution",
            "target": payload.get("target_at") or "-",
        }
        return self._a02r2_email_users(event, "near_breach", users, values, order)

    @api.model
    def consume_sla_escalated(self, event: dict) -> dict:
        """sla.escalated -> the users the escalation rule named."""
        self._m01_assert_relay()
        payload = event.get("payload") or {}
        escalation = self._a02r2_record("fix.escalation.event", event.get("aggregate_id"))
        if not escalation:
            return {"queued": 0, "reason": "no escalation event"}
        users = escalation.notified_user_ids.filtered(lambda u: u.active and not u.share)
        if not users:
            return {"queued": 0, "reason": "the escalation named nobody"}
        values = {
            "record": escalation.record_ref or "%s #%s" % (escalation.res_model, escalation.res_id),
            "kpi": payload.get("kpi") or escalation.kpi_code or "resolution",
            "elapsed": "%.0f" % (payload.get("elapsed_pct") or escalation.elapsed_pct or 0.0),
            "threshold": "%.0f" % (payload.get("threshold_pct") or escalation.threshold_pct or 0.0),
        }
        return self._a02r2_email_users(event, "escalated", users, values, escalation)

    # ------------------------------------------------------------------ M05
    @api.model
    def consume_msp_service_report_published(self, event: dict) -> dict:
        """AUT-RMS-10: the client contacts are told the report is out."""
        self._m01_assert_relay()
        report = self._a02r2_record("fix.msp.service.report", event.get("aggregate_id"))
        if not report:
            return {"queued": False, "reason": "no service report"}
        msp = report.msp_contract_id
        partner = msp.contract_id.customer_id if msp.contract_id else None
        language = self._preferred_language(partner) if partner else "en"
        summary = (report.summary_bn if language == "bn" else report.summary_en) or ""
        values = {"period": report.period_label, "contract": msp.name, "summary": summary}
        return self._a02r2_customer(
            event,
            "report",
            partner,
            "email",
            values,
            report,
            subject=_CUSTOMER["report"]["subject"],
        )

    # ------------------------------------------------------------------ M06
    @api.model
    def consume_data_case_evaluated(self, event: dict) -> dict:
        """AUT-DTS-03: the customer is told the evaluation is complete."""
        self._m01_assert_relay()
        evaluation = self._a02r2_record("fix.data.evaluation", event.get("aggregate_id"))
        if not evaluation or not evaluation.evaluated_at or not evaluation.case_id:
            return {"queued": False, "reason": "no completed evaluation"}
        case = evaluation.case_id
        return self._a02r2_customer(
            event, "evaluated", case.customer_id, "sms", {"case": case.name}, case
        )

    @api.model
    def consume_data_case_quote_sent(self, event: dict) -> dict:
        """A sent quotation reaches the customer: its number and amount."""
        self._m01_assert_relay()
        quote = self._a02r2_record("fix.data.quote", event.get("aggregate_id"))
        if not quote or quote.state == "draft" or not quote.case_id:
            return {"queued": False, "reason": "no sent quotation"}
        case = quote.case_id
        values = {"quote": quote.name, "case": case.name, "amount": "%.2f" % (quote.amount or 0.0)}
        return self._a02r2_customer(event, "quote", case.customer_id, "sms", values, case)
