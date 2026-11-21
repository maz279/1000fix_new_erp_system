# fix_rental_retirement — A05 remediation (2026-11-20, stream S1): the fleet
# unit's book value, its retirement and the loss write-off.
#
#   FIN-15 / M13-15  Book value is M49's when the unit is capitalised, else the
#                    straight-line value computed ON READ (never a stored
#                    figure that stopped ageing on the day it was saved).
#   M13-14 / M13-16  Retirement is its own request: always approved (no
#   XC-03 / BRU-RNT-15 zero-value bypass), jointly by the Corporate Services
#                    Head and the CFO (approval policy 'all'), behind the M06
#                    wipe gate (BRU-RNT-03, FR-RNT-039), with a required
#                    destination: resale (M14) or recycle (M18) (AUT-RNT-16).
#                    Executed, it publishes rental.asset_retired (interface I1)
#                    and hands the M49 fixed asset to its disposal - marked
#                    for M18 physical disposal when the route is recycle.
#   M13-13 / XC-04   The loss write-off is routed on the LOSS record (its own
#                    domain, rental_loss_writeoff), pinned to the valuation,
#                    customer and claim decision; a valuation below book
#                    value is part of what the approval covers.
#   M13-25           A unit's grade, unit and branch change only through
#                    turnaround, redeployment and their records.
#   XC-08            Cost, book value and revenue of a unit are visible to
#                    Rental Finance and Fleet Managers only.
from __future__ import annotations

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish

from . import rental_policy as policy

GROUP_CSH = "cd_rental_asset.group_rental_csh"
GROUP_CFO = "cd_rental_asset.group_rental_cfo"
COST_GROUPS = (
    "cd_rental_asset.group_rental_finance,cd_rental_asset.group_rental_fleet_manager,"
    "account.group_account_manager,base.group_system"
)
MATERIALS = [
    ("phone", "Mobile Phone"),
    ("laptop", "Laptop"),
    ("tablet", "Tablet"),
    ("accessory", "Accessory"),
    ("battery", "Battery"),
    ("other", "Other"),
]
LOSS_THRESHOLDS = [
    (50000.0, "tier_1"),
    (250000.0, "tier_2"),
    (1000000.0, "tier_3"),
    (float("inf"), "tier_4"),
]


def _refuse(message):
    raise ValidationError(message)


class FixRentalAsset(models.Model):
    _inherit = "fix.rental.asset"

    # XC-08: what a unit cost, is worth and earned is Finance's and the fleet
    # manager's to see - masked on the ORM (lists, forms, exports) for others
    purchase_cost = fields.Monetary(groups=COST_GROUPS)
    residual_value = fields.Monetary(groups=COST_GROUPS)
    daily_depreciation = fields.Monetary(groups=COST_GROUPS)
    total_repair_cost = fields.Monetary(groups=COST_GROUPS)
    cumulative_revenue = fields.Monetary(groups=COST_GROUPS)
    # FIN-15: computed on read, from M49 when capitalised
    net_book_value = fields.Monetary(
        compute="_compute_book_value", store=False, compute_sudo=True, groups=COST_GROUPS
    )
    accumulated_depreciation = fields.Monetary(
        compute="_compute_book_value", store=False, compute_sudo=True, groups=COST_GROUPS
    )
    branch_id = fields.Many2one(
        "fix.branch",
        string="Home Branch",
        index=True,
        help="The branch the unit is homed at (its unit must be the asset's operating unit)",
    )
    retirement_ids = fields.One2many("fix.rental.retirement", "asset_id", string="Retirements")

    # ---- book value -----------------------------------------------------
    def _book_value(self):
        """M49's net book value when the unit is capitalised there (S4's
        `_fix_book_value`: posted events only; nil once M49 disposed of it),
        else the IAS 16 straight-line value as of today (Dhaka) - a memo
        figure for a unit that is not on the fixed-asset register. A unit is
        never capitalised from here: D1 names no account to credit."""
        self.ensure_one()
        rec = self.sudo()
        fa = rec.fixed_asset_id
        if fa and fa.state in ("active", "disposed"):
            return round(fa._fix_book_value(), 2)
        from .fix_rental_fleet import _straight_line_nbv

        return _straight_line_nbv(
            rec.purchase_cost,
            rec.residual_value,
            rec.useful_life_days,
            rec.acquisition_date,
            policy.dhaka_today(self.env),
        )

    @api.depends(
        "purchase_cost",
        "residual_value",
        "useful_life_days",
        "acquisition_date",
        "fixed_asset_id",
    )
    def _compute_book_value(self):
        for rec in self:
            nbv = rec._book_value() if rec.id else 0.0
            cost = rec.purchase_cost or 0.0
            rec.net_book_value = nbv
            rec.accumulated_depreciation = round(max(cost - nbv, 0.0), 2) if cost else 0.0

    def _compute_depreciation(self):
        # the daily rate stays stored (it depends on the cost basis only); the
        # book value and accumulated depreciation are _compute_book_value's
        for rec in self:
            cost = rec.purchase_cost or 0.0
            residual = rec.residual_value or 0.0
            life = rec.useful_life_days or 1095
            daily = (cost - residual) / float(life) if life > 0 and cost > residual else 0.0
            rec.daily_depreciation = round(daily, 2)

    def _dofa_amount(self) -> float:
        self.ensure_one()
        return self._book_value()

    def _at_risk_with(self, vals):
        return super(FixRentalAsset, self.sudo())._at_risk_with(vals)

    # the unit's own DOFA request is no longer how it is retired
    def _approval_needed(self) -> bool:
        return False

    def action_request_approval(self, justification=None):
        raise UserError(
            "A fleet unit is retired through a Retirement Request (route, reason, wipe "
            "certificate), approved jointly by the Corporate Services Head and the CFO."
        )

    # ---- M13-25: grade, unit and branch are not typed after creation ------
    _MOVED_ONLY_BY_PROCESS = ("condition_grade", "operating_unit_id", "branch_id")

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self:
            locked |= set(self._MOVED_ONLY_BY_PROCESS) | {"retirement_reason"}
        return locked

    @api.constrains("branch_id", "operating_unit_id")
    def _check_branch_unit(self):
        for rec in self.filtered("branch_id"):
            if rec.operating_unit_id and rec.branch_id.operating_unit_id != rec.operating_unit_id:
                raise ValidationError(
                    "Unit %s: branch %s belongs to %s, not to the unit's operating unit %s."
                    % (
                        rec.name,
                        rec.branch_id.display_name,
                        rec.branch_id.operating_unit_id.name or "-",
                        rec.operating_unit_id.name,
                    )
                )

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self:
                moved = [
                    n
                    for n in self._MOVED_ONLY_BY_PROCESS
                    if n in vals and rec._fix_guard_differs(n, vals[n], rec[n])
                ]
                if moved:
                    _refuse(
                        "Unit %s: %s change only through its turnaround re-grade or a fleet "
                        "redeployment, not by editing the unit (M13-25)."
                        % (rec.name, ", ".join(self._fields[n].string or n for n in moved))
                    )
        return super().write(vals)

    # ---- retirement -------------------------------------------------------
    def _approved_retirement(self):
        self.ensure_one()
        return self.retirement_ids.filtered(
            lambda r: r.state == "approved" and r.approval_state == "approved"
        )[:1]

    def action_retire(self):
        """Retire on the unit's APPROVED retirement request (route, wipe gate,
        joint CSH + CFO approval). There is no other way to retire a unit."""
        for rec in self:
            retirement = rec._approved_retirement()
            if not retirement:
                raise UserError(
                    "%s has no approved retirement request: request one with its route "
                    "(resale / recycle) and reason; the Corporate Services Head and the CFO "
                    "approve it jointly (BRU-RNT-15)." % rec.name
                )
            retirement.action_retire()
        return True


class FixRentalTurnaround(models.Model):
    _inherit = "fix.rental.turnaround"

    def action_retire(self):
        """A unit retired from its turnaround still needs its approved
        retirement request: the turnaround no longer retires on its own."""
        for rec in self:
            if rec.state in ("ready", "retired"):
                raise UserError("Turnaround %s is %s." % (rec.name, rec.state))
            rec.rental_asset_id.action_retire()
        return True


class FixRentalRetirement(models.Model):
    """BRU-RNT-15 / FR-RNT-039/040 / AUT-RNT-16: the retirement of a fleet
    unit. Routed to the Corporate Services Head AND the CFO (every holder of
    either role approves: policy 'all'), never to whoever asked. The approval
    pins the unit, the route, the book value, the wipe certificate and the
    disposal data; any change voids it."""

    _name = "fix.rental.retirement"
    _description = "Rental Fleet Retirement"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.approvable.mixin"]
    _order = "id desc"

    _approval_domain = "rental_asset_retirement"
    _approval_routed = True
    _approval_apply_method = "_retirement_vote"

    name = fields.Char(required=True, default="New", readonly=True, copy=False)
    asset_id = fields.Many2one(
        "fix.rental.asset",
        string="Fleet Unit",
        required=True,
        index=True,
        ondelete="restrict",
        domain=[("status", "in", ("available", "maintenance"))],
    )
    company_id = fields.Many2one(related="asset_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(related="asset_id.operating_unit_id", store=True)
    currency_id = fields.Many2one(related="asset_id.currency_id")
    route = fields.Selection(
        [("resale", "Resale (M14 refurbishment)"), ("recycle", "Recycle (M18 e-waste)")],
        string="Destination",
        required=True,
        tracking=True,
        help="AUT-RNT-16: a retired unit always has a destination",
    )
    reason = fields.Text(string="Why Retire", required=True)
    weight_kg = fields.Float(string="Weight (kg)", digits=(10, 3))
    material = fields.Selection(MATERIALS, string="Material", default="other", required=True)
    data_wipe_certificate_id = fields.Many2one(
        "fix.data.wipe.certificate",
        string="Data Wipe Certificate (M06)",
        ondelete="restrict",
        help="BRU-RNT-03: a data-bearing unit is retired only on M06's verified certificate "
        "bound to its serial",
    )
    book_value = fields.Monetary(
        string="Book Value at Request",
        currency_field="currency_id",
        readonly=True,
        copy=False,
        groups=COST_GROUPS,
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("requested", "Awaiting Joint Approval"),
            ("approved", "Approved"),
            ("retired", "Retired"),
            ("rejected", "Rejected"),
        ],
        default="draft",
        required=True,
        readonly=True,
        tracking=True,
        copy=False,
    )
    retired_on = fields.Date(readonly=True, copy=False)
    disposal_id = fields.Many2one("fix.asset.disposal", readonly=True, copy=False)

    _GUARDED = frozenset({"state", "book_value", "retired_on", "disposal_id"})

    def _fix_guarded_fields(self) -> set:
        return set(super()._fix_guarded_fields()) | self._GUARDED

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if any(r.state != "draft" for r in self):
            locked |= {"asset_id", "route", "reason", "weight_kg", "material"}
        return locked

    def _approval_pinned_fields(self) -> set:
        return super()._approval_pinned_fields() | {
            "asset_id",
            "route",
            "weight_kg",
            "material",
            "data_wipe_certificate_id",
            "book_value",
        }

    def _approval_amount(self) -> float:
        self.ensure_one()
        return round(self.sudo().book_value or 0.0, 2)

    def _approval_needed(self) -> bool:
        # never a zero-value bypass (M13-16 / XC-03)
        return True

    def _approval_rule_value(self, rule, key):
        if key == "approval_policy":
            return "all"  # BRU-RNT-15: jointly, whatever a rule row says
        return super()._approval_rule_value(rule, key)

    def _approval_resolve(self, rule, tier):
        users = self.env["res.users"]
        for xmlid in (GROUP_CSH, GROUP_CFO):
            group = self.env.ref(xmlid, raise_if_not_found=False)
            holders = self._approval_holders(group)
            if not holders:
                return []
            users |= holders
        return self._approval_substitutes(users)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["name"] = (
                self.env["ir.sequence"].sudo().next_by_code("fix.rental.retirement")
                or "RNT-RET/New"
            )
        recs = super().create(vals_list)
        for rec in recs:
            rec.sudo()._guarded().write({"book_value": rec.asset_id._book_value()})
        return recs

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self.sudo().filtered(lambda r: r.state in ("retired", "rejected")):
                if any(
                    n in rec._fields
                    and rec._fields[n].store
                    and rec._fix_guard_differs(n, v, rec[n])
                    for n, v in vals.items()
                    if not n.startswith(("message_", "activity_"))
                ):
                    _refuse("Retirement %s is %s: it is final." % (rec.name, rec.state))
        res = super().write(vals)
        if "asset_id" in vals:
            for rec in self.filtered(lambda r: r.state == "draft"):
                rec.sudo()._guarded().write({"book_value": rec.asset_id._book_value()})
        return res

    # ---- gates --------------------------------------------------------
    def _wipe_denial(self):
        self.ensure_one()
        asset = self.asset_id.sudo()
        if asset.category not in policy.data_bearing_categories(self.env):
            return ""
        cert = self.data_wipe_certificate_id
        denial = cert._fix_certify_denial(asset.serial_no)
        if denial:
            return (
                "unit %s is data-bearing (%s): %s. Attach M06's verified wipe certificate for "
                "its serial (BRU-RNT-03, FR-RNT-039)." % (asset.name, asset.category, denial)
            )
        returns = [r.actual_return_date for r in asset.reservation_ids if r.actual_return_date]
        last_return = max(returns) if returns else None
        cert = cert.sudo()
        verified_on = (
            fields.Datetime.context_timestamp(self, cert.verified_at).date()
            if cert.verified_at
            else None
        )
        if last_return and verified_on and verified_on < last_return:
            return "wipe certificate %s was verified on %s, before the unit's last return (%s)" % (
                cert.name,
                verified_on,
                last_return,
            )
        return ""

    def _retire_denial(self):
        self.ensure_one()
        asset = self.asset_id.sudo()
        if asset.status in ("retired", "lost"):
            return "unit %s is already %s" % (asset.name, asset.status)
        if asset.status in ("out", "reserved", "transit"):
            return "unit %s is %s: bring it back first" % (asset.name, asset.status)
        if (
            self.env["fix.rental.reservation"]
            .sudo()
            .search_count(
                [
                    ("rental_asset_id", "=", asset.id),
                    ("state", "in", ("reserved", "delivered", "active")),
                ]
            )
        ):
            return "unit %s still has open bookings" % asset.name
        if not (self.reason or "").strip():
            return "the reason is missing"
        if self.route == "recycle" and not (self.weight_kg and self.weight_kg > 0):
            return "a unit routed to recycling needs its weight for the M18 collection"
        return self._wipe_denial()

    def action_request_approval(self, justification=None):
        for rec in self:
            if rec.state not in ("draft", "rejected"):
                raise UserError("Retirement %s is %s." % (rec.name, rec.state))
            denial = rec._retire_denial()
            if denial:
                raise UserError("Retirement %s cannot be requested: %s." % (rec.name, denial))
            rec.sudo()._guarded().write({"book_value": rec.asset_id._book_value()})
        result = super().action_request_approval(justification=justification)
        self._guarded().write({"state": "requested"})
        return result

    def _retirement_vote(self):
        """One vote of the joint approval (the engine runs it as a dry run
        for the earlier votes and applies it on the last one)."""
        self._approval_assert_routed()
        for rec in self:
            authority = rec._approval_authority_user()
            if not self.env.su and not (
                authority.has_group(GROUP_CSH) or authority.has_group(GROUP_CFO)
            ):
                raise UserError(
                    "A fleet retirement is approved by the Corporate Services Head and the CFO."
                )
            requester = rec.approval_request_id.sudo().requested_by_id
            if not self.env.su and (rec._approval_acting_users() & (rec.create_uid | requester)):
                raise UserError(
                    "Segregation of duties: you asked for retirement %s; you do not approve it."
                    % rec.name
                )
            denial = rec._retire_denial()
            if denial:
                raise UserError("Retirement %s cannot be approved: %s." % (rec.name, denial))
            if abs(rec.asset_id._book_value() - (rec.sudo().book_value or 0.0)) > 0.005:
                raise UserError(
                    "The unit's book value moved since retirement %s was requested; request it "
                    "again." % rec.name
                )
            rec._assert_joint(authority)
            rec._guarded().write({"state": "approved"})
        return True

    def _assert_joint(self, authority):
        """On the vote that completes the request: the signatures include a
        Corporate Services Head and a CFO who are two different people."""
        self.ensure_one()
        if self.env.su:
            return
        req = self.approval_request_id.sudo()
        task = self._approval_task()
        if not req or not task or not req._completed_by(task):
            return  # an earlier vote of the joint approval (dry run)
        signers = (
            req.task_ids.filtered(lambda t: t.decision == "approved" and t != task).mapped(
                lambda t: t.on_behalf_of_id or t.assigned_user_id
            )
            | authority
        )
        csh = signers.filtered(lambda u: u.has_group(GROUP_CSH))
        cfo = signers.filtered(lambda u: u.has_group(GROUP_CFO))
        if not csh or not cfo or (len(csh | cfo) < 2):
            raise UserError(
                "Retirement %s needs the Corporate Services Head AND the CFO, two different "
                "people (BRU-RNT-15)." % self.name
            )

    def _approval_on_rejected(self, comment):
        self._guarded().write({"state": "rejected"})
        for rec in self:
            rec.message_post(body="Retirement rejected: %s" % (comment or "no comment"))

    def _approval_clear_stamp(self, reason):
        self.filtered(lambda r: r.state in ("requested", "approved"))._guarded().write(
            {"state": "draft"}
        )
        return super()._approval_clear_stamp(reason)

    def action_retire(self):
        """Execute the approved retirement: the unit leaves the fleet for
        good, its M49 asset goes to disposal (for M18 when recycled), and
        rental.asset_retired tells M14 / M18 to receive it (interface I1)."""
        for rec in self:
            if rec.state != "approved" or rec.approval_state != "approved":
                raise UserError(
                    "Retirement %s is not approved by the Corporate Services Head and the CFO."
                    % rec.name
                )
            denial = rec._retire_denial()
            if denial:
                raise UserError("Retirement %s cannot be executed: %s." % (rec.name, denial))
            current = rec.asset_id._book_value()
            if abs(current - (rec.sudo().book_value or 0.0)) > 0.005:
                rec._approval_void(
                    "the book value moved from %.2f to %.2f after approval"
                    % (rec.sudo().book_value, current)
                )
                raise UserError(
                    "The unit's book value moved since retirement %s was approved; request it "
                    "again." % rec.name
                )
            rec._execute()
        return True

    def _execute(self):
        self.ensure_one()
        asset = self.asset_id.sudo()
        today = policy.dhaka_today(self.env)
        asset._guarded().write(
            {
                "status": "retired",
                "retired_on": today,
                "retirement_reason": self.reason,
            }
        )
        asset.turnaround_ids.filtered(
            lambda t: t.state not in ("ready", "retired")
        )._guarded().write({"state": "retired"})
        disposal = self.env["fix.asset.disposal"]
        fa = asset.fixed_asset_id
        note = ""
        if fa and fa.state == "active":
            # S6 wiring (S4 M49 source API): the M49 disposal of the route's
            # own kind. transfer_resale posts Dr refurbished stock / Cr cost
            # at the carrying amount (IAS 16.68A, no gain or loss) - the GL
            # side of the M14 intake, which records the same value as
            # transfer_in without posting; recycle derecognises the unit.
            # ewaste_route=False: M18 receives the unit from
            # rental.asset_retired (S3), so posting the disposal must not
            # open a second collection.
            disposal = fa._fix_open_disposal(
                "transfer_resale" if self.route == "resale" else "recycle",
                "Rental fleet retirement %s (%s): %s"
                % (self.name, dict(self._fields["route"].selection)[self.route], self.reason),
                source=asset,
                ewaste_route=False,
                device_id=asset.device_id.id or 0,
                weight_kg=self.weight_kg or 0.0,
                material=self.material or False,
                on_date=today,
            ).sudo()
            asset._guarded().write({"disposal_id": disposal.id or False})
        else:
            # owner decision D13 (21 Nov 2026): a unit the fixed-asset register
            # never held has no value in the books, so it is carried into M14
            # at nil - its memo straight-line value is shown, never posted
            note = (
                " The unit is not on the fixed-asset register (M49): no disposal is posted and "
                "it is carried to %s at nil value (owner decision D13; its straight-line memo "
                "value BDT %.2f is not in the books)."
                % (
                    "refurbished stock" if self.route == "resale" else "recycling",
                    self.sudo().book_value or 0.0,
                )
            )
        carried = float(self.sudo().book_value or 0.0) if disposal else 0.0
        self._guarded().write(
            {"state": "retired", "retired_on": today, "disposal_id": disposal.id or False}
        )
        branch = asset.branch_id
        publish(
            self.env,
            "rental.asset_retired",
            "fix.rental.asset",
            asset.id,
            {
                "asset_id": asset.id,
                "device_id": asset.device_id.id or False,
                "serial": asset.serial_no or "",
                "route": self.route,
                "weight_kg": float(self.weight_kg or 0.0),
                "material": self.material or "other",
                "company_id": asset.company_id.id,
                "operating_unit_id": asset.operating_unit_id.id or False,
                "branch_id": branch.id or False,
                # the value the books carry across: M49's posted book value,
                # nil for a unit never on the register (D13)
                "book_value": carried,
            },
        )
        body = "Retired by %s (%s route); M49 disposal %s.%s" % (
            self.name,
            self.route,
            disposal.display_name or "-",
            note,
        )
        asset.message_post(body=body)
        if note:
            self.message_post(body=body)


class FixRentalLoss(models.Model):
    """XC-04 / M13-13: the write-off of a lost unit is the LOSS record's own
    routed approval (domain rental_loss_writeoff), tiered on what is written
    off (the higher of the unit's book value and the agreed valuation) and
    pinned to the valuation, the customer and the claim decision. (The DOFA
    mixin is added on the model's own declaration in fix_rental_capture.)"""

    _inherit = "fix.rental.loss"

    _approval_domain = "rental_loss_writeoff"
    _approval_routed = True

    book_value_at_report = fields.Monetary(
        string="Book Value When Reported",
        currency_field="currency_id",
        readonly=True,
        copy=False,
        groups=COST_GROUPS,
    )

    def _fix_guarded_fields(self) -> set:
        return set(super()._fix_guarded_fields()) | {"book_value_at_report"}

    def _dofa_thresholds(self):
        return LOSS_THRESHOLDS

    def _dofa_amount(self) -> float:
        self.ensure_one()
        rec = self.sudo()
        return round(max(rec.book_value_at_report or 0.0, rec.valuation or 0.0), 2)

    def _dofa_amount_label(self) -> str:
        self.ensure_one()
        return "BDT %.2f (rental loss write-off)" % self._dofa_amount()

    @api.depends("valuation", "book_value_at_report")
    def _compute_dofa_tier_required(self):
        return super()._compute_dofa_tier_required()

    def _approval_pinned_fields(self) -> set:
        return super()._approval_pinned_fields() | {
            "reservation_id",
            "valuation",
            "kind",
            "claim_decision",
            "claim_ref",
            "police_report_ref",
        }

    def _approval_excluded(self):
        return (super()._approval_excluded() | self.sudo().reported_by).sudo()

    @api.model_create_multi
    def create(self, vals_list):
        recs = super().create(vals_list)
        for rec in recs:
            asset = rec.reservation_id.rental_asset_id
            rec.sudo()._guarded().write(
                {"book_value_at_report": asset._book_value() if asset else 0.0}
            )
        return recs

    def _writeoff_request_denial(self):
        self.ensure_one()
        if self.state != "open":
            return "loss %s is %s" % (self.name, self.state)
        if self.escalation_stage == "notice" and self.kind == "non_return":
            return (
                "a non-return is written off only after recovery has been attempted (escalate it)"
            )
        if self.kind == "theft" and not (self.police_report_ref or "").strip():
            return "a theft is written off only on its police report (BRU-RNT-10)"
        if not self.valuation or self.valuation <= 0:
            return "the agreed replacement valuation is missing"
        if not self.claim_decision:
            return "record the insurance claim or the decision not to claim (BRU-RNT-22)"
        if self.claim_decision == "claim" and not (self.claim_ref or "").strip():
            return "the insurance claim reference is missing"
        if self.claim_decision == "no_claim" and not (self.no_claim_reason or "").strip():
            return "the documented decision not to claim is missing"
        return ""

    def action_request_writeoff(self, justification=None):
        for rec in self:
            denial = rec._writeoff_request_denial()
            if denial:
                raise UserError("Loss %s: %s." % (rec.name, denial))
            below = (rec.sudo().book_value_at_report or 0.0) - (rec.valuation or 0.0)
            given = (justification or "").strip()
            text = given or (rec.dofa_justification or "").strip()
            if below > 0.005 and not given:
                raise UserError(
                    "Loss %s: the valuation is %.2f below the unit's book value; the approval "
                    "waives that difference, so justify it." % (rec.name, below)
                )
            rec.action_request_approval(
                justification=text or "%s: %s" % (rec.name, rec.circumstances)
            )
        return True

    def _writeoff_denial(self):
        denial = self._writeoff_request_denial()
        if denial:
            return denial
        if self.approval_state != "approved" or not self.dofa_approved:
            return "its write-off approval is not granted (request it; the approver decides it in the M63 inbox)"
        if self.reported_by == self.env.user:
            return "you reported this loss: another person writes it off"
        return ""

    def action_write_off(self):
        for rec in self:
            denial = rec._writeoff_denial()
            if denial:
                raise UserError("Loss %s cannot be written off: %s." % (rec.name, denial))
            rec._dofa_assert_approved("Rental loss write-off")
        Ledger = self.env["fix.rental.deposit"]
        for rec in self:
            res = rec.reservation_id
            asset = rec.rental_asset_id
            approver = rec.dofa_approved_by
            rec._guarded().write(
                {
                    "state": "written_off",
                    "written_off_on": policy.dhaka_today(self.env),
                    "approved_by": approver.id or self.env.uid,
                }
            )
            # the rental charge to date is billed like any other rental (FIN-07)
            today = policy.dhaka_today(self.env)
            res._guarded().write({"late_fee": res._late_fee_on(today)})
            billable, billed = res._unbilled()
            if abs(billable - billed) > 0.005:
                res._bill_rental(
                    "loss-rental-%d" % rec.id, reason="Rental %s: unit lost" % res.name
                )
            held = res._ledger_balance()
            take = round(min(held, rec.valuation), 2)
            ledger = Ledger.with_context(rental_release_uid=(approver or self.env.user).id)
            if take > 0:
                ledger._post(res, "forfeit", take, "Forfeited against lost unit (%s)" % rec.name)
            balance = round(max(held - take, 0.0), 2)
            if balance > 0:
                ledger._post(res, "refund", balance, "Deposit balance after loss write-off")
            excess = round(max(rec.valuation - take, 0.0), 2)
            res._guarded().write(
                {"state": "lost", "deposit_refunded": balance, "excess_billed": excess}
            )
            if excess > 0:
                res._hand_off_excess(
                    excess,
                    kind="loss",
                    key="loss-%d" % rec.id,
                    description="Rental %s: lost unit %s, valuation above the deposit "
                    "(compensation, outside the scope of VAT)" % (res.name, asset.name or ""),
                )
            rec._guarded().write({"forfeited_amount": take, "invoiced_amount": excess})
            if asset:
                asset.sudo()._guarded().write({"status": "lost", "retired_on": today})
                fa = asset.sudo().fixed_asset_id
                if fa and fa.state == "active":
                    result = fa.action_dispose() or {}
                    ids = result.get("disposal_ids") or []
                    if ids:
                        disposal = self.env["fix.asset.disposal"].sudo().browse(ids[0])
                        if disposal.state == "draft":
                            disposal.write(
                                {
                                    "incident_ref": rec.police_report_ref or rec.name,
                                    "insurance_claim_ref": rec.claim_ref or False,
                                    "reason": "Rental loss %s: %s" % (rec.name, rec.circumstances),
                                }
                            )
                        asset.sudo()._guarded().write({"disposal_id": ids[0]})
            publish(
                self.env,
                "rental.asset_lost",
                "fix.rental.loss",
                rec.id,
                {
                    "rental": res.name,
                    "asset": asset.name or "",
                    "kind": rec.kind,
                    "valuation": float(rec.valuation),
                    "claim_ref": rec.claim_ref or "",
                },
            )
        return True


class FixAssetDisposalRentalRetirement(models.Model):
    """S6 wiring: a retired rental unit's transfer to refurbished stock is
    booked twice by design - M49 posts the GL (Dr refurbished stock at the
    carrying amount) and M14's intake records the same carrying amount in the
    trade-in stock ledger as transfer_in, without posting. The two agree only
    if M49 posts the value the retirement published to M14: a disposal
    re-dated past another month's depreciation (or a revaluation) would
    debit stock with less (or more) than the ledger carries, and the resale
    COGS would credit stock with the ledger's figure. Such a posting is
    refused, naming both figures."""

    _inherit = "fix.asset.disposal"

    def _fix_rental_retirement(self):
        self.ensure_one()
        if self.source_model != "fix.rental.asset" or not self.source_res_id:
            return self.env["fix.rental.retirement"]
        return (
            self.env["fix.rental.retirement"]
            .sudo()
            .search([("disposal_id", "=", self.id), ("state", "=", "retired")], limit=1)
        )

    def action_post(self):
        for rec in self.filtered(lambda d: d.kind == "transfer_resale"):
            retirement = rec._fix_rental_retirement()
            if not retirement:
                continue
            asset = rec.asset_id.sudo()
            posting = round(
                (asset.cost or 0.0)
                - (asset.accumulated_depreciation or 0.0)
                - (asset.impairment_total or 0.0),
                2,
            )
            carried = round(retirement.book_value or 0.0, 2)
            if abs(posting - carried) > 0.005:
                raise UserError(
                    "Disposal %s would move %s to refurbished stock at BDT %.2f, but rental "
                    "retirement %s handed it to M14 resale at BDT %.2f (its trade-in stock "
                    "ledger carries that figure). Date the disposal on the retirement day "
                    "(%s) or reverse the later depreciation, so the stock account and the "
                    "ledger agree."
                    % (
                        rec.name,
                        asset.display_name,
                        posting,
                        retirement.name,
                        carried,
                        retirement.retired_on or "-",
                    )
                )
        return super().action_post()
