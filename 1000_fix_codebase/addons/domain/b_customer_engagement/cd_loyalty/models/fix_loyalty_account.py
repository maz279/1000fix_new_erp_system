# fix_loyalty_account — M10 Customer Loyalty Account (CD-M10-01).
import logging
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError

from libs.py.fix_events import publish

_logger = logging.getLogger(__name__)


class FixLoyaltyAccount(models.Model):
    _name = "fix.loyalty.account"
    _description = "Customer Loyalty Membership Account"
    # fix.approvable.mixin already sits in front of fix.guarded.mixin.
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.approvable.mixin"]

    # A03 audit M10-4 / R7: releasing a fraud freeze is a Tier 2 decision
    # taken from the approver's inbox. action_unfreeze is the apply method;
    # pressing it directly is refused.
    _approval_domain = "loyalty_release"
    _approval_apply_method = "action_unfreeze"
    _approval_group = "cd_entity_config.group_dofa_tier_2"
    _approval_routed = True

    def _fix_guarded_fields(self) -> set:
        # The balance is the sum of posted ledger lines and the state carries
        # the fraud lock. A direct write set a balance of 4,242,424 and
        # released a frozen wallet without Tier 2 (A03 audit).
        return super()._fix_guarded_fields() | {
            "state",
            "points_balance",
            "lifetime_points_earned",
            "lifetime_points_redeemed",
            "lifetime_spend_bdt",
            "frozen_at",
            "freeze_reason",
            "unlock_supervisor_id",
            "balance_drift",
            "balance_reconciled_at",
        }

    def _approval_needed(self) -> bool:
        return self.state == "frozen"

    def _approval_on_rejected(self, comment):
        for account in self:
            account.message_post(
                body="Fraud-lock release refused; the wallet stays frozen. %s" % (comment or "")
            )

    _order = "points_balance desc, create_date desc"

    # AS-03: Company and Operating Unit scoping
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        index=True,
        default=lambda self: self.env.company,
    )
    operating_unit_id = fields.Many2one(
        "operating.unit",
        string="Operating Unit",
        index=True,
    )

    name = fields.Char(
        string="Membership Number",
        required=True,
        readonly=True,
        copy=False,
        default=lambda self: self.env["ir.sequence"].next_by_code("fix.loyalty.account") or "NEW",
    )
    partner_id = fields.Many2one(
        "res.partner",
        string="Customer Party",
        required=True,
        ondelete="restrict",
        index=True,
        tracking=True,
    )
    program_id = fields.Many2one(
        "fix.loyalty.program",
        string="Programme",
        required=True,
        ondelete="restrict",
        index=True,
    )
    tier_id = fields.Many2one(
        "fix.loyalty.tier",
        string="Current Tier",
        index=True,
        tracking=True,
    )

    state = fields.Selection(
        [
            ("active", "Active"),
            ("frozen", "Frozen — Fraud Review"),
            ("suspended", "Suspended"),
            ("closed", "Closed"),
        ],
        default="active",
        required=True,
        tracking=True,
    )
    # REQ-10.6 velocity fraud lock
    freeze_reason = fields.Char(string="Freeze Reason", readonly=True, copy=False, tracking=True)
    frozen_at = fields.Datetime(string="Frozen On", readonly=True, copy=False)
    unlock_supervisor_id = fields.Many2one(
        "res.users", string="Unlocked By", readonly=True, copy=False, tracking=True
    )

    # Derived only (A03 audit M10-2): the sum of the posted ledger. A
    # reversed line keeps its points and its posted reversal cancels them,
    # so both states count. Nothing writes this field; marking a line
    # posted moves it, and reconcile_balance() proves it.
    points_balance = fields.Integer(
        string="Spendable Points Balance",
        compute="_compute_points_balance",
        store=True,
        readonly=True,
        tracking=True,
    )
    balance_drift = fields.Integer(
        string="Balance Drift Found",
        readonly=True,
        copy=False,
        help="Stored balance minus the posted-ledger sum at the last reconciliation "
        "that found a difference. Non-zero means the balance had been changed "
        "outside the ledger and was re-derived.",
    )
    balance_reconciled_at = fields.Datetime(readonly=True, copy=False)
    lifetime_points_earned = fields.Integer(
        string="Lifetime Points Earned",
        default=0,
        readonly=True,
    )
    lifetime_points_redeemed = fields.Integer(
        string="Lifetime Points Redeemed",
        default=0,
        readonly=True,
    )
    lifetime_spend_bdt = fields.Monetary(
        string="Lifetime Spend (BDT)",
        currency_field="currency_id",
        default=0.0,
        readonly=True,
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.ref("base.BDT", raise_if_not_found=False)
        or self.env.company.currency_id,
    )

    enrollment_date = fields.Date(
        string="Enrollment Date",
        default=fields.Date.context_today,
        readonly=True,
    )
    tier_upgraded_date = fields.Date(string="Last Tier Upgrade Date")

    ledger_ids = fields.One2many(
        "fix.loyalty.ledger",
        "account_id",
        string="Points Transactions",
    )
    voucher_ids = fields.One2many(
        "fix.loyalty.voucher",
        "account_id",
        string="Issued Vouchers",
    )

    _partner_prog_unique = models.Constraint(
        "UNIQUE (partner_id, program_id)",
        "Customer already has an active account in this loyalty programme.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("tier_id") and vals.get("program_id"):
                # Assign lowest qualification tier initially
                initial_tier = self.env["fix.loyalty.tier"].search(
                    [("program_id", "=", vals["program_id"]), ("active", "=", True)],
                    order="min_points_threshold asc, sequence asc",
                    limit=1,
                )
                if initial_tier:
                    vals["tier_id"] = initial_tier.id
        # A03 audit W5 (M33-3): the draft-party switch at enrolment. A no-op
        # under the default 'allow'; hasattr keeps it optional.
        Partner = self.env["res.partner"]
        if hasattr(Partner, "_fix_assert_party_usable_downstream"):
            Partner.browse(
                {vals["partner_id"] for vals in vals_list if vals.get("partner_id")}
            )._fix_assert_party_usable_downstream("loyalty enrolment")
        records = super().create(vals_list)
        for rec in records:
            publish(
                self.env,
                "loyalty.account_created",
                "fix.loyalty.account",
                rec.id,
                {
                    "account_no": rec.name,
                    "partner_id": rec.partner_id.id,
                    "program": rec.program_id.code,
                    "tier": rec.tier_id.code if rec.tier_id else "NONE",
                },
            )
        return records

    _BALANCE_STATES = ("posted", "reversed")

    @api.depends("ledger_ids.points", "ledger_ids.state")
    def _compute_points_balance(self):
        for account in self:
            account.points_balance = sum(
                line.points for line in account.ledger_ids if line.state in self._BALANCE_STATES
            )

    def _tier_qualifies(self, tier) -> bool:
        """Does this account meet `tier`'s thresholds?

        A threshold of 0 is "no requirement on this measure", not "met".
        Reading 0 as met put an account with 1 point in Platinum, because
        Platinum had a points floor but no spend floor and `0 >= 0` held
        (A03 audit M10-6). A tier with neither floor is the entry tier and
        qualifies everyone; otherwise either floor reached qualifies."""
        floors = []
        if tier.min_points_threshold:
            floors.append(self.lifetime_points_earned >= tier.min_points_threshold)
        if tier.min_spend_bdt:
            floors.append(self.lifetime_spend_bdt >= tier.min_spend_bdt)
        return any(floors) if floors else True

    def check_and_update_tier(self):
        """Evaluate qualification thresholds and upgrade tier if earned.

        Promotion only: a demotion is recalculate_tier's decision, which
        honours the retention window."""
        self.ensure_one()
        tiers = self.env["fix.loyalty.tier"].search(
            [("program_id", "=", self.program_id.id), ("active", "=", True)],
            order="min_points_threshold desc, min_spend_bdt desc",
        )
        for candidate_tier in tiers:
            if candidate_tier == self.tier_id:
                break  # already at the highest tier earned so far
            if self._tier_qualifies(candidate_tier):
                if self.tier_id != candidate_tier:
                    old_tier = self.tier_id.name if self.tier_id else "None"
                    self.write(
                        {
                            "tier_id": candidate_tier.id,
                            "tier_upgraded_date": fields.Date.today(),
                        }
                    )
                    self.message_post(
                        body=f"Congratulations! Upgraded from {old_tier} to {candidate_tier.name} tier."
                    )
                    publish(
                        self.env,
                        "loyalty.tier_upgraded",
                        "fix.loyalty.account",
                        self.id,
                        {
                            "partner_id": self.partner_id.id,
                            "account_no": self.name,
                            "old_tier": old_tier,
                            "new_tier": candidate_tier.code,
                        },
                    )
                break

    def action_suspend(self):
        self._guarded().write({"state": "suspended"})

    def action_activate(self):
        if any(account.state == "frozen" for account in self):
            # The fraud lock is released by action_unfreeze (Tier 2), not by
            # re-activating the wallet around it.
            raise UserError(
                "This wallet is frozen by the fraud check. Use 'Request Fraud-Lock "
                "Release' so a DOFA Tier 2 approver can release it, instead of "
                "re-activating it."
            )
        # A03 audit W5 (M33-3): the draft-party switch at activation.
        if hasattr(self.partner_id, "_fix_assert_party_usable_downstream"):
            self.partner_id._fix_assert_party_usable_downstream("an active loyalty account")
        self._guarded().write({"state": "active"})

    def action_close(self):
        self._guarded().write({"state": "closed"})

    # --- REQ-10.6 velocity fraud detection -------------------------------
    # "more than 3 earn transactions from disparate physical branches within
    # 120 minutes" freezes the wallet for investigation.
    _FRAUD_WINDOW_MINUTES = 120
    _FRAUD_MAX_ACCRUALS = 3

    def _check_velocity_fraud(self):
        """Freeze the wallet when accrual velocity crosses the REQ-10.6 limit."""
        window_start = fields.Datetime.now() - timedelta(minutes=self._FRAUD_WINDOW_MINUTES)
        for account in self:
            if account.state != "active":
                continue
            recent = self.env["fix.loyalty.ledger"].search(
                [
                    ("account_id", "=", account.id),
                    ("transaction_type", "=", "accrual"),
                    ("state", "=", "posted"),
                    ("create_date", ">=", window_start),
                ]
            )
            if len(recent) <= self._FRAUD_MAX_ACCRUALS:
                continue
            # Disparate branches are the stronger signal, but a burst from one
            # till is still a burst: the count alone trips the lock, and the
            # branch spread is recorded for the investigator.
            units = {r.operating_unit_id.id for r in recent if r.operating_unit_id}
            account._guarded().write(
                {
                    "state": "frozen",
                    "frozen_at": fields.Datetime.now(),
                    "freeze_reason": (
                        "Velocity check: %d accruals within %d minutes across %d "
                        "operating unit(s) (REQ-10.6)."
                        % (len(recent), self._FRAUD_WINDOW_MINUTES, len(units) or 1)
                    ),
                    # A new freeze needs a new release decision; the last
                    # release's 'approved' must not read as covering it.
                    "approval_state": "none",
                }
            )
            publish(
                self.env,
                "loyalty.wallet_frozen",
                "fix.loyalty.account",
                account.id,
                {
                    "account_no": account.name,
                    "partner_id": account.partner_id.id,
                    "accruals_in_window": len(recent),
                    "operating_units": len(units),
                },
            )

    def action_unfreeze(self):
        """Release a fraud lock: the M63 apply method (A03 audit M10-4, R7).

        Reached only from the approver's inbox task, after a requester asked
        for it with action_request_approval. Tier 2 authority is checked on
        the approver (the absent one when a delegate decides), and neither
        the approver nor a delegate may be the member."""
        self._approval_assert_routed()
        authority = self._approval_authority_user()
        acting = self._approval_acting_users()
        for account in self:
            if account.state != "frozen":
                raise UserError("Only a frozen wallet can be released.")
            if not authority.has_group("cd_entity_config.group_dofa_tier_2"):
                raise UserError(
                    "Releasing a fraud lock requires DOFA Tier 2 (Branch / "
                    "Operations Manager) authority."
                )
            if acting & account.partner_id.user_ids:
                raise UserError("A member cannot release the fraud lock on their own wallet.")
            account._guarded().write(
                {
                    "state": "active",
                    "unlock_supervisor_id": self.env.user.id,
                    "freeze_reason": False,
                    "frozen_at": False,
                }
            )
            account.message_post(
                body="Fraud lock released by %s after investigation." % self.env.user.name
            )

    # --- balance reconciliation (A03 audit M10-2) -------------------------
    def _ledger_sums(self) -> dict:
        """{account id: sum of its posted (and reversed) ledger points}, from SQL."""
        if not self.ids:
            return {}
        self.env.flush_all()
        self.env.cr.execute(
            "SELECT account_id, COALESCE(SUM(points), 0) FROM fix_loyalty_ledger "
            "WHERE account_id IN %s AND state IN %s GROUP BY account_id",
            (tuple(self.ids), self._BALANCE_STATES),
        )
        return dict(self.env.cr.fetchall())

    def _stored_balances(self) -> dict:
        if not self.ids:
            return {}
        self.env.cr.execute(
            "SELECT id, points_balance FROM fix_loyalty_account WHERE id IN %s",
            (tuple(self.ids),),
        )
        return {row[0]: row[1] or 0 for row in self.env.cr.fetchall()}

    def reconcile_balance(self) -> list:
        """Prove balance == sum of posted lines; flag and re-derive any drift.

        The ORM keeps the derived balance right, but a SQL script, an import
        or a pre-derivation row can still leave the stored column wrong. The
        stored value is read from the database, not the cache, so this sees
        what reports see. A drift is recorded (balance_drift, chatter and a
        loyalty.balance_drift event) before the balance is re-derived, so a
        repair never hides that something wrote around the ledger.
        Returns one dict per drifted account."""
        ledger = self._ledger_sums()
        stored = self._stored_balances()
        now = fields.Datetime.now()
        drifted = []
        for account in self:
            expected = ledger.get(account.id, 0)
            found = stored.get(account.id, 0)
            if found == expected:
                account._guarded().write({"balance_reconciled_at": now})
                continue
            drift = found - expected
            drifted.append(
                {"account": account.name, "stored": found, "ledger": expected, "drift": drift}
            )
            account._guarded().write({"balance_drift": drift, "balance_reconciled_at": now})
            account.message_post(
                body="Balance reconciliation: the stored balance was %d but the posted "
                "ledger sums to %d (drift %+d). The balance was re-derived from the "
                "ledger." % (found, expected, drift)
            )
            publish(
                self.env,
                "loyalty.balance_drift",
                "fix.loyalty.account",
                account.id,
                {"account_no": account.name, "stored": found, "ledger": expected, "drift": drift},
            )
        if drifted:
            stale = self.filtered(lambda a: ledger.get(a.id, 0) != stored.get(a.id, 0))
            stale.invalidate_recordset(["points_balance"])
            self.env.add_to_compute(self._fields["points_balance"], stale)
            self.env.flush_all()
        return drifted

    def action_reconcile_balance(self) -> dict:
        """Workspace button: reconcile these accounts and say what was found."""
        drifted = self.reconcile_balance()
        message = (
            "%d account(s) checked; every balance equals its posted ledger." % len(self)
            if not drifted
            else "%d of %d account(s) had drifted from the ledger and were re-derived."
            % (len(drifted), len(self))
        )
        # A client notification, so the backend button shows the answer; the
        # P03 workspace reads the same dict as the action result.
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Balance reconciliation",
                "message": message,
                "type": "warning" if drifted else "success",
                "sticky": bool(drifted),
            },
            "checked": len(self),
            "drifted": len(drifted),
            "detail": drifted,
        }

    @api.model
    def cron_reconcile_balances(self) -> int:
        """Daily proof that every balance is its ledger. Returns the drift count."""
        return len(self.search([]).reconcile_balance())

    # --- R8 event consumers ----------------------------------------------
    def _assert_system_consumer(self):
        # consume_* is a public model method, so JSON-RPC can reach it. Only
        # the relay (superuser) may apply an event: a forged party.merged
        # would otherwise move anyone's points to anyone.
        if not self.env.su:
            raise AccessError("Loyalty event consumers run only from the event relay.")

    @api.model
    def _order_earn_amount(self, order) -> float:
        """What the customer paid for the order, in BDT.

        The settled amount when one is recorded, else the approved estimates.
        A warranty, AMC or goodwill order settles at zero and earns nothing."""
        if order.amount_settled_bdt:
            return order.amount_settled_bdt
        return sum(
            order.estimate_ids.filtered(lambda e: e.state == "approved").mapped("grand_total")
        )

    @api.model
    def consume_service_order_closed(self, event: dict) -> dict:
        """R8 consumer of service_order.closed: earn on the closed order.

        No code called the earn rules, so a member earned nothing from
        repairs (A03 audit M10-10). Each of the customer's accounts earns once
        per order, ever: the receipt key is the order and the programme, not
        the event, so a re-published event cannot earn twice. The accrual is
        a system line (not manual-credit DOFA), but it still posts through
        action_post, so the REQ-10.6 velocity check runs on it."""
        self._assert_system_consumer()
        order_id = event.get("aggregate_id") or (event.get("payload") or {}).get("order_id")
        order = self.env["fix.service.order"].sudo().browse(int(order_id or 0)).exists()
        if not order or order.state != "closed":
            return {"accrued": 0, "reason": "not a closed service order"}
        amount = self._order_earn_amount(order)
        accounts = self.sudo().search(
            [("partner_id", "=", order.customer_id.id), ("program_id.active", "=", True)]
        )
        accrued = 0
        for account in accounts:
            accrued += account._accrue_order(order, amount, event)
        converted = self.env["fix.loyalty.referral.code"].sudo()._convert_on_first_service(order)
        return {"accrued": accrued, "referrals_converted": converted}

    def _accrue_order(self, order, amount: float, event: dict) -> int:
        """Earn on one closed order for this account. Returns points posted."""
        self.ensure_one()
        Receipt = self.env["fix.loyalty.event.receipt"]
        key = "earn:service_order:%d:%d" % (order.id, self.program_id.id)
        if Receipt._seen(key):
            return 0
        if self.state == "closed":
            Receipt._record(key, event, "No accrual: the account is closed.", self)
            return 0
        verdict = self.evaluate_earn(
            amount, category=order.order_category, channel=order.service_type
        )
        points = verdict["points"]
        if points <= 0:
            Receipt._record(key, event, "No points: %s" % verdict["basis"], self)
            return 0
        if verdict["point_class"] == "qualifying":
            self.sudo().award_qualifying_points(points, reason="Order %s" % order.name)
            Receipt._record(key, event, "%d tier-qualifying points." % points, self)
            return 0
        line = (
            self.env["fix.loyalty.ledger"]
            .sudo()
            .create(
                {
                    "account_id": self.id,
                    "transaction_type": "accrual",
                    "points": points,
                    "service_order_id": order.id,
                    "order_amount_bdt": amount,
                    "company_id": self.company_id.id,
                    "operating_unit_id": (
                        order.operating_unit_id or order.branch_id.operating_unit_id
                    ).id,
                    "notes": "Earned on closed service order %s. %s"
                    % (order.name, verdict["basis"]),
                }
            )
        )
        if self.state != "active":
            # A frozen or suspended wallet takes no postings. The earned line
            # is kept as a draft so it is not lost. It is not auto-posted on
            # release: staff post it once the investigation clears the
            # wallet (a system line, so posting it needs no manual DOFA).
            Receipt._record(
                key, event, "Held as draft: the account is %s." % self.state, self, line
            )
            return 0
        line.action_post()
        Receipt._record(key, event, "Posted %d points." % points, self, line)
        return points

    @api.model
    def consume_party_merged(self, event: dict) -> dict:
        """R8 consumer of party.merged: loyalty follows the surviving party.

        Loyalty accounts stayed on the tombstoned victim (A03 audit M10-11).
        Per programme: if only the victim has an account it is re-pointed to
        the survivor. If both do, the victim's balance moves to the survivor
        as posted merge_transfer lines (a debit on the victim, credits on the
        survivor that keep the original expiry dates) and the victim account
        is closed. Posted lines are never edited. Idempotent per event."""
        self._assert_system_consumer()
        payload = event.get("payload") or {}
        Receipt = self.env["fix.loyalty.event.receipt"]
        key = "party.merged:%s" % (event.get("event_id") or "")
        if Receipt._seen(key):
            return {"skipped": "already applied"}
        Partner = self.env["res.partner"].sudo().with_context(active_test=False)
        victim = Partner.browse(int(payload.get("victim_id") or 0)).exists()
        survivor = Partner.browse(
            int(payload.get("survivor_id") or event.get("aggregate_id") or 0)
        ).exists()
        if not victim or not survivor or victim == survivor:
            Receipt._record(key, event, "Ignored: the event names no victim/survivor pair.")
            return {"skipped": "no victim/survivor pair"}
        # A03 audit W1: the merge record, when there is one, is what the
        # reversal unwinds. A merge reversed before this delivery moves
        # nothing; a stray late delivery must not move points onto a party
        # that was already restored.
        Log = self.env["fix.party.repoint.log"]
        merge = Log._event_merge(event)
        if payload.get("merge_id") and not merge:
            Receipt._record(key, event, "Ignored: the merge no longer stands (reversed).")
            return {"skipped": "merge no longer stands"}
        outcomes = []
        for account in self.sudo().search([("partner_id", "=", victim.id)]):
            target = self.sudo().search(
                [("partner_id", "=", survivor.id), ("program_id", "=", account.program_id.id)],
                limit=1,
            )
            if target:
                outcomes.append(account._merge_into(target, event, merge))
            else:
                if merge:
                    # Logged, so party.merge_reversed gives the account back.
                    Log.repoint(merge, account, "partner_id", victim, survivor)
                else:
                    account.write({"partner_id": survivor.id})
                account.message_post(
                    body="Re-pointed from %s to %s by the party merge."
                    % (victim.name, survivor.name)
                )
                outcomes.append("%s re-pointed to the survivor." % account.name)
        Receipt._record(key, event, " ".join(outcomes) or "The victim had no loyalty account.")
        return {"outcomes": outcomes}

    def consume_merge_reversal_settlement(self, event: dict) -> dict:
        """R8 consumer of loyalty.merge_reversal_blocked / _shortfall.

        A merge reversal that cannot hand all the points back (a frozen
        wallet, or a survivor who spent them) needs a DOFA-approved
        adjustment. The alert had no reader (FF-48), so the settlement was
        left to chance: each Tier 2 holder in the account's company now gets
        a to-do on the restored account. Idempotent per event."""
        self._assert_system_consumer()
        Receipt = self.env["fix.loyalty.event.receipt"]
        key = "%s:%s" % (event.get("event_type") or "", event.get("event_id") or "")
        if Receipt._seen(key):
            return {"skipped": "already applied"}
        account = self.browse(int(event.get("aggregate_id") or 0)).exists()
        if not account:
            Receipt._record(key, event, "Ignored: the account no longer exists.")
            return {"assigned": 0}
        payload = event.get("payload") or {}
        if event.get("event_type") == "loyalty.merge_reversal_shortfall":
            note = (
                "Merge reversal returned %s of %s points from %s. Settle the %s-point "
                "shortfall by a DOFA-approved adjustment."
                % (
                    payload.get("returned"),
                    payload.get("points"),
                    payload.get("survivor_account"),
                    int(payload.get("points") or 0) - int(payload.get("returned") or 0),
                )
            )
        else:
            note = (
                "Merge reversal could not return the points from %s: one of the wallets "
                "is not active. Settle by a DOFA-approved adjustment."
                % payload.get("survivor_account")
            )
        group = self.env.ref(self._approval_group, raise_if_not_found=False)
        users = (
            group.sudo().all_user_ids.filtered(
                lambda u: u.active and not u.share and account.company_id in u.company_ids
            )
            if group
            else self.env["res.users"]
        )
        for user in users:
            account.activity_schedule(
                "mail.mail_activity_data_todo",
                summary="Settle loyalty points after a merge reversal",
                note=note,
                user_id=user.id,
            )
        if not users:
            _logger.warning("loyalty account %s: %s, but nobody holds Tier 2", account.id, note)
        account.message_post(body=note)
        Receipt._record(key, event, "%d settlement to-do(s): %s" % (len(users), note), account)
        return {"assigned": len(users)}

    def _transfer_allocations(self, balance: int) -> list:
        """[(points, expiry_date)] covering `balance`, newest credit first.

        Redemption and expiry consume the oldest points first, so what is
        left is the newest credits. Moving them with their own expiry dates
        keeps the merge from extending any point's life."""
        self.ensure_one()
        credits = self.env["fix.loyalty.ledger"].search(
            [
                ("account_id", "=", self.id),
                ("state", "=", "posted"),
                ("points", ">", 0),
                ("points_expired", "=", False),
            ],
            order="id desc",
        )
        out, left = [], balance
        for line in credits:
            if left <= 0:
                break
            take = min(line.points, left)
            out.append((take, line.expiry_date))
            left -= take
        if left > 0:
            out.append((left, False))
        return out

    def _merge_into(self, target, event: dict, merge=None) -> str:
        """Move this (victim) account's balance to `target` and close this one.

        With the merge record, the transfer is recorded
        (fix.loyalty.merge.transfer) so a reversal can undo it (A03 audit W1)."""
        self.ensure_one()
        balance = self.points_balance
        if balance > 0 and (self.state != "active" or target.state != "active"):
            # A frozen wallet's points are under fraud review; moving them
            # would make them spendable on the survivor. A steward settles it.
            note = (
                "Party merge: %d points NOT moved from %s (%s) to %s (%s). Release "
                "the hold, then transfer by a DOFA-approved adjustment."
                % (balance, self.name, self.state, target.name, target.state)
            )
            for account in self | target:
                account.message_post(body=note)
            publish(
                self.env,
                "loyalty.merge_transfer_blocked",
                "fix.loyalty.account",
                self.id,
                {"victim_account": self.name, "survivor_account": target.name, "points": balance},
            )
            return note
        Ledger = self.env["fix.loyalty.ledger"].sudo()
        lines = Ledger
        reason = "Party merge (event %s): %s into %s." % (
            event.get("event_id"),
            self.partner_id.name,
            target.partner_id.name,
        )
        if balance > 0:
            allocations = self._transfer_allocations(balance)
            debit = Ledger.create(
                {
                    "account_id": self.id,
                    "transaction_type": "merge_transfer",
                    "points": -balance,
                    "company_id": self.company_id.id,
                    "notes": "%s Balance moved to account %s." % (reason, target.name),
                }
            )
            debit.action_post()
            lines |= debit
            for points, expiry in allocations:
                credit = Ledger.create(
                    {
                        "account_id": target.id,
                        "transaction_type": "merge_transfer",
                        "points": points,
                        "expiry_date": expiry,
                        "company_id": target.company_id.id,
                        "notes": "%s Balance received from account %s." % (reason, self.name),
                    }
                )
                credit.action_post()
                lines |= credit
        qualifying = self.qualifying_points_balance or 0
        if qualifying:
            target.sudo().award_qualifying_points(
                qualifying, reason="Party merge from %s" % self.name
            )
            self.sudo().write({"qualifying_points_balance": 0})
        self._guarded().write({"state": "closed"})
        if merge:
            self.env["fix.loyalty.merge.transfer"]._record(
                merge, self, target, max(balance, 0), qualifying, lines
            )
        self.message_post(body="%s Account closed." % reason)
        target.message_post(body="%s %d points received." % (reason, balance))
        publish(
            self.env,
            "loyalty.account_merged",
            "fix.loyalty.account",
            target.id,
            {"victim_account": self.name, "survivor_account": target.name, "points": balance},
        )
        return "%s merged into %s (%d points)." % (self.name, target.name, balance)
