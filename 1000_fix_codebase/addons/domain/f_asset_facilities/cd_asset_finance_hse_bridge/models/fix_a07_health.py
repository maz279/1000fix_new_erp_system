# fix_a07_health — A07 ERP audit (2026-11-20) FIN-25 and FIN-20 / M46-18.
#
# FIN-25: on fix_real no fixed-asset category had a journal or an account, so
# every A07 money hand-off dead-ended (failing closed). The health check lists,
# per company, what is still unconfigured: each category's journal and
# accounts (D1), and every account role the A07 money contract reads (D2/D3).
# The seed script (scratchpad build_r2a/seed_a07_finance.py) configures them.
#
# FIN-20 / M46-18: the cost of a vehicle over a period from the ledger's own
# figures (M49 depreciation, posted A07 cost entries by type, insurer
# recoveries), for the cost-per-km report to read instead of fuel + PM only.
from collections import defaultdict

from odoo import api, models

from .fix_bridge_exception import PARAM_PREFIX, role_account

CATEGORY_FIELDS = (
    "journal_id",
    "asset_account_id",
    "accumulated_account_id",
    "expense_account_id",
    "cwip_account_id",
    "gain_account_id",
    "loss_account_id",
)
# account roles: cd_asset_finance_hse_bridge.account.<key> (codes from D2/D3,
# D5, D19 and the R2a settlement roles). The seed reads this map.
ACCOUNT_ROLES = {
    "vehicle_fuel": "600259",
    "vehicle_service": "500005",
    "vehicle_insurance": "500505",
    "vehicle_insurance_excess": "500505",
    "vehicle_renewal": "5000110",
    "vehicle_fine": "500121",
    "vehicle_lease_rent": "500005",
    "lease_rent": "500401",
    # R2a: the service charge in a rent payment is a non-lease component
    "lease_rent.service_charge": "500401",
    "lease_rent.break_penalty": "500908",
    "site_utility": "500012",
    # the utility kinds M47 records (fix.site.utility.utility_type)
    "site_utility.power": "500403",
    "site_utility.water": "500403",
    "site_utility.gas": "500031",
    "facility_work_order": "510003",
    # a capitalised fit-out's cost lines book to CWIP (D1)
    "facility_work_order.fit_out": "100608",
    "calibration_service": "510003",
    "equipment_service": "510003",
    "equipment_expensed": "500093",
    "licence_fee": "500209",
    "licence_fee.trade": "500503",
    "licence_fee.agent": "500209",
    "licence_fee.penalty": "500121",
    "deposit": "100031",
    "deposit.refund": "100031",
    "deposit.adjusted": "200127",
    "deposit.write_off": "500906",
    "advance_rent": "100032",
    "advance_rent.refund": "100032",
    "advance_rent.write_off": "500906",
    "employee_recovery_receivable": "100049",
    "insurance_claim_receivable": "100048",
    "recovery.equipment_loss": "500901",
    "recovery.insurance": "500005",
    "ifrs16_liability": "200505",
    "ifrs16_interest": "500604",
    "ifrs16_clearing": "200127",
    # D19 (owner round 2)
    "petty_cash": "100034",
    "fuel_card_clearing": "200129",
    "disposal_proceeds": "200128",
}
# finer roles with NO fallback to their cost type (capital, or a settlement
# that would otherwise debit and credit the same deposit): a blocker when unset
STRICT_ROLES = (
    "facility_work_order.fit_out",
    "deposit.write_off",
    "advance_rent.write_off",
)
# roles whose account the owner has not decided: listed, never seeded
UNDECIDED_ROLES = ()


class FixAssetCategoryA07Health(models.Model):
    _inherit = "fix.asset.category"

    @api.model
    def _fix_a07_health(self, company=None):
        """What blocks the A07 money paths in `company` (default: every
        company): {'categories': [(code, name, [missing field labels])],
        'roles': [(param, why)], 'ok': bool}."""
        companies = company or self.env["res.company"].sudo().search([])
        categories, roles = [], []
        for comp in companies:
            for cat in self.sudo().search([("company_id", "=", comp.id)]):
                missing = [cat._fields[f].string for f in CATEGORY_FIELDS if not cat[f]]
                if missing:
                    categories.append((cat.code, cat.name, missing))
            for key in list(ACCOUNT_ROLES) + list(UNDECIDED_ROLES):
                if key not in STRICT_ROLES and "." in key and key.split(".")[0] in ACCOUNT_ROLES:
                    continue  # a finer role falls back to its cost type: not a blocker
                if not role_account(self.env, comp, key):
                    roles.append(
                        (
                            "%saccount.%s" % (PARAM_PREFIX, key),
                            "not set or not in %s's chart" % comp.name,
                        )
                    )
        return {"categories": categories, "roles": roles, "ok": not categories and not roles}


class FleetVehicleTco(models.Model):
    _inherit = "fleet.vehicle"

    def _fix_tco(self, date_from, date_to):
        """FIN-20: the vehicle's cost in [date_from, date_to] from the ledger:
        M49 book depreciation of its fixed asset, its POSTED A07 cost entries
        by cost type, less insurer settlements booked. Entries not yet in the
        GL are reported apart (provisional)."""
        self.ensure_one()
        v = self.sudo()
        out = defaultdict(float)
        asset = v.fixed_asset_id
        if asset:
            for line in asset.depreciation_line_ids.filtered(
                lambda ln: ln.book == "book"
                and ln.state == "posted"
                and date_from <= ln.period_start <= date_to
            ):
                out["depreciation"] += line.amount
        Entry = self.env["fix.asset.cost.entry"].sudo()
        entries = Entry.search(
            [
                ("vehicle_id", "=", v.id),
                ("cost_date", ">=", date_from),
                ("cost_date", "<=", date_to),
                ("state", "not in", ("rejected",)),
            ]
        )
        provisional = 0.0
        for entry in entries:
            if entry.state == "posted":
                key = entry.cost_type
                if key == "facility_work_order":
                    # a vehicle service done through the work-order spine is
                    # the PM's cost: kept apart so a report adding PM cost from
                    # the PM records does not count it twice
                    order = entry._m52_source()
                    if order and getattr(order, "vehicle_pm_id", None):
                        key = "facility_work_order_pm"
                out[key] += entry.amount
            else:
                provisional += entry.amount
        recoveries = (
            self.env["fix.asset.recovery"]
            .sudo()
            .search(
                [
                    ("source_model", "=", "fix.vehicle.accident"),
                    ("state", "in", ("approved", "in_payroll")),
                    (
                        "operating_unit_id",
                        "=",
                        (v.operating_unit_id or v.branch_id.operating_unit_id).id,
                    ),
                ]
            )
        )
        accidents = (
            self.env["fix.vehicle.accident"].sudo().browse(recoveries.mapped("source_res_id"))
        )
        mine = accidents.filtered(lambda a: a.vehicle_id == v).ids
        out["insurance_recovered"] = -sum(
            recoveries.filtered(lambda r: r.source_res_id in mine).mapped("amount")
        )
        result = {k: round(val, 2) for k, val in out.items()}
        result["total"] = round(sum(out.values()), 2)
        result["provisional"] = round(provisional, 2)
        return result
