# The M14 payout as an M63 decision domain (A05 workflow audit E11): lets a
# DoA matrix row target the routed trade-in payout approval.
from odoo import fields, models


class FixApprovalMatrixTradein(models.Model):
    _inherit = "fix.approval.matrix"

    decision_domain = fields.Selection(
        selection_add=[("tradein_payout", "Trade-In Payout (M14)")],
        ondelete={"tradein_payout": "cascade"},
    )
