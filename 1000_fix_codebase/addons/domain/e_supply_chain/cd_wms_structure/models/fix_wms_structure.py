# cd_wms_structure — M41 Warehouse structure, W3 slice (P06-M07, CD-M41-01).
#
# The warehouse STRUCTURE only: warehouses, zones, bins. Inbound/outbound
# operations (CD-M41-02/03) land in Phase 5's inventory completion; this
# slice exists so consignments and procurement have physical destinations.
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class FixWarehouse(models.Model):
    """A warehouse (central + depot workshops)."""

    _name = "fix.warehouse"
    _description = "Warehouse"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    name = fields.Char(required=True)
    code = fields.Char(required=True, size=8)
    branch_id = fields.Many2one("fix.branch", string="Branch", index=True)
    zone_ids = fields.One2many("fix.warehouse.zone", "warehouse_id", string="Zones")
    active = fields.Boolean(default=True)
    # Odoo 19 dropped the legacy constraint tuple list;
    # models.Constraint attributes (migrated by tooling/scripts/migrate-sql-constraints.py)
    _code_company_unique = models.Constraint('UNIQUE (code, company_id)', 'Warehouse code must be unique per company')


class FixWarehouseZone(models.Model):
    """A zone inside a warehouse (receiving, QC, quarantine, main storage,
    dispatch). Zone TYPES carry the M15 rules that Phase 5 enforces:

      quarantine/blocked -> stock inside cannot be reserved or issued
                            (BRU-INV-08); goods become available only after
                            the inspection step is recorded (BRU-INV-09)
    """

    _name = "fix.warehouse.zone"
    _description = "Warehouse Zone"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    warehouse_id = fields.Many2one("fix.warehouse", required=True, ondelete="cascade")
    name = fields.Char(required=True)
    code = fields.Char(required=True, size=8)
    zone_type = fields.Selection(
        [("receiving", "Receiving"), ("inspection", "Quality Inspection"),
         ("quarantine", "Quarantine / Blocked"), ("storage", "Main Storage"),
         ("dispatch", "Dispatch"), ("returns", "Returns")],
        required=True, default="storage")
    reservable = fields.Boolean(compute="_compute_reservable", store=True,
                                help="False for quarantine/blocked zones — BRU-INV-08")
    bin_ids = fields.One2many("fix.warehouse.bin", "zone_id", string="Bins")
    # Odoo 19 dropped the legacy constraint tuple list;
    # models.Constraint attributes (migrated by tooling/scripts/migrate-sql-constraints.py)
    _code_warehouse_unique = models.Constraint('UNIQUE (code, warehouse_id)', 'Zone code must be unique within the warehouse')

    @api.depends("zone_type")
    def _compute_reservable(self):
        for zone in self:
            zone.reservable = zone.zone_type not in ("quarantine", "inspection")


class FixWarehouseBin(models.Model):
    """A storage bin — the leaf of the structure (CD-M41-01)."""

    _name = "fix.warehouse.bin"
    _description = "Warehouse Bin"
    # P03 workspace data-entry form (discovered by cd_p03_portal).
    _p03_capture = {
        "module": "M41",
        "form": "Bin",
        "fields": ["zone_id", "name", "barcode", "capacity_qty"],
    }
    _inherit = ["mail.thread", "mail.activity.mixin"]

    zone_id = fields.Many2one("fix.warehouse.zone", required=True, ondelete="cascade")
    name = fields.Char(required=True)
    barcode = fields.Char(index=True, help="RF-scannable bin barcode")
    capacity_qty = fields.Float(default=0.0,
                                help="0 = unconstrained bin")

    @api.constrains("capacity_qty")
    def _check_capacity(self):
        for bin_record in self:
            if bin_record.capacity_qty < 0:
                raise ValidationError("Bin capacity cannot be negative")
