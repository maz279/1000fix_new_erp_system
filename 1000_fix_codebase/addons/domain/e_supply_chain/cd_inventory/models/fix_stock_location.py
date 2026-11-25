# cd_inventory — Multi-location & Van Stock Locations (M15, CD-M15-01).
from __future__ import annotations

import logging

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from .fix_inventory_approval import CONTROLLER_GROUP, location_class

_logger = logging.getLogger(__name__)

# D3: store types a job never draws from (they hold what left use)
NOT_ISSUING_TYPES = ("damage", "returnable_damage")
EPS = 1e-6


class FixStockLocation(models.Model):
    """Multi-location storage facility including branch warehouses and mobile van stock."""

    _name = "fix.stock.location"
    _description = "Inventory Location & Van Stock"
    # A06 audit (2026-11-03): the status and the audit stamps were free
    # fields; they now change only through their actions.
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]

    company_id = fields.Many2one(
        "res.company",
        required=True,
        index=True,
        default=lambda self: self.env.company,
    )
    operating_unit_id = fields.Many2one(
        "operating.unit",
        string="Operating Unit",
        index=True,
    )
    name = fields.Char(string="Location Name", required=True, tracking=True)
    name_bn = fields.Char(string="লোকেশন নাম (বাংলা)", help="Bengali name per DoD-08")
    code = fields.Char(string="Location Code", required=True, size=16, index=True)

    location_type = fields.Selection(
        [
            ("central", "Central Warehouse"),
            ("branch", "Branch Hub / Workshop"),
            ("van", "Mobile Technician Van Stock"),
            ("quarantine", "Quarantine / Inspection"),
            ("scrap", "Scrap / E-Waste Disposal"),
        ],
        string="Location Type",
        required=True,
        default="branch",
        tracking=True,
    )

    branch_id = fields.Many2one("fix.branch", string="Branch Hub", index=True)
    # WAREHOUSE-WITH-LOCATION capability report (2026-11-09) E1: the legacy
    # estate's six stock classes (Warranty / Non-Warranty / Returnable Damage /
    # Buffer / Refurbished / Damage) are a stock dimension of their own —
    # location_type says what a place IS, stock_type says which class of stock
    # it holds. Canonical locations load as <BRANCH>-<TYPE> children under the
    # branch hub (e.g. GCSC-WTY under GCSC).
    stock_type = fields.Selection(
        [
            ("warranty", "Warranty"),
            ("non_warranty", "Non-Warranty"),
            ("returnable_damage", "Returnable Damage"),
            ("buffer", "Buffer Stock"),
            ("refurbished", "Refurbished"),
            ("damage", "Damage"),
            ("unspecified", "Unspecified"),
        ],
        string="Stock Type",
        index=True,
        tracking=True,
        help="Stock class held at this location; blank on structural hubs.",
    )
    technician_id = fields.Many2one(
        "hr.employee",
        string="Custodian Technician",
        index=True,
        help="Designated field technician for mobile van stock",
    )
    van_plate = fields.Char(string="Vehicle Registration / Plate Number")
    is_van_stock = fields.Boolean(
        string="Is Van Stock",
        compute="_compute_is_van_stock",
        store=True,
    )
    is_van_location = fields.Boolean(
        string="Is Van Location",
        compute="_compute_is_van_stock",
        store=True,
    )

    parent_id = fields.Many2one("fix.stock.location", string="Parent Location", index=True)
    # D7 (owner decision 20 Nov 2026): a van or branch store below its minimum
    # is refilled by a transfer from the warehouse that supplies it; only
    # warehouses buy. Empty: the central store of its operating unit.
    supply_location_id = fields.Many2one(
        "fix.stock.location",
        string="Replenished From",
        index=True,
        domain="[('location_type', '=', 'central')]",
        help="The warehouse a transfer refills this location from when it falls below its "
        "minimum. Empty: the one central store of the location's operating unit.",
    )
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("inactive", "Inactive")],
        string="Status",
        default="active",
        tracking=True,
    )
    active = fields.Boolean(default=True)
    last_audit_date = fields.Date(string="Last Physical Audit Date")
    audit_discrepancy_count = fields.Integer(string="Audit Discrepancies", default=0)
    legacy_reference = fields.Char(
        string="Legacy Reference",
        index=True,
        readonly=True,
        copy=False,
        help="MIG-03: permanent source-system reference written by the inventory "
        "loader (migrations/load_inventory.py) - never edited, never copied",
    )

    _code_company_unique = models.Constraint(
        "UNIQUE (code, company_id)",
        "Location code must be unique per company.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        # A06 ERP audit A36: custody decides who draws from a van, so naming a
        # custodian is an Inventory Controller's act on create as on write
        if not self.env.su and not self.env.user.has_group(CONTROLLER_GROUP):
            for vals in vals_list:
                if vals.get("technician_id"):
                    raise AccessError(
                        "Only an Inventory Controller names a location's custodian technician."
                    )
        return super().create(vals_list)

    @api.depends("location_type")
    def _compute_is_van_stock(self):
        for loc in self:
            val = loc.location_type == "van"
            loc.is_van_stock = val
            loc.is_van_location = val

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "last_audit_date",
            "audit_discrepancy_count",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.id and not self.env.user.has_group(CONTROLLER_GROUP):
            locked |= {"location_type", "technician_id"}
        return locked

    def write(self, vals):
        # A06 final pass A2 / M15-14: custody decides who draws from a van, so the
        # custodian and the van's type change only by an Inventory Controller
        # (a storekeeper naming himself custodian would pass the custody check).
        if self and not self._fix_guard_open() and not self.env.user.has_group(CONTROLLER_GROUP):
            for name in ("technician_id", "location_type"):
                if name in vals and any(
                    loc._fix_guard_differs(name, vals[name], loc[name]) for loc in self
                ):
                    raise AccessError(
                        "Only an Inventory Controller changes a location's custodian or type."
                    )
        return super().write(vals)

    # ---------------------------------------------------- D7 supply chain
    def _fix_supplier_location(self):
        """Where this van or branch store is refilled from: its configured
        warehouse, else the single central store of its operating unit.
        Refuses clearly when none or several could be meant (fail closed)."""
        self.ensure_one()
        loc = self.sudo()
        if loc.supply_location_id:
            return loc.supply_location_id
        ou = loc.operating_unit_id or loc.branch_id.operating_unit_id
        warranty = (loc.stock_type or False) == "warranty"
        centrals = (
            self.sudo()
            .search(
                [
                    ("company_id", "=", loc.company_id.id),
                    ("location_type", "=", "central"),
                    ("state", "=", "active"),
                    ("id", "!=", loc.id),
                    ("operating_unit_id", "=", ou.id if ou else False),
                ]
            )
            # D3: a warranty store is refilled from a warranty warehouse, any
            # other store never from one
            .filtered(lambda c: ((c.stock_type or False) == "warranty") == warranty)
        )
        if len(centrals) == 1:
            return centrals
        raise UserError(
            "%s has no warehouse to be refilled from (%s): set its 'Replenished From' "
            "warehouse (D7: a van or branch store is refilled by a transfer, never bought for)."
            % (
                loc.code,
                "no central store of its kind (warranty or not) in its operating unit"
                if not centrals
                else "%d central stores in its operating unit" % len(centrals),
            )
        )

    # ---------------------------------------------------- D3 job stores
    @api.model
    def _fix_job_store(
        self,
        company,
        branch,
        warranty,
        part,
        qty,
        technician=None,
        job_ref=None,
        fixed=None,
        van=None,
    ):
        """The store a job's part is issued from (D3, A06 ERP audit A06/A08):
        returns (location, reservation).

        1. the job's own active reservation of the part (it was held for it);
        2. the van named on the job, else the technician's van, when it is a
           store of the job's warranty status;
        3. a fixed store (a workshop's own), when it is of that status;
        4. the branch's stores of that status (warranty jobs: warranty stores
           only; other jobs: never a warranty or damage store) that hold the
           part available. One is chosen only when exactly one qualifies:
           several are refused as ambiguous, never the first taken."""
        Location = self.sudo()
        Reservation = self.env["fix.stock.reservation"].sudo()

        def fits(loc):
            if not loc:
                return False
            is_w = (loc.stock_type or False) == "warranty"
            if warranty != is_w:
                return False
            return (loc.stock_type or False) not in NOT_ISSUING_TYPES

        def available(loc):
            row = self.env["fix.stock.onhand"]._bucket(part, loc, location_class(loc, "owned"))
            return (row.qty - row.reserved) if row else 0.0

        if job_ref:
            held = Reservation.search(
                [
                    ("state", "=", "active"),
                    ("service_order_ref", "=", job_ref),
                    ("part_id", "=", part.id),
                    ("company_id", "=", company.id),
                ],
                order="priority, reserved_at, id",
            ).filtered(lambda r: fits(r.location_id) and r.qty_open + EPS >= qty)
            if held:
                return held[0].location_id, held[0]
        if not van and technician:
            van = Location.search(
                [
                    ("technician_id", "=", technician.id),
                    ("location_type", "=", "van"),
                    ("state", "=", "active"),
                ]
            )
            if len(van) > 1:
                van = van.filtered(fits)
                if len(van) > 1:
                    raise UserError(
                        "%s has several vans (%s): name the van on the job."
                        % (technician.name, ", ".join(van.mapped("code")))
                    )
        if van and fits(van):
            return van, Reservation
        if fixed:
            if not fits(fixed):
                raise UserError(
                    "Store %s is %s store, and this is %s job (D3): set the workshop's "
                    "warranty store, or issue from a store of the job's kind."
                    % (
                        fixed.code,
                        "a warranty" if fixed.stock_type == "warranty" else "a non-warranty",
                        "a warranty" if warranty else "a non-warranty",
                    )
                )
            return fixed, Reservation
        if not branch:
            return Location.browse(), Reservation
        stores = Location.search(
            [
                ("branch_id", "=", branch.id),
                ("location_type", "in", ("branch", "central")),
                ("state", "=", "active"),
                ("company_id", "=", company.id),
            ]
        ).filtered(fits)
        if len(stores) <= 1:
            return stores, Reservation
        stocked = stores.filtered(lambda loc: available(loc) + EPS >= qty)
        if len(stocked) == 1:
            return stocked, Reservation
        raise UserError(
            "Branch %s has %s %s stores %s %s: which one the part leaves is ambiguous. Reserve "
            "it for the job at the store it should come from."
            % (
                branch.display_name,
                len(stocked or stores),
                "warranty" if warranty else "non-warranty",
                "holding" if stocked else "and none holds",
                "%s %s (%s)"
                % (qty, part.part_number, ", ".join((stocked or stores).mapped("code"))),
            )
        )

    def _location_check_controller(self):
        if not self.env.su and not self.env.user.has_group(CONTROLLER_GROUP):
            raise AccessError("Only an Inventory Controller opens or closes a stock location.")

    def action_set_active(self):
        self._location_check_controller()
        self._guarded().write({"state": "active"})
        return True

    def action_set_inactive(self):
        """An inactive location moves no stock (every movement checks it)."""
        self._location_check_controller()
        self._guarded().write({"state": "inactive"})
        return True

    @api.constrains("location_type", "technician_id")
    def _check_van_technician(self):
        for loc in self:
            if loc.location_type == "van" and not loc.technician_id:
                raise ValidationError(
                    "Mobile van stock locations must designate a custodian technician."
                )

    def action_audit_van_stock(
        self,
        audited_skus: list[dict] | None = None,
        audited_count: float | None = None,
        discrepancy_count: float | None = None,
    ) -> dict:
        """Execute mobile van stock physical reconciliation audit. An Inventory
        Controller who is not the van's custodian audits it; the RF device sends
        the audited lines, the workspace button the two totals."""
        self.ensure_one()
        if self.location_type != "van":
            raise ValidationError("Van stock audit can only be performed on van stock locations.")
        if not self.env.su and (
            not self.env.user.has_group(CONTROLLER_GROUP)
            or self.technician_id.user_id == self.env.user
        ):
            raise AccessError("An Inventory Controller other than the custodian audits a van.")

        if audited_skus:
            total_audited = len(audited_skus)
            discrepancies = sum(1 for s in audited_skus if s.get("discrepancy_qty", 0) != 0)
        else:
            total_audited = int(audited_count or 0)
            discrepancies = int(discrepancy_count or 0)
        if total_audited <= 0:
            # A06 audit M15-16: an audit with no lines used to report 100%
            # accuracy; nothing audited is not an accurate van.
            raise ValidationError("A van stock audit needs at least one audited line.")
        if discrepancies < 0 or discrepancies > total_audited:
            raise UserError(
                "%s discrepancies out of %s audited lines is not possible."
                % (discrepancies, total_audited)
            )

        self._guarded().write(
            {
                "last_audit_date": fields.Date.context_today(self),
                "audit_discrepancy_count": discrepancies,
            }
        )

        # Emit van.reconciled outbox event
        accuracy_pct = round((total_audited - discrepancies) / total_audited * 100.0, 1)
        event_payload = {
            "van_id": self.id,
            "van_code": self.code,
            "technician_id": self.technician_id.id if self.technician_id else False,
            "audited_qty": total_audited,
            "discrepancy_qty": discrepancies,
            "accuracy_pct": accuracy_pct,
            "audit_date": str(self.last_audit_date),
        }

        try:
            from libs.py.fix_events import publish

            publish(self.env, "van.reconciled", "fix.stock.location", self.id, event_payload)
        except Exception:
            _logger.exception("van.reconciled event publish failed for location %s", self.id)

        return {
            "van_id": self.id,
            "audited_count": total_audited,
            "discrepancies": discrepancies,
            "accuracy_pct": accuracy_pct,
            "status": "reconciled",
        }
