# A12 audit (2026-11-04) D8 hand-off "M67 risks -> M60": a project risk at
# severity 9 (or the configured escalation threshold) was closed or carried
# with no mitigation and never reached the enterprise risk register. cd_ppm
# publishes project.risk_escalated; this consumer opens the matching
# fix.risk.register entry so GRC owns it from there.
from odoo import api, models


class FixRiskRegisterProjectHandoff(models.Model):
    _inherit = "fix.risk.register"

    @api.model
    def consume_project_risk_escalated(self, event):
        """Open a register entry for an escalated project risk.

        Idempotent: the event id is stamped into the entry name, so a
        redelivery finds it and creates nothing.
        """
        payload = event.get("payload") or {}
        title = (payload.get("title") or payload.get("name") or "Project risk").strip()
        project = (payload.get("project") or {}).get("name") or payload.get("project_name") or ""
        event_id = event.get("event_id") or ""
        name = "[M67] %s%s" % (title, " — %s" % project if project else "")
        existing = self.sudo().search([("name", "=", name)], limit=1)
        if existing:
            return existing

        def _clamp(value, default=3):
            try:
                return str(min(5, max(1, int(value))))
            except (TypeError, ValueError):
                return str(default)

        company = (
            self.env["res.company"].browse(event.get("company_id"))
            if event.get("company_id")
            else self.env.company
        )
        return self.sudo().create(
            {
                "name": name,
                "category": "operational",
                "likelihood": _clamp(payload.get("probability"), 3),
                "impact": _clamp(payload.get("impact"), 3),
                "mitigation": "Escalated from project risk register (event %s).\n%s"
                % (event_id, payload.get("mitigation") or ""),
                "company_id": company.id,
                "state": "open",
            }
        )
