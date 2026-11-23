# fix_knowledge_surface — M61 knowledge surfacing ON THE JOB (A10 deep audit
# 2026-11-23, D-A10-1/#4).
#
# "M31 repair methods" / "M01 diagnostic trees" were registry claims with no
# production caller: surface_for() (FR-KMS-015) ranked published articles and
# trees perfectly — and nothing read it. A technician never saw fault-matched
# procedures at the moment of diagnosis.
#
# cd_knowledge already depends on cd_service_order, so the wiring lives here
# with no new dependency: every service order carries its knowledge surface
# (fault-code/model/brand matched, ranked by link relevance then resolution
# rate), exposed as a computed list the order drawer reads and as an API
# payload for the P02 app. Published-only, honest-empty by construction.
from odoo import api, fields, models


class FixServiceOrderKnowledgeSurface(models.Model):
    _inherit = "fix.service.order"

    knowledge_surface_ids = fields.Json(
        string="Knowledge Surface (M61)",
        compute="_compute_knowledge_surface",
        help="The published knowledge for THIS job — articles and troubleshooting "
        "trees matched on the fault code, device model and brand, ranked by link "
        "relevance then by how often they resolved the fault (FR-KMS-015).",
    )

    @api.depends(
        "fault_line_ids",
        "fault_line_ids.fault_code",
        "device_id",
        "device_id.device_model_id",
        "device_id.device_model_id.brand_id",
    )
    def _compute_knowledge_surface(self):
        Article = self.env.get("fix.knowledge.article")
        for order in self:
            rows = []
            if Article is not None:
                fault = order.fault_line_ids[:1]
                rows = Article.sudo().surface_for(
                    fault_code_id=fault.fault_code_id.id
                    if fault and "fault_code_id" in fault._fields
                    else None,
                    device_model_id=order.device_id.device_model_id.id
                    if order.device_id
                    else None,
                    brand_id=order.device_id.device_model_id.brand_id.id
                    if order.device_id and order.device_id.device_model_id
                    else None,
                )
            order.knowledge_surface_ids = rows or []

    def action_read_the_knowledge(self):
        """Open the surfaced ARTICLES (the trees stay one click deeper in the
        M61 workspace — one act_window cannot span two models honestly)."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Knowledge for %s" % self.name,
            "domain": [
                ("id", "in", [r["id"] for r in (self.knowledge_surface_ids or []) if r["kind"] == "article"])
            ],
            "res_model": "fix.knowledge.article",
            "view_mode": "list,form",
            "target": "current",
        }
