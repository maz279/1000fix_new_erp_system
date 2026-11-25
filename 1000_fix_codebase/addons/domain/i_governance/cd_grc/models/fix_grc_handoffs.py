# A12 audit (2026-11-04) D8 hand-off "M67 risks -> M60": a project risk at
# severity 9 (or the configured escalation threshold) was closed or carried
# with no mitigation and never reached the enterprise risk register. cd_ppm
# publishes project.risk_escalated; this consumer opens the matching
# fix.risk.register entry so GRC owns it from there.
#
# A12 finish (2026-11-07) F5: the first version read `payload["project"]` as a
# dict while the publisher sends a string, so all 3 live deliveries died on
# AttributeError while the project's chatter said "delivered". It also defaulted
# likelihood and impact to 3, so a severity 9 risk landed at 3 x 3.
from math import sqrt

from odoo import api, models

# The project scale (1-3) on the register's scale (1-5): a high x high project
# risk is the register's 25, not its 9.
LEVEL_SCORE = {"low": 1, "medium": 3, "high": 5, 1: 1, 2: 3, 3: 5}


def _level_score(level):
    """A register score from a project level. The hand-off carries the words; a
    numeric 1-5 is taken as it stands, inside the register's range."""
    if level in ("low", "medium", "high"):
        return LEVEL_SCORE[level]
    try:
        return min(5, max(1, int(level)))
    except (TypeError, ValueError):
        return None


class FixRiskRegisterProjectHandoff(models.Model):
    _inherit = "fix.risk.register"

    @api.model
    def _project_risk_of(self, event):
        if "fix.project.risk" not in self.env:
            return None
        return self.env["fix.project.risk"].sudo().browse(event.get("aggregate_id") or 0).exists()

    @api.model
    def _project_risk_scores(self, event, payload):
        """(likelihood, impact) as the register's 1-5. Events published before the
        hand-off carried them are read from the risk, else from the severity."""
        likelihood = _level_score(payload.get("probability"))
        impact = _level_score(payload.get("impact"))
        if likelihood and impact:
            return likelihood, impact
        risk = self._project_risk_of(event)
        if risk:
            # A score the event does state stands; only the missing one is read back.
            return (
                likelihood or _level_score(risk.probability),
                impact or _level_score(risk.impact),
            )
        try:
            level = round(sqrt(max(1, int(payload.get("severity")))))
        except (TypeError, ValueError):
            level = 2
        fallback = LEVEL_SCORE[min(3, level)]
        return likelihood or fallback, impact or fallback

    @api.model
    def consume_project_risk_escalated(self, event):
        """Open a register entry for an escalated project risk.

        Idempotent: the entry name carries the project risk's own number, so a
        redelivery finds it and creates nothing.
        """
        payload = event.get("payload") or {}
        title = (payload.get("title") or payload.get("name") or "Project risk").strip()
        project = payload.get("project") or payload.get("project_name") or ""
        if isinstance(project, dict):
            project = project.get("name") or ""
        reference = payload.get("risk") or event.get("event_id") or ""
        name = "[M67] %s%s%s" % (
            "%s: " % reference if reference else "",
            title,
            " — %s" % project if project else "",
        )
        existing = self.sudo().search([("name", "=", name)], limit=1)
        if existing:
            return existing
        likelihood, impact = self._project_risk_scores(event, payload)
        company = (
            self.env["res.company"].browse(event.get("company_id"))
            if event.get("company_id")
            else self.env.company
        )
        entry = self.sudo().create(
            {
                "name": name,
                "category": "operational",
                "likelihood": str(likelihood),
                "impact": str(impact),
                "mitigation": "Escalated from project risk register (event %s, %s).\n%s"
                % (
                    event.get("event_id") or "",
                    payload.get("reason") or "no reason stated",
                    payload.get("mitigation") or "",
                ),
                "company_id": company.id,
                "state": "open",
            }
        )
        risk = self._project_risk_of(event)
        if risk:
            risk.message_post(
                body="Entered on the enterprise risk register as %s (score %d)."
                % (entry.display_name, entry.risk_score)
            )
        return entry
