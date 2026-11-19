# M30 capture audit, second pass (2026-11-19), FR-ADM-004: a branch's
# capability profile says which repair levels it can perform, "so that intake,
# dispatch and booking respect it". The workshop is where a repair level is
# set, so a job above the profile of the workshop's branch is refused here.
# A branch without a recorded profile is not restricted.
from odoo import api, models
from odoo.exceptions import ValidationError


class FixWorkshopJobBranchCapability(models.Model):
    _inherit = "fix.workshop.job"

    @api.constrains("repair_level", "workshop_id")
    def _check_branch_capability(self):
        for job in self:
            branch = job.workshop_id.branch_id
            if not branch or not job.repair_level:
                continue
            refusal = branch._fix_capability_refusal(job.repair_level)
            if refusal:
                raise ValidationError("%s %s" % (job.display_name, refusal))
