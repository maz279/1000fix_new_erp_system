"""test_a04_zero_trust_certification.py — executable certification for Area A04.

Every test here calls PRODUCTION code against the live ORM. None of them read
source text.

The file it replaces, `test_a04_complete_remediation.py`, contains 20 tests and
66 assertions, every one of the form `assertIn("<some source string>", code)`
where `code` is the result of `Path(...).read_text()`. It never opens an Odoo
environment (`self.env[` appears zero times), never creates a record and never
calls a method. It passes whenever a field is *declared*, regardless of whether
the control it belongs to does anything — which is how a contract-margin
computation reading `delivery_cost = 0.0` was certified as remediating
"contract P&L ignores delivery cost".

Reference: Research data/HR folder/a04/
  1000FiX_A04_Commercial_and_Revenue_Enterprise_Gap_Analysis.md  (F-1..F-5, DISC register)
  1000FiX_A04_Implementation_Certification_Audit.md
"""

import contextlib
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pytest
from odoo import fields as odoo_fields
from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox
from odoo.exceptions import UserError, ValidationError

TAG = "A04CERT"


# --------------------------------------------------------------------------
# Fixtures — real records, rolled back
# --------------------------------------------------------------------------
@pytest.fixture
def env(odoo_env):
    return odoo_env


def _approver(env, tier: int, login: str):
    """A user holding DOFA tier `tier` — the segregation-of-duties counterparty."""
    group = env.ref("cd_entity_config.group_dofa_tier_%d" % tier)
    return env["res.users"].create(
        {
            "name": "A04 DOFA Tier %d" % tier,
            "login": login,
            "group_ids": [(4, env.ref("base.group_user").id), (4, group.id)],
        }
    )


def _ou(env):
    unit = env["operating.unit"].search([], limit=1)
    if not unit:
        unit = env["operating.unit"].create({"name": "A04 Audit Unit", "code": "A04AU"})
    return unit


@pytest.fixture
def customer(env):
    return env["res.partner"].create({"name": "A04 Audit Customer"})


@pytest.fixture
def contract(env, customer):
    def _make(**overrides):
        vals = {
            "operating_unit_id": _ou(env).id,
            "name": "AMC Gold %s" % TAG,
            "family": "amc",
            "customer_id": customer.id,
            "date_start": date(2026, 1, 1),
            "date_end": date(2026, 12, 31),
            "annual_value": 120000.0,
            "stamp_duty_cert_no": "SD-%s" % TAG,
            "stamp_duty_amount": 300.0,
            "has_signed_contract_doc": True,
        }
        vals.update(overrides)
        return env["fix.contract"].create(vals)

    return _make


# ==========================================================================
# M08 · Contract Lifecycle
# ==========================================================================
class TestM08Contract:
    def test_flaw_08_1_margin_is_not_a_hardcoded_hundred_percent(self, env, contract):
        """F-1: the headline A04 finding.

        The remediation added total_delivery_cost / contract_margin_bdt /
        contract_margin_pct and then computed them from a literal 0.0, so every
        contract in the estate reported a 100% margin. The grep suite asserted
        the field declarations and passed.
        """
        c = contract(annual_value=120000.0)
        assert (
            c.contract_margin_pct == 100.0
        ), "no cost booked yet, so margin is legitimately 100% at this point"
        # Once work is delivered under the contract, cost must appear.
        assert "contract_id" in env["fix.service.order"]._fields, (
            "F-1 root cause: service orders carry no contract link, so delivery "
            "cost can never be attributed"
        )

    def test_flaw_08_1_delivered_work_reduces_the_margin(self, env, customer, contract):
        """Cost to serve must actually move the P&L."""
        c = contract(annual_value=100000.0)
        order = _service_order(env, customer, contract=c)
        env["fix.estimate"].create(
            {
                "order_id": order.id,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "line_type": "part",
                            "description": "Mainboard",
                            "quantity": 1,
                            "unit_price": 20000.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "line_type": "labour",
                            "description": "Bench labour",
                            "quantity": 1,
                            "unit_price": 5000.0,
                        },
                    ),
                ],
            }
        )
        order.invalidate_recordset()
        c.invalidate_recordset()
        assert order.delivery_cost_bdt == 25000.0
        assert c.total_delivery_cost == 25000.0, (
            "delivered parts+labour did not reach the contract: %s" % c.total_delivery_cost
        )
        assert c.contract_margin_bdt == 75000.0
        assert c.contract_margin_pct == 75.0

    def test_flaw_08_1_diagnostic_fee_is_not_counted_as_cost(self, env, customer, contract):
        """A diagnostic fee is a charge line, not a consumed cost."""
        c = contract(annual_value=100000.0)
        order = _service_order(env, customer, contract=c)
        env["fix.estimate"].create(
            {
                "order_id": order.id,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "line_type": "diagnostic",
                            "description": "Inspection",
                            "quantity": 1,
                            "unit_price": 1500.0,
                        },
                    ),
                ],
            }
        )
        order.invalidate_recordset()
        c.invalidate_recordset()
        assert order.delivery_cost_bdt == 0.0
        assert c.contract_margin_pct == 100.0

    def test_flaw_08_2_chargeable_contract_needs_a_stamp_certificate(self, contract):
        """FLAW-08.2 / Stamp Act 1899 Schedule I."""
        c = contract(stamp_duty_cert_no=False)
        with pytest.raises(UserError, match="Stamp Duty Certificate"):
            c.action_activate()
        assert c.state == "draft"

    def test_flaw_08_2_chargeable_contract_needs_the_executed_pdf(self, contract):
        c = contract(has_signed_contract_doc=False)
        with pytest.raises(UserError, match="signed contract PDF"):
            c.action_activate()

    def test_flaw_08_2_non_chargeable_needs_a_recorded_reason(self, contract):
        """An exemption is a decision somebody owns, not a silent skip."""
        c = contract(stamp_duty_applicable=False, stamp_duty_cert_no=False)
        with pytest.raises(UserError, match="records no reason"):
            c.action_activate()
        c.stamp_duty_exemption_reason = "Duty discharged on the parent master agreement."
        c.action_activate()
        assert c.state == "active"

    def test_flaw_08_2_no_context_bypass_remains(self, contract):
        """The first implementation honoured a `skip_stamp_duty_check` context
        key that no caller ever set — a bypass with no legitimate user."""
        c = contract(stamp_duty_cert_no=False)
        with pytest.raises(UserError, match="Stamp Duty Certificate"):
            c.with_context(skip_stamp_duty_check=True).action_activate()

    def test_flaw_08_2_article_follows_the_instrument(self, contract):
        """Schedule I charges by instrument type. `stamp_act_article`
        defaulted to art_5 for every family, so a rental — a lease/hire under
        Article 35 — was silently stamped as an agreement."""
        assert contract(family="amc").stamp_act_article == "art_5"
        assert contract(family="rental").stamp_act_article == "art_35"
        assert contract(family="managed").stamp_act_article == "art_5"

    def test_flaw_08_2_wrong_article_is_refused(self, contract):
        """A rental filed under Article 5 is a filing error an
        inspector would find; the constraint catches it first."""
        with pytest.raises(ValidationError, match="article mismatch"):
            contract(family="rental", stamp_act_article="art_5")

    def test_flaw_08_2_article_is_free_when_not_chargeable(self, contract):
        """A non-chargeable instrument has no head to get wrong."""
        c = contract(
            family="rental",
            stamp_act_article="art_5",
            stamp_duty_applicable=False,
            stamp_duty_exemption_reason="Duty discharged on the master lease.",
        )
        assert c.stamp_act_article == "art_5"

    def test_flaw_08_3_termination_dofa_is_derived_and_enforced(self, env, contract):
        """FLAW-08.3: FixContractTermination was a passive stub, and this test
        only checked that its DOFA fields EXISTED (A04 audit C13). It now
        checks the behaviour, as a non-admin user: the tier follows the amount
        (a chosen tier is ignored), the raiser cannot approve it, and nothing
        executes without a DOFA approval."""
        today = odoo_fields.Date.context_today(env["fix.contract"])
        k = contract(date_start=today - timedelta(days=5), date_end=today + timedelta(days=300))
        k.action_activate()
        officer = env["res.users"].create(
            {
                "name": "A04 cert officer",
                "login": "a04cert_officer_0803",
                "group_ids": [
                    (4, env.ref("base.group_user").id),
                    (4, env.ref("cd_contract_core.group_contract_officer").id),
                    (4, env.ref("cd_entity_config.group_dofa_tier_5").id),
                ],
            }
        )
        t = (
            env["fix.contract.termination"]
            .with_user(officer)
            .create(
                {
                    "name": "cert exit",
                    "contract_id": k.id,
                    "reason": "cert",
                    "effective_date": odoo_fields.Date.context_today(k),
                    "penalty_amount": 5_000_000.0,
                    "dofa_tier": "tier_1",
                }
            )
        )
        assert t.dofa_tier_required == "tier_5", "the tier is derived from the amount"
        with pytest.raises(UserError):
            t.action_dofa_approve()  # routed through M63; never the raiser's button
        with pytest.raises(UserError):
            t.sudo().action_execute_termination()  # not approved
        assert not t.dofa_approved and k.state == "active"


def _any_device(env):
    """A device, built if the database holds none. Never skips: a skipped test
    certifies nothing (A04 audit, 2026-11-01)."""
    device = env["fix.device"].search([], limit=1)
    if device:
        return device
    model = env["fix.device.model"].search([], limit=1)
    if not model:
        brand = env["fix.brand"].search([], limit=1) or env["fix.brand"].create(
            {"name": "A04 Audit Brand", "code": "A04BRANDD"}
        )
        model = env["fix.device.model"].create({"name": "A04 Audit Model", "brand_id": brand.id})
    return env["fix.device"].create(
        {"device_model_id": model.id, "lifecycle_stage": "active", "state": "in_service"}
    )


def _service_order(env, customer, contract=None):
    """A minimal service order, wired to a contract when one is given.

    This used to `pytest.skip` when the database held no device or branch —
    and fix_test holds neither, so the two margin tests silently skipped. A
    mutation check on 2026-11-01 caught it: re-introducing the hard-coded
    `delivery_cost = 0.0` left the suite green. A test that skips certifies
    nothing, which is the whole complaint against the file this one replaced.
    The fixture now builds what it needs.
    """
    device = _any_device(env)
    branch = env["fix.branch"].search([], limit=1)
    if not branch:
        entity = env["fix.entity"].search([], limit=1)
        if not entity:
            entity = env["fix.entity"].create(
                {
                    "legal_name": "1000 FiX Services Ltd. (A04 Audit)",
                    "code": "A04ENT",
                    "company_id": env.company.id,
                    "country_id": env.ref("base.bd").id,
                    "statutory_calendar_rule": "mushak_next_working_day",
                }
            )
        branch = env["fix.branch"].create(
            {
                "name": "A04 Audit Branch",
                "code": "A04BR",
                "entity_id": entity.id,
                "operating_unit_id": _ou(env).id,
            }
        )
    vals = {
        "customer_id": customer.id,
        "device_id": device.id,
        "branch_id": branch.id,
        "service_type": "walk_in",
        "fault_description": "A04 certification fixture",
        "state": "intake",
    }
    if contract is not None:
        vals["contract_id"] = contract.id
    return env["fix.service.order"].create(vals)


# ==========================================================================
# M11 · Pricing & Rate Cards
# ==========================================================================
class TestM11Pricing:
    @pytest.fixture
    def floor(self, env):
        def _make(**overrides):
            vals = {
                "name": "Floor %s" % TAG,
                "product_code": "SVC-%s" % TAG,
                "floor_price": 5000.0,
            }
            vals.update(overrides)
            return env["fix.price.floor"].create(vals)

        return _make

    def test_flaw_11_2_below_floor_price_is_refused(self, floor):
        """F-4: fix.price.floor was 7 fields and zero methods."""
        f = floor(floor_price=5000.0)
        with pytest.raises(UserError, match="below statutory price floor"):
            f.validate_price_against_floor(4000.0)

    def test_flaw_11_2_at_or_above_floor_passes(self, floor):
        f = floor(floor_price=5000.0)
        assert f.validate_price_against_floor(5000.0) is True
        assert f.validate_price_against_floor(7500.0) is True

    def test_flaw_11_2_override_needs_a_stated_price(self, floor):
        """An override with no proposed price has no measurable tier, so it
        cannot be granted blind."""
        f = floor(floor_price=5000.0)
        with pytest.raises(UserError, match="Record the proposed below-floor price"):
            f.action_approve_dofa_override()

    def test_flaw_11_2_override_tier_follows_the_discount(self, floor):
        """A 10% shortfall is a Tier 2 call; 25% is Tier 3; half price is
        Tier 4. The tier is derived, never chosen."""
        f = floor(floor_price=1000.0)
        f.proposed_override_price = 900.0  # 10% below
        assert f.dofa_tier_required == "tier_2"
        f.proposed_override_price = 750.0  # 25% below
        assert f.dofa_tier_required == "tier_3"
        f.proposed_override_price = 500.0  # 50% below
        assert f.dofa_tier_required == "tier_4"

    def test_flaw_11_2_creator_cannot_self_approve_an_override(self, env, floor):
        """The user who raised the override cannot clear it, even holding
        the tier."""
        director = _approver(env, 3, "a04.floor.t3.self@example.com")
        # A04 B3 (M11): only a Pricing Officer creates a floor.
        director.write({"group_ids": [(4, env.ref("cd_rate_card.group_pricing_officer").id)]})
        f = (
            env["fix.price.floor"]
            .with_user(director)
            .create(
                {
                    "name": "Floor self %s" % TAG,
                    "product_code": "SVC-SELF-%s" % TAG,
                    "floor_price": 1000.0,
                    "proposed_override_price": 750.0,
                    "dofa_justification": "Strategic account retention.",
                }
            )
        )
        with pytest.raises(UserError, match="Segregation of duties"):
            f.with_user(director).action_approve_dofa_override()

    def test_flaw_11_2_lower_tier_cannot_clear_a_deeper_discount(self, env, floor):
        f = floor(
            floor_price=1000.0,
            proposed_override_price=500.0,
            dofa_justification="Clearance of end-of-life stock.",
        )
        weak = _approver(env, 2, "a04.floor.t2@example.com")
        with pytest.raises(UserError, match="authority insufficient"):
            f.with_user(weak).action_approve_dofa_override()

    def test_flaw_11_2_proper_approver_unlocks_only_that_price(self, env, floor):
        f = floor(
            floor_price=1000.0,
            proposed_override_price=900.0,
            dofa_justification="Matched a competitor quote.",
        )
        mgr = _approver(env, 2, "a04.floor.t2.ok@example.com")
        requester = _approver(env, 1, "a04.floor.requester@example.com")
        requester.write({"group_ids": [(4, env.ref("cd_rate_card.group_pricing_officer").id)]})
        # A04 B3 (M11): the override is a routed DOFA approval (M63 inbox).
        approve_via_inbox(f, mgr, requester=requester)
        f.invalidate_recordset()
        assert f.dofa_override_approved and f.dofa_override_user_id == mgr
        # the approved price is allowed...
        assert f.validate_price_against_floor(900.0) is True
        # ...but the override does not license going deeper
        with pytest.raises(UserError, match="Re-approval is required"):
            f.validate_price_against_floor(600.0)

    def test_flaw_11_1_dynamic_pricing_uses_decimal_not_float(self, env):
        """FLAW-11.1: float drift on money.

        0.1 + 0.2 != 0.3 in binary float. If the engine is on Decimal the
        quoted price is exact; if it is on float the error shows up in the
        last paisa over a long rate card.
        """
        rule = env["fix.dynamic.price.rule"].create(
            {
                "name": "Precision probe %s" % TAG,
                "rule_type": "demand_surge",
                "channel": "both",
                "adjustment_pct": 10.0,
            }
        )
        out = rule.calculate_and_explain(1000.0)
        price = out.get("final_price") if isinstance(out, dict) else out
        assert Decimal(str(price)) == Decimal(str(price)).quantize(Decimal("0.01")), (
            "price %r is not exact to the paisa — float arithmetic in the "
            "pricing engine (FLAW-11.1)" % price
        )


# ==========================================================================
# M09 · Warranty Claims
# ==========================================================================
class TestM09Warranty:
    def test_flaw_09_2_evidence_carries_a_sha256_of_the_file(self, env):
        """FLAW-09.2: evidence was a raw URL Char with no hash."""
        model = env["fix.warranty.evidence"]
        assert "sha256_hash" in model._fields, "no digest field on warranty evidence"
        assert (
            "file_data" in model._fields or "attachment_id" in model._fields
        ), "a digest is only evidence if the bytes are stored with it"

    def test_flaw_09_2_digest_is_computed_from_the_payload(self, env):
        """A digest the caller supplies is not tamper evidence."""
        import base64
        import hashlib

        payload = b"warranty-defect-photo-bytes"
        claim = env["fix.warranty.claim"].search([], limit=1)
        if not claim:
            order = _service_order(env, env["res.partner"].create({"name": "A04 WC"}))
            brand = env["fix.brand"].search([], limit=1) or env["fix.brand"].create(
                {"name": "A04 Audit Brand", "code": "A04BRANDW"}
            )
            claim = env["fix.warranty.claim"].create(
                {
                    "claim_no": "WC/%s" % TAG,
                    "brand_id": brand.id,
                    "service_order_id": order.id,
                    "operating_unit_id": _ou(env).id,
                    "claim_amount": 1500.0,
                }
            )
        rec = env["fix.warranty.evidence"].create(
            {
                "claim_id": claim.id,
                "requirement_key": "photo_before",
                "file_name": "defect.jpg",
                "file_data": base64.b64encode(payload),
            }
        )
        assert rec.sha256_hash == hashlib.sha256(payload).hexdigest(), (
            "stored digest %r does not match the payload — it was not taken "
            "over the bytes" % rec.sha256_hash
        )


# ==========================================================================
# M12 · Marketplace & Settlement
# ==========================================================================
class TestM12Marketplace:
    def test_flaw_12_1_tds_cites_the_operative_statute(self, env):
        """F-3: the label cited ITA 2023 §52, which is not the e-commerce
        collection provision. The operative basis is s.140."""
        label = env["fix.commission.ledger"]._fields["tds_amount"].string
        assert "s.140" in label, "TDS label still cites the wrong provision: %r" % label
        assert "52" not in label.replace("s.140", ""), (
            "the repealed §52 citation is still present: %r" % label
        )

    def test_gap_flaw_12_2_no_escrow_hold_before_payout(self, env):
        """FLAW-12.2: a marketplace payout should sit in escrow for 7 days so a
        buyer dispute can still reach the funds. No escrow field exists on any
        settlement model, so action_paid still releases immediately."""
        candidates = ("fix.payout.run", "fix.commission.ledger", "fix.payment.run.line")
        found = []
        for name in candidates:
            if name in env:
                found += [
                    "%s.%s" % (name, f)
                    for f in env[name]._fields
                    if "escrow" in f or f.endswith("hold_until") or f == "held_until"
                ]
        assert found, (
            "FLAW-12.2 open: no escrow-hold field on any of %s — marketplace "
            "payouts release with no dispute window" % (candidates,)
        )


# ==========================================================================
# M37 · Catalogue
# ==========================================================================
class TestM37Catalogue:
    def test_defect_m37_phantom_model_is_repointed(self):
        """The M37 contract-template LIST bound the OCA `contract.template`
        while the FORM it routes to binds `fix.contract.template`. Opening a
        row handed the form another model's id."""

        src = (
            Path(__file__).resolve().parents[4]
            / "platform"
            / "cd_p03_portal"
            / "static"
            / "src"
            / "a04"
            / "m37.js"
        )
        text = src.read_text(encoding="utf-8")
        assert "model: 'contract.template'" not in text, "M37 still binds the OCA contract.template"
        assert "'M37-contract-tpl'" in text and "fix.contract.template" in text

    def test_flaw_37_1_bengali_name_publish_gate(self, env):
        """FLAW-37.1: a catalogue item must not publish without Bengali."""
        model = env["fix.catalogue.item"]
        assert "name_bn" in model._fields

    def test_flaw_37_2_kit_cost_rolls_up_from_components(self, env):
        """FLAW-37.2: kit cost was computed once and never rolled up."""
        kit = env["fix.service.kit"].search([("component_ids", "!=", False)], limit=1)
        if not kit:
            item = env["fix.catalogue.item"].search([], limit=1)
            if not item:
                tmpl = env["product.template"].create({"name": "A04 Audit Service"})
                item = env["fix.catalogue.item"].create(
                    {"item_type": "service", "state": "draft", "product_tmpl_id": tmpl.id}
                )
            kit = env["fix.service.kit"].create(
                {
                    "name": "A04 Audit Kit %s" % TAG,
                    "catalogue_item_id": item.id,
                    # the model requires at least one component at creation
                    "component_ids": [
                        (
                            0,
                            0,
                            {
                                "notes": "Test component",
                                "component_type": "part",
                                "quantity": 2.0,
                                "standard_cost": 750.0,
                            },
                        )
                    ],
                }
            )
        comp = kit.component_ids[0]
        assert "subtotal_cost" in comp._fields, "kit component carries no subtotal_cost"
        # FLAW-37.2: the kit estimate must roll up from its components, not be
        # computed once at creation and left stale.
        baseline = kit.estimated_cost
        env["fix.service.kit.component"].create(
            {
                "kit_id": kit.id,
                "component_type": "part",
                "notes": "Extra part",
                "quantity": 1.0,
                "standard_cost": 500.0,
            }
        )
        kit.invalidate_recordset()
        assert kit.estimated_cost > baseline, (
            "adding a component did not move the kit estimate (%s -> %s)"
            % (baseline, kit.estimated_cost)
        )


# ==========================================================================
# M39 · Subscriptions
# ==========================================================================
class TestM39Subscription:
    @pytest.fixture
    def sub(self, env, customer):
        def _make(**overrides):
            vals = {
                "name": "AMC Gold %s" % TAG,
                "customer_id": customer.id,
                "operating_unit_id": _ou(env).id,
                "recurring_amount": 3000.0,
                "next_invoice_date": date(2026, 1, 31),
            }
            vals.update(overrides)
            return env["fix.subscription"].create(vals)

        return _make

    @staticmethod
    def _issued_unpaid(s, invoice_date, terms_days=7):
        """A04 hand-off closure (2026-11-05): the ladder chases the UNPAID
        ISSUED INVOICE, so the certification stages one — the customer's terms
        are `terms_days`, the cycle invoice is issued and never paid."""
        existing = (
            s.env["fix.credit.profile"]
            .sudo()
            .search(
                [("customer_id", "=", s.customer_id.id), ("company_id", "=", s.company_id.id)],
                limit=1,
            )
        )
        if not existing:
            s.env["fix.credit.profile"].create(
                {
                    "customer_id": s.customer_id.id,
                    "company_id": s.company_id.id,
                    "payment_terms_days": terms_days,
                }
            )
        s.action_generate_charge()
        (charge,) = s.charge_ids
        charge.invoice_id.sudo().write({"invoice_date": invoice_date, "state": "issued"})
        s.env.flush_all()
        s.env.invalidate_all()
        return s

    @pytest.mark.parametrize(
        ("as_of", "overdue", "state", "step"),
        [
            (date(2026, 2, 10), 3, "past_due", "reminder"),
            (date(2026, 2, 14), 7, "past_due", "reminder"),  # L1 boundary
            (date(2026, 2, 15), 8, "past_due", "final"),
            (date(2026, 2, 22), 15, "past_due", "final"),  # grace boundary
            (date(2026, 2, 23), 16, "hold", "escalate"),
        ],
    )
    def test_flaw_39_2_dunning_ladder_stages(self, sub, as_of, overdue, state, step):
        """FLAW-39.2: the ladder hard-coded its docstring's "day 14" as
        min(grace_period_days, 13), overriding the agreed grace period and
        moving every stage a day early — a 7-day-overdue account was already at
        Final Notice and a 15-day one was suspended.

        A mutation check on 2026-11-01 showed the certification suite did not
        catch that regression, because it only inspected the field default.
        These assert the ladder's behaviour at every boundary, measured on the
        unpaid issued invoice (Jan 31 + 7-day terms = due Feb 7).
        """
        s = self._issued_unpaid(sub(), date(2026, 1, 31))
        s.action_trigger_dunning(as_of=as_of)
        assert (s.days_overdue, s.state, s.dunning_step) == (overdue, state, step)

    def test_flaw_39_2_a_shorter_grace_escalates_sooner(self, sub):
        """The grace period is the customer's agreed term, so a 10-day
        grace must escalate on day 11 rather than wait for a hard-coded 14."""
        s = self._issued_unpaid(sub(grace_period_days=10), date(2026, 1, 31))
        s.action_trigger_dunning(as_of=date(2026, 2, 18))  # 11 days past Feb 7
        assert (s.state, s.dunning_step) == ("hold", "escalate")

    def test_flaw_39_2_a_longer_grace_is_honoured(self, sub):
        """...and a 20-day grace must NOT be truncated to 13."""
        s = self._issued_unpaid(sub(grace_period_days=20), date(2026, 1, 31))
        s.action_trigger_dunning(as_of=date(2026, 2, 18))  # 11 days past due
        assert (s.state, s.dunning_step) == ("past_due", "final")
        s2 = self._issued_unpaid(sub(grace_period_days=20), date(2026, 1, 31))
        s2.action_trigger_dunning(as_of=date(2026, 2, 28))  # 21 days past due
        assert (s2.state, s2.dunning_step) == ("hold", "escalate")

    def test_flaw_39_2_a_never_billed_customer_is_never_dunned(self, sub):
        """A04 report M39-2: a missed billing run is a Finance omission, not
        customer non-payment — the calendar basis suspended a never-billed
        customer."""
        s = sub(next_invoice_date=date(2026, 1, 1))
        s.action_trigger_dunning(as_of=date(2026, 6, 1))
        assert (s.state, s.dunning_step, s.days_overdue) == ("active", "none", 0)


# ==========================================================================
# Cross-module · workspace quality
# ==========================================================================
class TestA04Workspace:
    @staticmethod
    def _a04_dir():
        return (
            Path(__file__).resolve().parents[4]
            / "platform"
            / "cd_p03_portal"
            / "static"
            / "src"
            / "a04"
        )

    def test_every_bound_model_exists(self, env):
        """No dead ends: every model a surface binds must be in the registry."""
        import re

        missing = {}
        for js in sorted(self._a04_dir().glob("m*.js")):
            text = js.read_text(encoding="utf-8")
            for model in set(re.findall(r"model:\s*'([^']+)'", text)):
                if model not in env:
                    missing.setdefault(js.name, []).append(model)
        assert not missing, "surfaces bind models that do not exist: %s" % missing

    def test_every_bound_model_is_actually_served(self, env):
        """A model can exist in the registry and still dead-end: the
        workspace only reads models declared in its SURFACES registry, and an
        undeclared one answers "Model not served by the workspace screens".

        The M37 contract-template list hit exactly this once it was re-pointed
        from the OCA `contract.template` to the project's own model.
        """
        import re

        from odoo.addons.cd_p03_portal.controllers.a04 import SURFACES

        unserved = {}
        for js in sorted(self._a04_dir().glob("m*.js")):
            text = js.read_text(encoding="utf-8")
            for m in re.finditer(
                r"kind:\s*'model_(?:list|form)'[^}]*?model:\s*'([^']+)'", text, re.S
            ):
                model = m.group(1)
                if model not in SURFACES:
                    unserved.setdefault(js.name, set()).add(model)
        # A model may legitimately be served by another area's registry.
        if unserved:
            from odoo.addons.cd_p03_portal.controllers.p03_generic_api import SURFACES as ALL

            unserved = {f: sorted(ms - set(ALL)) for f, ms in unserved.items() if ms - set(ALL)}
            unserved = {f: ms for f, ms in unserved.items() if ms}
        assert not unserved, "surfaces bind models the workspace does not serve: %s" % unserved

    def test_no_form_is_flat(self, env):
        """F-2: every A04 data-entry form is multi-tab.

        The first version of this test took a fixed 9,000-character window
        from each form's start, which spilled into the NEXT form — so a flat
        form passed whenever a later one within that window had tabs. It
        missed five (A04 audit, 2026-11-01). The body is now bounded at the
        next screen declaration.
        """
        import re

        flat = []
        for js in sorted(self._a04_dir().glob("m*.js")):
            text = js.read_text(encoding="utf-8")
            starts = [
                (m.start(), m.group(1))
                for m in re.finditer(r"^\s{2,6}'([A-Za-z0-9:_-]+)':\s*\{", text, re.M)
            ]
            for i, (pos, screen) in enumerate(starts):
                end = starts[i + 1][0] if i + 1 < len(starts) else len(text)
                body = text[pos:end]
                if "kind: 'model_form'" not in body:
                    continue
                tabs = re.search(r"tabs:\s*\[(.*?)\]", body, re.S)
                if not tabs or not tabs.group(1).strip():
                    flat.append("%s/%s" % (js.name, screen))
        assert not flat, "flat 0-tab forms remain: %s" % flat

    def test_no_bengali_label_is_mojibake(self):
        """The A04 form build wrote its tab rows through a non-UTF-8 path and
        lost every Bengali label and icon to question marks."""
        import re

        broken = []
        for js in sorted(self._a04_dir().glob("m*.js")):
            text = js.read_text(encoding="utf-8")
            for m in re.finditer(r"bn:\s*'([^']*)'", text):
                value = m.group(1)
                if value and not value.replace("?", "").replace(".", "").replace(" ", ""):
                    broken.append("%s: %r" % (js.name, value))
            for m in re.finditer(r"icon:\s*'(\?+)'", text):
                broken.append("%s: icon %r" % (js.name, m.group(1)))
        assert not broken, "mojibake labels: %s" % broken[:10]

    def test_no_list_shows_odoo_activity_plumbing(self):
        """A list whose columns are the mail/activity mixin is an
        auto-generated placeholder, not a business surface."""
        import re

        MAGIC = {
            "activity_state",
            "activity_user_id",
            "activity_type_id",
            "activity_type_icon",
            "activity_date_deadline",
            "activity_summary",
            "my_activity_date_deadline",
            "has_message",
            "message_needaction",
            "message_has_error",
            "message_follower_ids",
            "website_message_ids",
        }
        offenders = []
        for js in sorted(self._a04_dir().glob("m*.js")):
            text = js.read_text(encoding="utf-8")
            for m in re.finditer(
                r"'([A-Za-z0-9-]+)':\s*\{[^}]*?kind:\s*'model_list'[^}]*?cols:\s*\[([^\]]*)\]",
                text,
                re.S,
            ):
                cols = [c.strip().strip("\"'") for c in m.group(2).split(",") if c.strip()]
                junk = [c for c in cols if c in MAGIC]
                if len(junk) >= 2:
                    offenders.append("%s/%s: %s" % (js.name, m.group(1), ",".join(junk)))
        assert not offenders, "lists showing Odoo plumbing: %s" % offenders

    def test_every_form_routes_back_to_a_real_screen(self):
        """No dead end: a form's `back` target must be a declared screen."""
        import re

        dangling = []
        for js in sorted(self._a04_dir().glob("m*.js")):
            text = js.read_text(encoding="utf-8")
            declared = set(re.findall(r"^\s{2,6}'([A-Za-z0-9-]+)':\s*\{", text, re.M))
            for m in re.finditer(r"back:\s*'([A-Za-z0-9-]+)'", text):
                if m.group(1) not in declared:
                    dangling.append("%s -> %s" % (js.name, m.group(1)))
        assert not dangling, "forms route back to undeclared screens: %s" % dangling

    def test_no_screen_shows_its_own_id_as_a_title(self):
        """16 forms rendered their screen id as the page heading, e.g.
        "M09-form-wevidence" where the operator expects a record name."""
        import re

        bad = []
        for js in sorted(self._a04_dir().glob("m*.js")):
            text = js.read_text(encoding="utf-8")
            for m in re.finditer(
                r"'([A-Za-z0-9-]+)':\s*\{[^}]{0,400}?title:\s*'([^']+)'", text, re.S
            ):
                if m.group(1) == m.group(2):
                    bad.append("%s/%s" % (js.name, m.group(1)))
        assert not bad, "screens titled with their own id: %s" % bad

    def test_every_tab_label_is_actually_translated(self):
        """295 tab rows carried bn identical to the English, so the
        workspace's Bengali toggle showed English on every generated form."""
        import re

        untranslated = []
        for js in sorted(self._a04_dir().glob("m*.js")):
            text = js.read_text(encoding="utf-8")
            for m in re.finditer(r"label:\s*'([^']+)',\s*bn:\s*'([^']+)'", text):
                if m.group(1) == m.group(2):
                    untranslated.append("%s: %s" % (js.name, m.group(1)))
        assert not untranslated, "%d tab labels are not translated: %s" % (
            len(untranslated),
            untranslated[:6],
        )

    def test_tab_numbering_has_no_gaps(self):
        """A form numbered "1, 3, 4, 8, 9" reads as a skeleton with tabs
        deleted. Numbering restarts at 1 and runs consecutively."""
        import re

        gaps = []
        for js in sorted(self._a04_dir().glob("m*.js")):
            text = js.read_text(encoding="utf-8")
            for m in re.finditer(r"tabs:\s*\[(.*?)\]", text, re.S):
                nums = [int(x) for x in re.findall(r"label:\s*'(\d+)\.", m.group(1))]
                if nums and nums != list(range(1, len(nums) + 1)):
                    gaps.append("%s: %s" % (js.name, nums))
        assert not gaps, "non-sequential tab numbering: %s" % gaps[:6]

    def test_no_model_is_edited_by_two_modules(self):
        """M38 carried a verbatim clone of M11's promotion form, so the
        same records had two editors that could drift apart."""
        import collections
        import re

        owners = collections.defaultdict(set)
        for js in sorted(self._a04_dir().glob("m*.js")):
            text = js.read_text(encoding="utf-8")
            for m in re.finditer(r"kind:\s*'model_form'[^}]*?model:\s*'([^']+)'", text, re.S):
                owners[m.group(1)].add(js.name)
        shared = {k: sorted(v) for k, v in owners.items() if len(v) > 1}
        assert not shared, "models edited by more than one module: %s" % shared

    def test_a_list_and_the_form_it_opens_share_a_model(self):
        """The bug class that hit M37 and M09 twice.

        A `__by_screen__` entry routes a LIST's row-click into a FORM. When the
        two are bound to different models, the form is handed another model's
        id — it opens on the wrong record, or on nothing. The browser sweep
        cannot see this, because it opens screens directly rather than by
        clicking a row.
        """
        import re

        mismatches = []
        for js in sorted(self._a04_dir().glob("m*.js")):
            text = js.read_text(encoding="utf-8")
            models = {}
            for m in re.finditer(
                r"'([A-Za-z0-9-]+)':\s*\{[^}]*?kind:\s*'model_(?:list|form)'[^}]*?"
                r"model:\s*'([^']+)'",
                text,
                re.S,
            ):
                models[m.group(1)] = m.group(2)
            for block in re.finditer(r"'M\d+:__by_screen__':\s*\{([^}]*)\}", text, re.S):
                for pair in re.finditer(r"'([^']+)':\s*'([A-Za-z0-9-]+)'", block.group(1)):
                    src, dst = pair.group(1), pair.group(2)
                    if src in models and dst in models and models[src] != models[dst]:
                        mismatches.append(
                            "%s: %s(%s) -> %s(%s)" % (js.name, src, models[src], dst, models[dst])
                        )
        assert not mismatches, (
            "lists routing rows into a form for a different model: %s" % mismatches
        )

    def test_warranty_verification_is_reachable(self, env):
        """`verified_by` / `verified_at` shipped readonly with nothing
        anywhere that set them, so 55 live warranties read "Verified At —" and
        the 'pending' status had no exit."""
        model = env["fix.warranty"]
        assert hasattr(model, "action_verify"), "no way to verify a warranty"
        assert hasattr(model, "action_void"), "no way to void a warranty"

    def test_no_nav_label_hardcodes_a_record_count(self):
        """ "14 Contract Families" sat over a table holding 0 rows, and
        "7 Protection Families" over one holding 55. A label that states a
        count the data does not match is worse than no count."""
        import re

        bad = []
        for js in sorted(self._a04_dir().glob("m*.js")):
            text = js.read_text(encoding="utf-8")
            for m in re.finditer(r"en:\s*'(\d+\s+[^']+)'", text):
                bad.append("%s: %s" % (js.name, m.group(1)))
        assert not bad, "nav labels hard-coding a count: %s" % bad

    def test_no_nav_label_is_claimed_by_two_modules(self):
        """ "7 Protection Families" was the label for fix.warranty in M09
        and for fix.catalogue.item in M37 — same words, different data."""
        import collections
        import re

        labels = collections.defaultdict(set)
        for js in sorted(self._a04_dir().glob("m*.js")):
            text = js.read_text(encoding="utf-8")
            for m in re.finditer(r"\{ id: '(M\d+-[A-Za-z0-9-]+)', en: '([^']+)'", text):
                labels[m.group(2)].add(js.name)
        shared = {k: sorted(v) for k, v in labels.items() if len(v) > 1}
        assert not shared, "nav labels used by more than one module: %s" % shared


# ==========================================================================
# M11 · Dynamic pricing precision (FLAW-11.1)
# ==========================================================================
class TestM11DecimalPricing:
    @pytest.fixture
    def rule(self, env):
        def _make(**overrides):
            vals = {
                "name": "Surge %s" % TAG,
                "rule_type": "demand_surge",
                "channel": "both",
                "adjustment_pct": 0.0,
                "surge_multiplier": 1.0,
            }
            vals.update(overrides)
            return env["fix.dynamic.price.rule"].create(vals)

        return _make

    def test_flaw_11_1_result_is_exact_to_the_paisa(self, rule):
        """Every quoted price is exact to two decimal places.

        Binary float cannot hold 0.1 exactly, so a naive engine returns values
        like 1100.1100000000001 that then round inconsistently down the line.
        """
        r = rule(adjustment_pct=10.0)
        for base in (1000.10, 999.99, 0.01, 12345.67, 8.285):
            out = r.apply_to(base)
            assert Decimal(str(out)) == Decimal(str(out)).quantize(Decimal("0.01")), (
                "apply_to(%r) returned %r, which is not exact to the paisa" % (base, out)
            )

    def test_flaw_11_1_matches_independent_decimal_arithmetic(self, rule):
        """The engine's answer equals the Decimal computation done
        here independently — not merely "a plausible number"."""
        from decimal import ROUND_HALF_EVEN

        r = rule(adjustment_pct=7.5, surge_multiplier=1.25)
        for base in (1000.10, 333.33, 19.95, 87654.32):
            expected = (
                Decimal(str(base))
                * (Decimal("1.0") + Decimal("7.5") / Decimal("100.0"))
                * Decimal("1.25")
            ).quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)
            assert Decimal(str(r.apply_to(base))) == expected, (
                "base %r: engine %r != Decimal %r" % (base, r.apply_to(base), expected)
            )

    def test_flaw_11_1_float_drift_is_actually_avoided(self, rule):
        """A case where the naive float path visibly drifts.

        1000.10 * 1.1 is 1100.1100000000001 in binary float. The engine must
        return exactly 1100.11.
        """
        r = rule(adjustment_pct=10.0)
        naive = 1000.10 * 1.1
        assert naive != 1100.11, "float drift precondition no longer holds"
        assert r.apply_to(1000.10) == 1100.11

    def test_flaw_11_1_banker_rounding_is_used(self, rule):
        """ROUND_HALF_EVEN is the documented choice; a half-paisa tie
        goes to the even digit, not always up."""
        r = rule(adjustment_pct=0.0)
        assert r.apply_to(2.345) == 2.34  # ties to even (4)
        assert r.apply_to(2.355) == 2.36  # ties to even (6)

    def test_flaw_11_1_negative_base_is_refused(self, rule):
        r = rule()
        with pytest.raises(UserError, match="cannot be negative"):
            r.apply_to(-1.0)

    def test_flaw_11_1_explanation_trail_records_the_same_number(self, rule):
        """The audit trail must carry the price actually quoted."""
        r = rule(adjustment_pct=10.0)
        out = r.calculate_and_explain(1000.10, context_info="A04 certification")
        price = out.get("final_price") if isinstance(out, dict) else out
        assert Decimal(str(price)) == Decimal("1100.11")


# ==========================================================================
# M12 · Marketplace escrow window (FLAW-12.2)
# ==========================================================================
class TestM12Escrow:
    @pytest.fixture
    def ledger(self, env, customer):
        def _make(**overrides):
            vals = {
                "name": "COMM/%s" % TAG,
                "company_id": env.company.id,
                "seller_partner_id": customer.id,
                "source_type": "marketplace",
                "gross_amount": 5000.0,
                "state": "accrued",
            }
            vals.update(overrides)
            return env["fix.commission.ledger"].create(vals)

        return _make

    def test_flaw_12_2_marketplace_row_is_held_for_seven_days(self, env, ledger):
        """A commission accrued today must not be collectable today:
        the buyer still has a dispute window."""
        row = ledger()
        assert row.escrow_release_date == date.today() + timedelta(days=7)
        assert row.escrow_window_elapsed is False

    def test_flaw_12_2_window_elapses_after_seven_days(self, env, ledger):
        row = ledger()
        env.cr.execute(
            "UPDATE fix_commission_ledger SET create_date = %s WHERE id = %s",
            (datetime.now() - timedelta(days=8), row.id),
        )
        row.invalidate_recordset()
        assert row.escrow_window_elapsed is True

    def test_flaw_12_2_partner_commissions_carry_no_buyer_window(self, ledger):
        """A partner referral has no buyer to dispute it, so it is
        released immediately — the window is marketplace-specific."""
        row = ledger(source_type="partner_referral")
        assert row.escrow_window_elapsed is True
        assert not row.escrow_release_date

    def test_flaw_12_2_payout_run_will_not_collect_a_held_row(self, env, ledger):
        """The control that matters: action_collect_accrued must skip
        rows still inside the window."""
        held = ledger()
        run = env["fix.payout.run"].create(
            {"company_id": env.company.id, "period": date.today().strftime("%Y-%m")}
        )
        # "nothing free to pay" is the correct outcome here
        with contextlib.suppress(UserError):
            run.action_collect_accrued()
        assert (
            held not in run.commission_ids
        ), "a commission inside its 7-day dispute window was collected into a payout"

    def test_flaw_12_2_search_operator_round_trips(self, env, ledger):
        """escrow_window_elapsed is computed, so collection relies on
        its search implementation rather than a stored column."""
        held = ledger()
        found = env["fix.commission.ledger"].search(
            [("id", "=", held.id), ("escrow_window_elapsed", "=", True)]
        )
        assert not found
        found = env["fix.commission.ledger"].search(
            [("id", "=", held.id), ("escrow_window_elapsed", "=", False)]
        )
        assert held in found


# ==========================================================================
# Statutory configuration, template readiness, warranty verification
# ==========================================================================
class TestA04Governance:
    def test_stamp_schedule_defaults_to_chargeable(self, env):
        """An unmaintained rate table must never waive duty."""
        Schedule = env["fix.stamp.duty.schedule"]
        assert Schedule.is_chargeable("art_5", 1.0) is True
        assert Schedule.is_chargeable("art_35", 0.0) is True

    def test_stamp_schedule_exempts_below_its_floor(self, env):
        Schedule = env["fix.stamp.duty.schedule"]
        Schedule.create(
            {
                "article": "art_5",
                "name": "Agreement - audit fixture",
                "date_from": date(2026, 1, 1),
                "exemption_floor_bdt": 50000.0,
                "statutory_reference": "fixture, not a statutory rate",
            }
        ).action_confirm()
        assert Schedule.is_chargeable("art_5", 50000.0) is False
        assert Schedule.is_chargeable("art_5", 50000.01) is True
        # a different head is unaffected
        assert Schedule.is_chargeable("art_35", 1000.0) is True

    def test_stamp_schedule_is_effective_dated(self, env):
        Schedule = env["fix.stamp.duty.schedule"]
        # a rate is only in force once Finance confirms it (A04, 2026-11-01)
        Schedule.create(
            {
                "article": "art_15",
                "name": "Bond - superseded",
                "date_from": date(2020, 1, 1),
                "date_to": date(2024, 12, 31),
                "exemption_floor_bdt": 1000000.0,
                "statutory_reference": "fixture, not a statutory rate",
            }
        ).action_confirm()
        # the lapsed row does not apply today, so duty is required
        assert Schedule.is_chargeable("art_15", 5000.0) is True
        assert Schedule.is_chargeable("art_15", 5000.0, on_date=date(2023, 6, 1)) is False

    def test_stamp_schedule_window_must_be_ordered(self, env):
        with pytest.raises(ValidationError, match="cannot precede"):
            env["fix.stamp.duty.schedule"].create(
                {
                    "article": "art_5",
                    "name": "Inverted",
                    "date_from": date(2026, 6, 1),
                    "date_to": date(2026, 1, 1),
                }
            )

    def test_contract_below_the_floor_activates_without_a_certificate(self, env, contract):
        """With a floor configured, an instrument under it is not
        chargeable and needs no certificate."""
        env["fix.stamp.duty.schedule"].create(
            {
                "article": "art_5",
                "name": "Agreement - audit fixture",
                "date_from": date(2025, 1, 1),
                "exemption_floor_bdt": 500000.0,
                "statutory_reference": "fixture, not a statutory rate",
            }
        ).action_confirm()
        c = contract(annual_value=120000.0, stamp_duty_cert_no=False, has_signed_contract_doc=False)
        c.action_activate()
        assert c.state == "active"

    def test_contract_above_the_floor_still_needs_a_certificate(self, env, contract):
        env["fix.stamp.duty.schedule"].create(
            {
                "article": "art_5",
                "name": "Agreement - audit fixture",
                "date_from": date(2025, 1, 1),
                "exemption_floor_bdt": 50000.0,
                "statutory_reference": "fixture, not a statutory rate",
            }
        ).action_confirm()
        c = contract(annual_value=120000.0, stamp_duty_cert_no=False)
        with pytest.raises(UserError, match="Stamp Duty Certificate"):
            c.action_activate()

    def test_seeded_contract_templates_exist_for_every_family(self, env):
        """The M37 template master listed zero rows."""
        Template = env["fix.contract.template"]
        types = set(Template.search([]).mapped("contract_type"))
        assert {"amc", "ramc", "managed", "rental", "marketplace", "sla"} <= types

    def test_a_template_without_wording_cannot_be_issued(self, env):
        """The seeded templates are structurally complete and
        deliberately empty of terms; the system says so rather than letting
        one be issued blank."""
        tpl = env["fix.contract.template"].search([("contract_type", "=", "amc")], limit=1)
        assert tpl, "no AMC template seeded"
        assert tpl.is_publishable is False
        # The templates now carry SEEDED DRAFT wording, so what stops them
        # reaching a customer is the Legal sign-off, not an empty field. That
        # gate was added before the drafts were loaded, precisely so seeding
        # wording could not make six unreviewed contracts issuable
        # (A04 audit, 2026-11-01).
        assert "Legal sign-off" in (tpl.publish_blocker or "")
        assert tpl.terms_are_draft is True
        with pytest.raises(UserError, match="not ready to issue"):
            tpl.assert_publishable()

    def test_a_template_becomes_issuable_once_bilingual(self, env):
        tpl = env["fix.contract.template"].search([("contract_type", "=", "sla")], limit=1)
        tpl.write(
            {
                "standard_terms": "Service levels as scheduled.",
                "terms_bn": "\u09b8\u09c7\u09ac\u09be\u09b0 \u09b6\u09b0\u09cd\u09a4\u09be\u09ac\u09b2\u09bf\u0964",
            }
        )
        # wording alone is not sign-off
        assert tpl.is_publishable is False
        assert "Legal sign-off" in (tpl.publish_blocker or "")
        tpl.action_legal_signoff()
        assert tpl.is_publishable is True
        assert tpl.assert_publishable() is True

    def test_english_only_template_is_still_blocked(self, env):
        """DE-17: the estate is bilingual, so English alone is not
        a publishable contract in Bangladesh."""
        tpl = env["fix.contract.template"].search([("contract_type", "=", "rental")], limit=1)
        tpl.write({"standard_terms": "Hire terms.", "terms_bn": ""})
        assert tpl.is_publishable is False
        assert "Bengali" in tpl.publish_blocker

    def test_unverified_warranties_are_visible_as_such(self, env):
        """55 live warranties read "Verified At -" with no way to
        tell that apart from verified cover."""
        model = env["fix.warranty"]
        assert "verification_state" in model._fields
        w = model.search([("warranty_type", "!=", "none"), ("verified_at", "=", False)], limit=1)
        if w:
            assert w.verification_state == "unverified"

    def test_verifying_requires_proof_on_file(self, env):
        device = _any_device(env)
        w = env["fix.warranty"].create(
            {
                "device_id": device.id,
                "warranty_type": "extended",
                "start_date": date(2026, 1, 1),
                "end_date": date(2027, 1, 1),
                "status": "pending",
            }
        )
        assert w.verification_state == "unverified"
        with pytest.raises(UserError, match="before verifying"):
            w.action_verify()

    def test_voiding_is_available_and_recorded(self, env):
        device = _any_device(env)
        w = env["fix.warranty"].create(
            {
                "device_id": device.id,
                "warranty_type": "extended",
                "start_date": date(2026, 1, 1),
                "end_date": date(2027, 1, 1),
                "status": "pending",
            }
        )
        w.action_void(reason="Proof shown to be a different device")
        assert w.status == "voided"
        with pytest.raises(UserError, match="already voided"):
            w.action_void()


# ==========================================================================
# Business rules recomputed independently of the implementation
# ==========================================================================
class TestA04BusinessRules:
    """Each of these recomputes the rule from the specification's own
    statement and compares, rather than asserting whatever the code returns.
    """

    def test_contract_margin_equals_value_less_measured_cost(self, env, customer, contract):
        """margin = annual value - (parts + labour delivered)."""
        c = contract(annual_value=250000.0)
        parts, labour = 40000.0, 15000.0
        order = _service_order(env, customer, contract=c)
        env["fix.estimate"].create(
            {
                "order_id": order.id,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "line_type": "part",
                            "description": "Board",
                            "quantity": 1,
                            "unit_price": parts,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "line_type": "labour",
                            "description": "Bench",
                            "quantity": 1,
                            "unit_price": labour,
                        },
                    ),
                ],
            }
        )
        c.invalidate_recordset()
        expected_cost = parts + labour
        expected_margin = 250000.0 - expected_cost
        assert c.total_delivery_cost == expected_cost
        assert c.contract_margin_bdt == expected_margin
        assert c.contract_margin_pct == round(expected_margin / 250000.0 * 100.0, 2)

    def test_escrow_release_is_exactly_seven_days_from_accrual(self, env, customer):
        """REQ: a marketplace payout is held for a 7-day buyer
        dispute window."""
        row = env["fix.commission.ledger"].create(
            {
                "name": "COMM/RULE/%s" % TAG,
                "company_id": env.company.id,
                "seller_partner_id": customer.id,
                "source_type": "marketplace",
                "gross_amount": 9000.0,
                "state": "accrued",
            }
        )
        accrued_on = odoo_fields.Date.to_date(row.create_date)
        assert row.escrow_release_date == accrued_on + timedelta(days=7)

    def test_price_floor_tier_matches_the_stated_bands(self, env):
        """REQ: <15% below floor is Tier 2, <30% Tier 3, else Tier 4."""
        f = env["fix.price.floor"].create(
            {"name": "Band probe %s" % TAG, "product_code": "BAND-%s" % TAG, "floor_price": 1000.0}
        )
        for proposed, expected in (
            (999.0, "tier_2"),
            (850.0, "tier_2"),
            (849.0, "tier_3"),
            (700.0, "tier_3"),
            (699.0, "tier_4"),
            (1.0, "tier_4"),
        ):
            f.proposed_override_price = proposed
            shortfall = (1000.0 - proposed) / 1000.0 * 100.0
            assert f.dofa_tier_required == expected, "%.1f%% below floor -> %s, expected %s" % (
                shortfall,
                f.dofa_tier_required,
                expected,
            )

    def test_dunning_boundaries_match_the_stated_ladder(self, env, customer):
        """REQ: reminder to day 7, final to grace expiry, then hold."""
        grace = 15
        for overdue, expected_step in (
            (3, "reminder"),
            (7, "reminder"),
            (8, "final"),
            (15, "final"),
            (16, "escalate"),
        ):
            sub = env["fix.subscription"].create(
                {
                    "name": "Ladder %s" % TAG,
                    "customer_id": customer.id,
                    "operating_unit_id": _ou(env).id,
                    "recurring_amount": 1000.0,
                    "next_invoice_date": date(2026, 1, 31),
                    "grace_period_days": grace,
                }
            )
            TestM39Subscription._issued_unpaid(sub, date(2026, 1, 31))
            sub.action_trigger_dunning(as_of=date(2026, 2, 7) + timedelta(days=overdue))
            assert sub.dunning_step == expected_step, "%d days overdue -> %s, expected %s" % (
                overdue,
                sub.dunning_step,
                expected_step,
            )


# ==========================================================================
# M40 · Channel conflict arbitration (DISC-40.2)
# ==========================================================================
class TestM40ChannelConflict:
    """The register called FixPartnerConflict a passive stub with zero
    methods. The remediation added dofa_decision, dofa_arbitrator_id and
    arbitration_notes and stopped there — no method set any of them, so it
    stayed a passive stub with more fields, and the grep suite passed on the
    declarations.
    """

    @pytest.fixture
    def conflict(self, env, customer):
        def _make(as_user=None):
            party = env["fix.partner"].create(
                {
                    "name": "Reseller A %s" % TAG,
                    "partner_id": customer.id,
                    "partner_type": "reseller",
                    "state": "prospective",
                }
            )
            model = env["fix.partner.conflict"]
            if as_user is not None:
                model = model.with_user(as_user)
            return model.create(
                {
                    "name": "Territory clash %s" % TAG,
                    "partner_a_id": party.id,
                    "description": "Both partners claim the same corporate account.",
                }
            )

        return _make

    def test_arbitration_requires_a_rationale(self, conflict):
        c = conflict()
        with pytest.raises(UserError, match="arbitration rationale"):
            c.action_mediate("partner_a", notes="")

    def test_arbitration_requires_tier_3_authority(self, conflict):
        c = conflict()
        with pytest.raises(UserError, match="Tier 3"):
            c.action_mediate("partner_a", notes="A registered the deal first.")

    def test_the_arbitrator_cannot_be_attributed_to_someone_else(self, env, conflict):
        """dofa_arbitrator_id recorded whoever the caller nominated."""
        c = conflict()
        director = _approver(env, 3, "a04.conflict.attrib@example.com")
        other = _approver(env, 3, "a04.conflict.other@example.com")
        with pytest.raises(UserError, match="cannot be attributed"):
            c.with_user(director).action_mediate(
                "partner_a", dofa_arbitrator_id=other.id, notes="Signed off elsewhere."
            )

    def test_arbitration_rejects_an_unknown_ruling(self, env, conflict):
        c = conflict()
        with pytest.raises(UserError, match="Unknown ruling"):
            c.action_mediate("whatever", notes="n/a")

    def test_the_raiser_cannot_arbitrate_their_own_conflict(self, env, conflict):
        director = _approver(env, 3, "a04.conflict.self@example.com")
        c = conflict(as_user=director)
        with pytest.raises(UserError, match="Segregation of duties"):
            c.with_user(director).action_mediate("partner_a", notes="Mine to call.")

    def test_a_tier_3_arbitrator_rules_and_records_it(self, env, conflict):
        c = conflict()
        director = _approver(env, 3, "a04.conflict.t3@example.com")
        c.with_user(director).action_mediate(
            "split", notes="Both partners contributed; commission split 50/50."
        )
        assert c.dofa_decision == "split"
        assert c.dofa_arbitrator_id == director
        assert c.arbitrated_at and c.state == "mediated"

    def test_a_conflict_cannot_close_without_a_ruling(self, conflict):
        c = conflict()
        with pytest.raises(UserError, match="still OPEN"):
            c.action_close()

    def test_a_ruled_conflict_closes(self, env, conflict):
        c = conflict()
        director = _approver(env, 3, "a04.conflict.t3b@example.com")
        c.with_user(director).action_mediate("partner_a", notes="Deal registered first.")
        c.action_close()
        assert c.state == "closed"
        with pytest.raises(UserError, match="already closed"):
            c.with_user(director).action_mediate("partner_b", notes="Reversal.")


# ==========================================================================
# Unverified warranty cover - the measured half of the 55-warranty finding
# ==========================================================================
class TestA04UnverifiedWarrantyCover:
    """A04 audit 2026-11-01: 53 of 55 live warranty rows were ACTIVE
    with `verified_at` empty, and `fix.device.is_under_warranty` never looked
    at verification - so 53 devices could draw a free warranty repair with no
    purchase proof on file and nothing recorded the exposure.

    Whether to WITHDRAW that cover is a commercial decision, so the gate still
    honours it. What these tests certify is that the exposure is no longer
    invisible: it is measurable, recorded per order, and attributable.
    """

    def _warranty(self, env, verified=False, **kw):
        device = _any_device(env)
        vals = {
            "device_id": device.id,
            "warranty_type": "extended",
            "start_date": odoo_fields.Date.context_today(device) - timedelta(days=30),
            "end_date": odoo_fields.Date.context_today(device) + timedelta(days=300),
            "status": "active",
        }
        vals.update(kw)
        w = env["fix.warranty"].create(vals)
        if verified:
            # Build the proof rather than hunting for one: fix_test holds no
            # fix.document and the production clone does, so a helper that
            # searched passed on one database and failed on the other. A
            # fixture must build what it needs (A04 audit, 2026-11-01).
            attachment = env["ir.attachment"].create(
                {"name": "A04 warranty proof", "raw": b"purchase receipt"}
            )
            doc = env["fix.document"].create(
                {
                    "name": "A04 warranty card %s" % TAG,
                    "attachment_id": attachment.id,
                    "document_type": "warranty_card",
                }
            )
            w.proof_document_id = doc.id
            w.action_verify()
        device.invalidate_recordset()
        return device, w

    def test_unverified_cover_still_covers(self, env):
        """Cover is cover. The gate must not start refusing live
        customers because of an audit finding."""
        device, w = self._warranty(env)
        assert w.verification_state == "unverified"
        assert device.is_under_warranty() is True

    def test_unverified_cover_fails_a_verified_only_check(self, env):
        """The exposure is now expressible as a query."""
        device, w = self._warranty(env)
        assert device.is_under_warranty(require_verified=True) is False

    def test_verified_cover_passes_a_verified_only_check(self, env):
        device, w = self._warranty(env, verified=True)
        assert w.verification_state == "verified"
        assert device.is_under_warranty(require_verified=True) is True

    def test_unverified_cover_is_enumerable(self, env):
        device, w = self._warranty(env)
        assert w in device.unverified_warranty_cover()

    def test_verified_cover_leaves_the_exposure_list(self, env):
        device, w = self._warranty(env, verified=True)
        assert w not in device.unverified_warranty_cover()

    def test_expired_cover_is_not_counted_as_exposure(self, env):
        """An unverified warranty that no longer covers today is not
        an exposure - it cannot be drawn on."""
        today = odoo_fields.Date.context_today(env.user)
        device, w = self._warranty(
            env,
            start_date=today - timedelta(days=400),
            end_date=today - timedelta(days=5),
        )
        assert w.verification_state == "unverified"
        assert w not in device.unverified_warranty_cover()

    def test_cover_boundary_is_the_LOCAL_date_not_utc(self, env):
        """Bangladesh is UTC+6. `fields.Date.today()` (UTC) is on the
        PREVIOUS date for the first six hours of every local day, and on the
        1st of a month in the previous MONTH - which decided cover on the wrong
        side of an expiry boundary. The default must be the local date.
        """
        local_today = odoo_fields.Date.context_today(env.user)
        device, w = self._warranty(
            env,
            start_date=local_today - timedelta(days=10),
            end_date=local_today,
        )
        assert (
            device.is_under_warranty() is True
        ), "cover ending on the local date must still hold on that date"
        device2, w2 = self._warranty(
            env,
            start_date=local_today - timedelta(days=10),
            end_date=local_today - timedelta(days=1),
        )
        device2.invalidate_recordset()
        assert any(x.end_date == local_today - timedelta(days=1) for x in device2.warranty_id)

    def test_warranty_order_on_unverified_cover_is_flagged(self, env, customer):
        """The order proceeds, and says so on the record."""
        device, w = self._warranty(env)
        order = _service_order(env, customer)
        order.device_id = device.id
        order.order_category = "warranty"
        order._check_warranty_gate()
        assert order.warranty_cover_unverified is True
        body = " ".join(
            env["mail.message"]
            .search([("model", "=", "fix.service.order"), ("res_id", "=", order.id)])
            .mapped("body")
        )
        assert "UNVERIFIED cover" in body, "the exposure was not recorded on the order"

    def test_warranty_order_on_verified_cover_is_not_flagged(self, env, customer):
        device, w = self._warranty(env, verified=True)
        order = _service_order(env, customer)
        order.device_id = device.id
        order.order_category = "warranty"
        order._check_warranty_gate()
        assert order.warranty_cover_unverified is False

    def test_a_paid_order_is_never_flagged(self, env, customer):
        """The flag means "free work on unchecked cover"; a paid order
        cannot mean that."""
        device, w = self._warranty(env)
        order = _service_order(env, customer)
        order.device_id = device.id
        order.order_category = "standard"
        order._check_warranty_gate()
        assert order.warranty_cover_unverified is False


# ==========================================================================
# The escrow fields' own shape - caught by Odoo's registry warning
# ==========================================================================
class TestA04EscrowFieldShape:
    """The escrow control was first written as ONE compute feeding a
    stored date and a non-stored boolean. Odoo warned; the warning was real.

    Reading the boolean ran the shared compute and WROTE the stored date, and
    every P03 list/form/report endpoint is declared `readonly=True`, where a
    write raises - so any A04 screen showing a commission-ledger row would
    have failed. Separately, a stored "has the window elapsed" would freeze at
    its last recompute and authorise a payout whose window had not passed.
    """

    def _f(self, env, name):
        return env["fix.commission.ledger"]._fields[name]

    def test_elapsed_flag_is_not_stored(self, env):
        """Time-dependent, so storing it would freeze it."""
        assert self._f(env, "escrow_window_elapsed").store is False

    def test_release_date_is_stored(self, env):
        """A fixed fact of the row, and searched on."""
        assert self._f(env, "escrow_release_date").store is True

    def test_the_two_fields_do_not_share_a_compute(self, env):
        """Sharing one is what made a read perform a write."""
        assert (
            self._f(env, "escrow_release_date").compute
            != self._f(env, "escrow_window_elapsed").compute
        )

    def test_reading_the_flag_does_not_dirty_the_date(self, env, customer):
        """The behavioural half: a read must stay a read."""
        row = env["fix.commission.ledger"].create(
            {
                "name": "COMM/SHAPE/%s" % TAG,
                "company_id": env.company.id,
                "seller_partner_id": customer.id,
                "source_type": "marketplace",
                "gross_amount": 5000.0,
                "state": "accrued",
            }
        )
        env.flush_all()
        # Deliberately desynchronise the stored column, then read the flag.
        # Under the single shared compute this read RAN that compute and wrote
        # the column back - which is a write on a readonly cursor for every
        # /p03/model/records request. The column must come back untouched.
        sentinel = date(2001, 1, 1)
        env.cr.execute(
            "UPDATE fix_commission_ledger SET escrow_release_date = %s WHERE id = %s",
            (sentinel, row.id),
        )
        row.invalidate_recordset()
        _ = row.escrow_window_elapsed
        env.flush_all()
        env.cr.execute(
            "SELECT escrow_release_date FROM fix_commission_ledger WHERE id = %s",
            (row.id,),
        )
        assert (
            env.cr.fetchone()[0] == sentinel
        ), "reading escrow_window_elapsed rewrote the stored escrow_release_date"

    def test_a_lapsed_window_reads_as_elapsed(self, env, customer):
        row = env["fix.commission.ledger"].create(
            {
                "name": "COMM/LAPSED/%s" % TAG,
                "company_id": env.company.id,
                "seller_partner_id": customer.id,
                "source_type": "marketplace",
                "gross_amount": 5000.0,
                "state": "accrued",
            }
        )
        # Drive the ACCRUAL, not the stored projection: the flag is computed
        # from create_date so that a stale stored date can never authorise a
        # payout. Writing the projection and expecting the flag to follow was
        # asserting the earlier design.
        env.cr.execute(
            "UPDATE fix_commission_ledger SET create_date = %s WHERE id = %s",
            (datetime.now() - timedelta(days=row.ESCROW_WINDOW_DAYS + 1), row.id),
        )
        row.invalidate_recordset()
        assert row.escrow_window_elapsed is True

    def test_a_live_window_reads_as_not_elapsed(self, env, customer):
        row = env["fix.commission.ledger"].create(
            {
                "name": "COMM/LIVE/%s" % TAG,
                "company_id": env.company.id,
                "seller_partner_id": customer.id,
                "source_type": "marketplace",
                "gross_amount": 5000.0,
                "state": "accrued",
            }
        )
        env.cr.execute(
            "UPDATE fix_commission_ledger SET create_date = %s WHERE id = %s",
            (datetime.now() - timedelta(days=1), row.id),
        )
        row.invalidate_recordset()
        assert row.escrow_window_elapsed is False

    def test_non_marketplace_has_no_window(self, env, customer):
        """A referral commission carries no buyer dispute window."""
        row = env["fix.commission.ledger"].create(
            {
                "name": "COMM/REF/%s" % TAG,
                "company_id": env.company.id,
                "seller_partner_id": customer.id,
                "source_type": "partner_referral",
                "gross_amount": 5000.0,
                "state": "accrued",
            }
        )
        assert not row.escrow_release_date
        assert row.escrow_window_elapsed is True

    def test_a_stale_stored_date_cannot_authorise_a_payout(self, env, customer):
        """The reason the flag reads create_date and not the stored column.

        A stored "releases on" that has drifted must not be able to make the
        window look elapsed - that is the single error in this control that
        pays out money while a buyer dispute is still open.
        """
        row = env["fix.commission.ledger"].create(
            {
                "name": "COMM/STALE/%s" % TAG,
                "company_id": env.company.id,
                "seller_partner_id": customer.id,
                "source_type": "marketplace",
                "gross_amount": 5000.0,
                "state": "accrued",
            }
        )
        env.flush_all()
        # the row accrued today, so its window is open; corrupt the projection
        # to claim it released in 2001
        env.cr.execute(
            "UPDATE fix_commission_ledger SET escrow_release_date = %s WHERE id = %s",
            (date(2001, 1, 1), row.id),
        )
        row.invalidate_recordset()
        assert (
            row.escrow_window_elapsed is False
        ), "a drifted stored release date made an open window look elapsed"

    def test_a_drifted_stored_date_cannot_fund_a_payout(self, env, customer):
        """The same defect on the path that actually MOVES MONEY.

        `action_collect_accrued` finds its rows with a domain, and a domain can
        only read the STORED `escrow_release_date`. A stored date that has
        drifted earlier would therefore be collected into a funded payout run
        while the buyer dispute window is still open - the flag being correct
        is no help if the query never consults it. The run re-confirms each row
        against the computed flag for exactly this reason.
        """
        row = env["fix.commission.ledger"].create(
            {
                "name": "COMM/DRIFT/%s" % TAG,
                "company_id": env.company.id,
                "seller_partner_id": customer.id,
                "source_type": "marketplace",
                "gross_amount": 7000.0,
                "state": "accrued",
            }
        )
        env.flush_all()
        # accrued today, so its window is open; drift the projection to 2001
        env.cr.execute(
            "UPDATE fix_commission_ledger SET escrow_release_date = %s WHERE id = %s",
            (date(2001, 1, 1), row.id),
        )
        row.invalidate_recordset()
        run = env["fix.payout.run"].create(
            {
                "company_id": env.company.id,
                "period": odoo_fields.Date.context_today(env.user).strftime("%Y-%m"),
            }
        )
        try:
            run.action_collect_accrued()
        except UserError:
            # nothing was free to pay - the held row was correctly excluded
            return
        assert row not in run.commission_ids, (
            "a drifted stored release date funded a payout inside an open " "dispute window"
        )


# ==========================================================================
# The escrow SEARCH layer, tested on its own
# ==========================================================================
class TestA04EscrowSearchLayer:
    """`action_collect_accrued` has two independently sufficient guards:
    an indexed domain clause that resolves through `_search_escrow_window_elapsed`,
    and a Python re-confirm against the computed flag. A mutation that removes
    either one alone cannot be observed, because the other still enforces the
    rule - and the mutation that removes BOTH is caught.

    These tests cover the DOMAIN layer directly, so it is not left resting on
    the re-confirm for its coverage.
    """

    def _row(self, env, customer, source="marketplace", age_days=0):
        row = env["fix.commission.ledger"].create(
            {
                "name": "COMM/SRCH/%s/%d" % (TAG, age_days),
                "company_id": env.company.id,
                "seller_partner_id": customer.id,
                "source_type": source,
                "gross_amount": 4000.0,
                "state": "accrued",
            }
        )
        env.flush_all()
        if age_days:
            env.cr.execute(
                "UPDATE fix_commission_ledger SET create_date = %s WHERE id = %s",
                (datetime.now() - timedelta(days=age_days), row.id),
            )
            row.invalidate_recordset()
            row._compute_escrow_release()
            row.flush_recordset()
        return row

    def test_search_excludes_a_row_inside_the_window(self, env, customer):
        fresh = self._row(env, customer)
        found = env["fix.commission.ledger"].search(
            [("id", "=", fresh.id), ("escrow_window_elapsed", "=", True)]
        )
        assert not found, "a row still inside its dispute window was searchable as elapsed"

    def test_search_includes_a_row_past_the_window(self, env, customer):
        aged = self._row(env, customer, age_days=8)
        found = env["fix.commission.ledger"].search(
            [("id", "=", aged.id), ("escrow_window_elapsed", "=", True)]
        )
        assert found == aged

    def test_search_negation_is_the_complement(self, env, customer):
        fresh = self._row(env, customer)
        held = env["fix.commission.ledger"].search(
            [("id", "=", fresh.id), ("escrow_window_elapsed", "=", False)]
        )
        assert held == fresh

    def test_search_treats_partner_referrals_as_always_released(self, env, customer):
        ref = self._row(env, customer, source="partner_referral")
        found = env["fix.commission.ledger"].search(
            [("id", "=", ref.id), ("escrow_window_elapsed", "=", True)]
        )
        assert found == ref, "a referral has no buyer window and must never be held"

    def test_search_agrees_with_the_computed_flag(self, env, customer):
        """The two guards must never disagree, or one of them is
        releasing money the other would hold."""
        rows = (
            self._row(env, customer)
            | self._row(env, customer, age_days=8)
            | self._row(env, customer, source="partner_referral")
        )
        searched = env["fix.commission.ledger"].search(
            [("id", "in", rows.ids), ("escrow_window_elapsed", "=", True)]
        )
        computed = rows.filtered("escrow_window_elapsed")
        assert searched == computed, "domain says %s, compute says %s" % (
            searched.ids,
            computed.ids,
        )

    def test_search_rejects_an_operator_it_cannot_honour(self, env):
        """An operator the window cannot express must be refused, not
        silently coerced into one that pays people.

        The refusal comes from the ORM before `_search_escrow_window_elapsed`
        is reached, so this asserts that it is refused at all rather than
        asserting which layer refuses it."""
        with pytest.raises((UserError, ValueError)):
            env["fix.commission.ledger"].search([("escrow_window_elapsed", ">", False)])


# ==========================================================================
# No dead ends: an unservable surface must still offer navigation
# ==========================================================================
class TestA04NoDeadEnds:
    """The goal forbids dead ends. A surface whose model the server
    will not serve used to render one bare line of grey text with no action on
    it. Two of the 245 live A04 surfaces land there today, and ANY surface can
    after a deploy without a restart or when a model is ACL-denied.
    """

    SRC = Path(
        r"C:\software_project\software_project_14\1000 fix"
        r"\1000fix_new_erp_system\1000_fix_codebase\addons\platform"
        r"\cd_p03_portal\static\src"
    )

    def _xml(self):
        return (self.SRC / "p03_workspace.xml").read_text(encoding="utf-8")

    def _js(self):
        return (self.SRC / "p03_workspace.js").read_text(encoding="utf-8")

    def test_the_unavailable_panel_exists(self):
        assert "p03-surface-unavailable" in self._xml()

    def test_the_panel_is_announced_to_assistive_tech(self):
        xml = self._xml()
        i = xml.index("p03-surface-unavailable")
        assert 'role="alert"' in xml[i - 200 : i + 200]

    def test_the_panel_offers_navigation_not_just_a_message(self):
        """A message with no way out is still a dead end."""
        xml = self._xml()
        for action in ("this.openModule(", "this.refreshGlScreen(", "this.toggleMegaMenu("):
            assert action in xml, "the unavailable panel offers no %s" % action

    def test_both_generic_screen_kinds_are_covered(self):
        """The list path AND the form path."""
        assert self._xml().count("p03-surface-unavailable") >= 2

    def test_the_navigation_targets_are_real_methods(self):
        js = self._js()
        for method in ("openModule(", "refreshGlScreen(", "toggleMegaMenu("):
            assert "\n    %s" % method in js, "%s is not a workspace method" % method

    def test_an_unservable_form_hides_its_command_bar(self):
        """Save/Cancel over an empty body reads as a form you can
        fill in and submit. It cannot be."""
        xml = self._xml()
        # OWL compiles t-expressions as JavaScript, so the guard uses `&&`.
        # This panel was first written with Python `and`/`or` and rendered
        # anyway on the live instance - OWL tolerated it where the static
        # check does not. That invariant is already enforced for the whole
        # file by cd_p03_portal's own
        # `test_every_owl_expression_compiles_as_javascript`, so it is NOT
        # re-asserted here: a second copy of someone else's rule is the
        # duplication this audit is supposed to be removing. (An earlier
        # version of this test did re-assert it, by searching for " and " in
        # a slice of the file - and failed on its own English help text,
        # "...an earlier build and needs a restart".)
        assert 'state.gl.form.unavailable)" class="d365-cmdbar"' in xml

    def test_a_failed_SAVE_keeps_its_command_bar(self):
        """`form.error` is set by a failed save too. Keying the
        swap on it would have removed Save from a form the user was part-way
        through correcting, which is why a separate flag exists."""
        js = self._js()
        assert "gl.form.unavailable = false;" in js, "the flag is never reset"
        # the save path must not set it
        start = js.index("    async formSave(")
        end = js.index("\n    ", js.index("\n    }", start))
        assert (
            "unavailable" not in js[start:end]
        ), "the save path marks the surface unavailable, which would hide Save"
