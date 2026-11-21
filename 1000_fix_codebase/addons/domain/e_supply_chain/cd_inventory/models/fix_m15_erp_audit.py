# cd_inventory - A06 ERP audit (20 Nov 2026), M15 builder stream: the pieces
# that belong to no single document.
#
#   A16  an inter-OU transfer moves its value between operating units: a
#        "transfer" valuation row out of the sender's OU and one into the
#        receiver's (net nil for the company);
#   X21  data repair: a ledger bucket carries the operating unit of the
#        location that holds it (the record rules show it to that branch);
#        4,863 fix_real buckets carried the main OU instead;
#   X33  stock.van_variance_detected reaches a receiver: the branch manager
#        (and the van's custodian's controllers) are told on the van.
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


def _transfer_rows_to_adjustment(rows):
    """Uninstalling keeps the rows as stock movements (+1 effect either way)."""
    rows.sudo()._guarded().write({"entry_type": "adjustment"})


class FixValuationSuspenseTransfer(models.Model):
    _inherit = "fix.inventory.valuation.suspense"

    # STOCK_EFFECT has no entry for it: the default (+1) is right, the row
    # carries the movement itself (out of one OU -, into the other +)
    entry_type = fields.Selection(
        selection_add=[("transfer", "Inter-OU Transfer")],
        ondelete={"transfer": _transfer_rows_to_adjustment},
    )


class FixStockOnhandOuRepair(models.Model):
    _inherit = "fix.stock.onhand"

    @api.model
    def _fix_repair_ou_stamps(self, dry_run=False):
        """X21: re-stamp every bucket whose operating unit is not that of its
        location (the location's own, else its branch's). A location with
        neither is left alone (nothing to derive from). Returns the counts
        and the value moved between operating units (BDT, owned classes)."""
        cr = self.env.cr
        self.env.flush_all()
        cr.execute(
            """
            SELECT o.id, o.operating_unit_id,
                   COALESCE(l.operating_unit_id, b.operating_unit_id) AS target,
                   COALESCE(o.qty, 0) * COALESCE(o.unit_cost, 0) AS value,
                   o.ownership_class
              FROM fix_stock_onhand o
              JOIN fix_stock_location l ON l.id = o.location_id
         LEFT JOIN fix_branch b ON b.id = l.branch_id
             WHERE COALESCE(l.operating_unit_id, b.operating_unit_id) IS NOT NULL
               AND o.operating_unit_id IS DISTINCT FROM
                   COALESCE(l.operating_unit_id, b.operating_unit_id)
            """
        )
        rows = cr.fetchall()
        valued = ("owned", "van", "bench", "warranty")
        result = {
            "buckets": len(rows),
            "value": round(sum(r[3] for r in rows if r[4] in valued), 2),
            "was_unset": len([r for r in rows if not r[1]]),
        }
        if rows and not dry_run:
            for target in {r[2] for r in rows}:
                ids = [r[0] for r in rows if r[2] == target]
                cr.execute(
                    "UPDATE fix_stock_onhand SET operating_unit_id = %s WHERE id = ANY(%s)",
                    (target, ids),
                )
            self.invalidate_model(["operating_unit_id"])
            _logger.info("X21: re-stamped the operating unit of %s buckets", len(rows))
        return result


class FixStockVanReconVarianceConsumer(models.Model):
    _inherit = "fix.stock.van.recon"

    @api.model
    def consume_van_variance_detected(self, event):
        """X33: a van count outside its tolerance is told to the people who
        decide it: the van's branch manager, else the Inventory Controllers of
        its company. Posted on the van location (its chatter), once per recon."""
        recon = self.sudo().browse(event.get("aggregate_id") or 0).exists()
        if not recon:
            return 0
        van = recon.location_id
        marker = "van-variance:%s" % recon.name
        if (
            self.env["mail.message"]
            .sudo()
            .search_count(
                [("model", "=", van._name), ("res_id", "=", van.id), ("body", "ilike", marker)]
            )
        ):
            return 0
        users = van.branch_id.manager_id
        if not users:
            group = self.env.ref("cd_wms_structure.group_inventory_controller")
            members = group.sudo().user_ids if "user_ids" in group._fields else group.sudo().users
            users = members.filtered(
                lambda u: not van.company_id or van.company_id in u.company_ids
            )
        payload = event.get("payload") or {}
        van.sudo().message_post(
            body="Van %s: count %s is outside the van tolerance (%s pieces, BDT %s). Issues "
            "from it are held until an approver resolves it. [%s]"
            % (
                van.code,
                recon.name,
                payload.get("variance"),
                payload.get("variance_value", "-"),
                marker,
            ),
            partner_ids=users.mapped("partner_id").ids,
            subtype_xmlid="mail.mt_comment",
        )
        return 1
