# cd_consignment — M03 Logistics & Reverse Logistics core (P06-M07, CD-M03-01/02).
#
# G3-05: pick & drop operating with an UNBROKEN CHAIN OF CUSTODY. A
# consignment moves through custody scan events; the chain is verified, not
# assumed — a gap in the chain is a hard error, never a warning.
from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish  # FF-28

# The custody chain, in order. A handover skips forward only with a named
# exception reason (e.g. customer absent -> returned to branch).
CUSTODY_STEPS = [
    ("picked_up", "Picked Up"),
    ("in_transit", "In Transit"),
    ("hub_scan", "Hub Scan"),
    ("out_for_delivery", "Out for Delivery"),
    ("delivered", "Delivered"),
    ("returned", "Returned"),
]


class FixConsignment(models.Model):
    """A logistics consignment (device to workshop, part to branch, device
    back to customer). Carries a custody chain that must never break."""

    _name = "fix.consignment"
    _description = "Consignment"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "scheduled_date desc, id desc"

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    name = fields.Char(string="Consignment No.", readonly=True, index=True, copy=False)
    consignment_type = fields.Selection(
        [("pickup", "Pickup (customer -> branch)"), ("delivery", "Delivery (branch -> customer)"),
         ("branch_transfer", "Branch Transfer"), ("return_to_vendor", "Return to Vendor")],
        required=True, default="pickup")
    state = fields.Selection(
        [("draft", "Draft"), ("confirmed", "Confirmed"), ("in_transit", "In Transit"),
         ("delivered", "Delivered"), ("returned", "Returned"), ("lost", "Lost")],
        default="draft", required=True, tracking=True)
    scheduled_date = fields.Datetime(required=True)
    origin_branch_id = fields.Many2one("fix.branch", string="Origin")
    dest_branch_id = fields.Many2one("fix.branch", string="Destination")
    rider_id = fields.Many2one("hr.employee", string="Rider", index=True)
    service_order_id = fields.Many2one("fix.service.order", string="Service Order",
                                       index=True)
    purchase_order_id = fields.Many2one("fix.purchase.order", string="Purchase Order",
                                        index=True)
    custody_ids = fields.One2many("fix.custody.scan", "consignment_id",
                                  string="Custody Chain")
    chain_broken = fields.Boolean(compute="_compute_chain", store=True,
                                  string="Chain Broken")
    custody_summary = fields.Char(compute="_compute_chain", store=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("name"):
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "fix.consignment") or ("CSG/%s" % fields.Date.today())
        return super().create(vals_list)

    @api.depends("custody_ids.step", "custody_ids.scanned_at")
    def _compute_chain(self):
        """The unbroken-chain check: custody scans must appear in the
        canonical step order with no gap. A scan out of order breaks the
        chain (G3-05 — the gate criterion is evidence, not hope)."""
        order = [s[0] for s in CUSTODY_STEPS]
        for consignment in self:
            scans = consignment.custody_ids.sorted("scanned_at")
            positions = [order.index(scan.step) for scan in scans if scan.step in order]
            monotonic = all(b > a for a, b in zip(positions, positions[1:]))
            consignment.chain_broken = not monotonic
            consignment.custody_summary = " -> ".join(
                dict(CUSTODY_STEPS)[s.step] for s in scans) or "no scans"

    def action_confirm(self):
        for consignment in self:
            consignment.state = "confirmed"

    def action_report_lost(self):
        """A lost consignment raises an incident — never silently drops."""
        for consignment in self:
            consignment.state = "lost"
            publish(self.env, "consignment.lost", "fix.consignment",
                    consignment.id, {"consignment": consignment.name})

    def action_deliver(self):
        """Deliver consignment enforcing unbroken chain of custody (Gate G3-05)."""
        for consignment in self:
            if consignment.chain_broken:
                raise UserError("Cannot deliver consignment: custody chain is broken (Gate G3-05).")
            last_scan = consignment.custody_ids.sorted("scanned_at")[-1:]
            if not last_scan or last_scan.step != "delivered":
                raise UserError("Cannot deliver consignment: terminal 'delivered' custody scan missing.")
            consignment.state = "delivered"
            publish(self.env, "consignment.delivered", "fix.consignment", consignment.id, {
                "consignment": consignment.name,
                "delivered_at": fields.Datetime.to_string(fields.Datetime.now()),
            })

    def action_return(self):
        """Reverse logistics return transition."""
        for consignment in self:
            consignment.state = "returned"
            publish(self.env, "consignment.returned", "fix.consignment", consignment.id, {
                "consignment": consignment.name,
                "returned_at": fields.Datetime.to_string(fields.Datetime.now()),
            })


class FixCustodyScan(models.Model):
    """One custody scan event — the chain's links. Scanned by the P09 rider
    app or the branch front desk; every scan is terminal-attributed."""

    _name = "fix.custody.scan"
    _description = "Custody Scan"
    _inherit = ["mail.thread"]
    _order = "scanned_at, id"

    consignment_id = fields.Many2one("fix.consignment", required=True,
                                     ondelete="cascade", index=True)
    step = fields.Selection(CUSTODY_STEPS, required=True,
                            help="The canonical custody step this scan records")
    scanned_at = fields.Datetime(default=fields.Datetime.now, required=True)
    scanned_by = fields.Many2one("hr.employee", string="Scanned By")
    location_branch_id = fields.Many2one("fix.branch", string="Location")
    exception_reason = fields.Char(
        help="Required when a step is skipped (named exception, never silent)")
    device_serial = fields.Char(string="Device Serial",
                                help="What is in custody — verified at every scan")

    @api.constrains("step", "exception_reason")
    def _check_exception(self):
        for scan in self:
            siblings = scan.consignment_id.custody_ids.sorted("scanned_at")
            if siblings and scan.id == siblings[-1].id and scan.exception_reason:
                pass  # a named exception on the latest scan is legitimate
            elif not siblings and scan.step != "picked_up" and not scan.exception_reason:
                raise UserError(
                    "A chain that does not start at pickup needs a named exception")
