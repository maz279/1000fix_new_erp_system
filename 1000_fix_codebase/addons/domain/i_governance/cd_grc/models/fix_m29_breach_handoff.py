# M29 -> M60 breach hand-off (M29 capture pass 2, 2026-11-19).
#
# Spec M29 §8.3 / AUT-SEC-13 / NFR-094: when a Security Officer assesses an
# incident as a notifiable personal-data breach, M29 "hands off to M60 with the
# evidence pack and starts the statutory clock"; M60 notifies the Authority
# (§3.2: breach notification is M60's). The hand-off opens the M60 Personal Data
# Breach record and tells the Compliance Officers. cd_grc depends on cd_rbac_ext,
# so the bridge lives here; without cd_grc the incident says to notify directly.
from odoo import models

GRC_OFFICER_GROUP = "cd_grc.group_grc_officer"


class FixSecurityIncidentM60(models.Model):
    _inherit = "fix.security.incident"

    def _fix_breach_handoff(self):
        self.ensure_one()
        rec = self.sudo()
        breach = (
            self.env["fix.grc.data.breach"]
            .sudo()
            .create(
                {
                    "company_id": rec.company_id.id,
                    "detected_on": rec.detected_at,
                    "description": "Security incident %s (%s, %s): %s\n\nBreach assessment by %s:\n%s"
                    % (
                        rec.name,
                        rec.category,
                        rec.severity,
                        rec.title,
                        self.env.user.name,
                        rec.breach_assessment or "",
                    ),
                    "subjects_affected": rec.data_subjects_estimate or 0,
                    "containment": rec.containment or False,
                    "assessment": rec.breach_assessment or False,
                }
            )
        )
        group = self.env.ref(GRC_OFFICER_GROUP, raise_if_not_found=False)
        officers = (group.sudo().user_ids if group else self.env["res.users"]).filtered(
            lambda u: u.active and not u.share
        )
        # fix.grc.data.breach carries mail.thread only: the officers are told by
        # a message addressed to them (no activity mixin on that model)
        breach.message_post(
            body="Opened from security incident %s, assessed NOTIFIABLE by %s. The statutory "
            "clock started %s: notify the Authority and the data subjects within the "
            "prescribed period (NFR-094)."
            % (rec.name, self.env.user.name, rec.statutory_clock_start),
            partner_ids=officers.mapped("partner_id").ids,
            subtype_xmlid="mail.mt_comment",
        )
        return breach.name
