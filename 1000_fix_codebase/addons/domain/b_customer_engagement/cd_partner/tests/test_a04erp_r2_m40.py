"""A04 ERP audit round 2 (21 Nov 2026), stream R2-4: the deferred M40 items.

  F23  deal registration checks every partner's open/protected deals and open
       leads and the customer's open M07 opportunities; a qualified lead and a
       won deal are handed to M07 with the partner attribution
  F26  one MDF mechanism (the fund / claim registers); legacy data migrated
  F28  the alliance benefit is an M11 promotion granted through price_for
       under an eligible check, never free text
  F25  TDS withheld on a partner payout is an M51 deduction the return sees
  F14  the "Authorisations Expiring" P03 pack, read through _scope

Every rule runs as the non-admin user it governs and is built so that only
the rule under test refuses it (each was mutation-checked; the report lists
the mutants). Business set-up the test does not prove is prepared as the
system through m40_fixtures."""

import base64
import types
from datetime import timedelta

import pytest
from odoo import fields
from odoo.addons.cd_partner.tests.m40_fixtures import (
    CONSENT,
    PAYOUT_PARAMS,
    configure_payout_accounts,
    ensure_account,
    guarded_write,
    make_onboardable,
)
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
PA = "cd_partner.group_fix_channel_"
TIER = "cd_entity_config.group_dofa_tier_%d"


def _mk(env, login, *xmlids):
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": login,
                "login": login,
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id] + [env.ref(x).id for x in xmlids])
                ],
            }
        )
    )


@pytest.fixture
def w(odoo_env):
    env = odoo_env
    x = types.SimpleNamespace(env=env, n=0)
    x.officer = _mk(env, "r24_officer", PA + "officer")
    x.manager = _mk(env, "r24_manager", PA + "manager")
    x.manager2 = _mk(env, "r24_manager2", PA + "manager")
    x.cco = _mk(env, "r24_cco", TIER % 2, TIER % 3)
    x.seller = _mk(env, "r24_seller", "sales_team.group_sale_salesman_all_leads")
    x.today = fields.Date.context_today(env.user)
    x.company = env.company
    params = env["ir.config_parameter"].sudo()
    for key in PAYOUT_PARAMS:
        params.set_param(key, False)
    params.set_param("cd_settlement_ext.partner_tds_rate_code", False)
    return x


def _party(w, name):
    return w.env["res.partner"].create({"name": name})


def _partner(w, ptype="reseller", **kw):
    w.n += 1
    vals = {
        "name": "R24 %s %d" % (ptype, w.n),
        "partner_id": _party(w, "R24 party %d" % w.n).id,
        "partner_type": ptype,
        "tin_number": "123456789012",
        "trade_license_no": "TL-R24-%d" % w.n,
    }
    vals.update(kw)
    p = w.env["fix.partner"].with_user(w.officer).create(vals)
    make_onboardable(w.env, p)
    p.with_user(w.manager).action_onboard()
    return p


def _deal(w, partner, customer, registered_on=None, value=50000.0):
    return (
        w.env["fix.partner.deal"]
        .with_user(w.officer)
        .create(
            {
                "name": "R24 deal %s" % partner.name,
                "partner_id": partner.id,
                "customer_id": customer.id,
                "value": value,
                "registered_on": registered_on or w.today,
            }
        )
    )


def _lead(w, partner, customer=None):
    vals = {
        "partner_id": partner.id,
        "customer_name": "R24 Customer",
        "customer_phone": "01711000000",
        "customer_email": "r24@example.test",
        "service_interest": "Laptop board repair",
        **CONSENT,
    }
    if customer:
        vals["customer_id"] = customer.id
    return w.env["fix.partner.lead"].with_user(w.officer).create(vals)


def _doc(w, record, user=None):
    return (
        w.env["ir.attachment"]
        .with_user(user or w.officer)
        .create(
            {
                "name": "doc.pdf",
                "res_model": record._name,
                "res_id": record.id,
                "datas": base64.b64encode(b"%PDF-1.4 r24"),
            }
        )
    )


# =================================================================== F23
def test_f23_an_earlier_registration_of_another_partner_is_a_clash(w):
    """Two partners register the same customer: the second is not protected
    by approving it first - the earlier registration is heard."""
    customer = _party(w, "R24 contested")
    p, q = _partner(w), _partner(w)
    _deal(w, q, customer, registered_on=w.today - timedelta(days=2))
    late = _deal(w, p, customer)
    result = late.with_user(w.manager).action_approve()
    assert late.state == "conflict" and late.conflict_id
    assert result == {"conflict": {late.id: late.conflict_id.name}}
    conflict = late.conflict_id.sudo()
    assert (conflict.partner_a_id, conflict.partner_b_id) == (q, p)
    assert "earlier deal" in conflict.description


def test_f23_another_partners_open_lead_is_a_clash(w):
    customer = _party(w, "R24 lead customer")
    p, q = _partner(w), _partner(w)
    _lead(w, q, customer)
    deal = _deal(w, p, customer)
    deal.with_user(w.manager).action_approve()
    assert deal.state == "conflict"
    conflict = deal.conflict_id.sudo()
    assert conflict.partner_a_id == q and "Open lead" in conflict.description


def test_f23_a_direct_m07_opportunity_is_a_clash_ruled_by_tier3(w):
    customer = _party(w, "R24 direct account")
    w.env["crm.lead"].create(
        {"name": "R24 direct opp", "type": "opportunity", "partner_id": customer.id}
    )
    p = _partner(w)
    deal = _deal(w, p, customer)
    deal.with_user(w.manager).action_approve()
    assert deal.state == "conflict"
    conflict = deal.conflict_id.sudo()
    # a direct clash: the partner is A, there is no partner B
    assert conflict.partner_a_id == p and not conflict.partner_b_id
    assert "direct sale" in conflict.description
    conflict.with_user(w.cco).action_rule_direct(notes="Key account stays direct")
    with pytest.raises(UserError, match="ruled for the other partner"):
        deal.with_user(w.manager).action_approve()


def test_f23_a_won_deal_is_handed_to_m07_with_its_attribution(w):
    customer = _party(w, "R24 won customer")
    p = _partner(w)
    deal = _deal(w, p, customer, value=80000.0)
    assert deal.with_user(w.manager).action_approve() is True
    deal.with_user(w.officer).action_mark_won()
    opp = deal.opportunity_id.sudo()
    assert deal.state == "won" and opp
    assert (opp.type, opp.partner_id, opp.expected_revenue) == ("opportunity", customer, 80000.0)
    assert (opp.fix_partner_id, opp.fix_partner_deal_id) == (p, deal)
    assert opp.lead_source == "referral"
    # idempotent
    assert deal._fix_handoff_opportunity() == deal.opportunity_id
    # the partner's own hand-off never clashes with its next deal on the customer
    again = _deal(w, p, customer)
    assert again.with_user(w.manager2).action_approve() is True
    assert again.state == "approved"


def test_f23_the_hand_off_attribution_is_guarded_on_m07(w):
    customer = _party(w, "R24 guard customer")
    p, q = _partner(w), _partner(w)
    deal = _deal(w, p, customer)
    deal.with_user(w.manager).action_approve()
    deal.with_user(w.officer).action_mark_won()
    opp = deal.opportunity_id.with_user(w.seller)
    with pytest.raises(UserError, match="cannot be set directly"), w.env.cr.savepoint():
        opp.write({"fix_partner_id": q.id})
    with pytest.raises(UserError, match="cannot be set directly"), w.env.cr.savepoint():
        w.env["crm.lead"].with_user(w.seller).create(
            {"name": "R24 forged", "type": "opportunity", "fix_partner_id": q.id}
        )
    assert deal.opportunity_id.sudo().fix_partner_id == p


def test_f23_a_qualified_lead_is_handed_to_m07(w):
    p = _partner(w, "referral")
    lead = _lead(w, p)
    assert not lead.opportunity_id
    lead.with_user(w.officer).action_qualify()
    m07 = lead.opportunity_id.sudo()
    assert m07 and m07.type == "lead" and not m07.partner_id
    assert (m07.contact_name, m07.phone) == ("R24 Customer", "01711000000")
    assert (m07.fix_partner_id, m07.fix_partner_lead_id) == (p, lead)
    # a lead naming its M33 party becomes an opportunity on it
    customer = _party(w, "R24 known party")
    lead2 = _lead(w, p, customer)
    lead2.with_user(w.officer).action_qualify()
    assert lead2.opportunity_id.sudo().type == "opportunity"
    assert lead2.opportunity_id.sudo().partner_id == customer


# =================================================================== F26
def test_f26_an_mdf_rebate_is_refused_with_a_pointer(w):
    p = _partner(w)
    vals = {
        "name": "R24 mdf",
        "partner_id": p.id,
        "period": "2026-Q4",
        "period_from": w.today - timedelta(days=30),
        "period_to": w.today,
        "rate": 0.05,
        "kind": "mdf",
    }
    Rebate = w.env["fix.partner.rebate"]
    for env_rebate in (Rebate.with_user(w.officer), Rebate.sudo()):
        with pytest.raises(ValidationError, match="MDF Claim"), w.env.cr.savepoint():
            env_rebate.create(dict(vals))
    rebate = Rebate.with_user(w.officer).create(dict(vals, kind="rebate"))
    with pytest.raises(ValidationError, match="MDF Fund"), w.env.cr.savepoint():
        rebate.with_user(w.officer).write({"kind": "mdf"})
    assert rebate.kind == "rebate"


def test_f26_the_migration_cancels_unapproved_legacy_mdf_only(w):
    p = _partner(w)
    Rebate = w.env["fix.partner.rebate"]
    legacy = {}
    for state in ("draft", "accrued", "approved", "paid"):
        rec = Rebate.with_user(w.officer).create(
            {"name": "R24 legacy %s" % state, "partner_id": p.id, "period": "2026-Q3", "rate": 0.05}
        )
        guarded_write(rec, {"state": state})
        legacy[state] = rec
    # the rows raised before M40-F26 (only SQL can make one now)
    w.env.cr.execute(
        "UPDATE fix_partner_rebate SET kind = 'mdf' WHERE id IN %s",
        (tuple(r.id for r in legacy.values()),),
    )
    Rebate.invalidate_model()
    volume = Rebate.with_user(w.officer).create(
        {"name": "R24 volume", "partner_id": p.id, "period": "2026-Q3", "rate": 0.05}
    )
    cancelled = Rebate._fix_migrate_mdf_rebates()
    assert sorted(cancelled) == sorted([legacy["draft"].id, legacy["accrued"].id])
    assert [legacy[s].state for s in ("draft", "accrued", "approved", "paid")] == [
        "cancelled",
        "cancelled",
        "approved",
        "paid",
    ]
    assert volume.state == "draft"
    assert "MDF Claims" in legacy["draft"].message_ids[0].body
    assert Rebate._fix_migrate_mdf_rebates() == []  # re-runnable


# =================================================================== F28
def _promotion(w, code, percent=10.0, used=0):
    promo = (
        w.env["fix.promotion"]
        .sudo()
        .create(
            {
                "name": "R24 %s" % code,
                "code": code,
                "discount_type": "percent",
                "value": percent,
                "channel": "all",
                "valid_from": w.today - timedelta(days=1),
                "valid_until": w.today + timedelta(days=30),
                "company_id": w.company.id,
            }
        )
    )
    guarded_write(promo, {"state": "active", "use_count": used})
    return promo


def _priced_item(w, code, price=1000.0):
    product = w.env["product.product"].create(
        {"name": "R24 item %s" % code, "default_code": code, "list_price": 1.0}
    )
    card = w.env["fix.rate.card"].create(
        {"product_code": code, "unit_price": price, "line_type": "labour"}
    )
    card._guarded().write({"state": "released"})
    return product


def _scheme(w, partner, promo, code):
    scheme = (
        w.env["fix.alliance.scheme"]
        .with_user(w.officer)
        .create(
            {
                "name": "R24 scheme %s" % code,
                "code": code,
                "partner_id": partner.id,
                "member_definition": "Bank staff",
                "eligibility_method": "member_id",
                "benefit_description": "10% off labour",
                "benefit_promotion_id": promo.id,
                "valid_from": w.today - timedelta(days=1),
            }
        )
    )
    return scheme


def test_f28_the_benefit_is_a_member_only_m11_promotion(w):
    alliance = _partner(w, "alliance")
    promo = _promotion(w, "R24-ALLY-1")
    product = _priced_item(w, "R24-SVC-1")
    scheme = _scheme(w, alliance, promo, "R24-SCH-1")
    assert scheme.benefit_ref == "R24-ALLY-1"
    assert "benefit_promotion_id" in scheme._fields and scheme._fields[
        "benefit_promotion_id"
    ].comodel_name == ("fix.promotion")
    scheme.with_user(w.manager).action_activate()
    member = _party(w, "R24 member")
    walk_in = _party(w, "R24 walk-in")
    check = (
        w.env["fix.alliance.eligibility.check"]
        .with_user(w.officer)
        .create(
            {
                "scheme_id": scheme.id,
                "customer_id": member.id,
                "member_ref": "EMP-1",
                "result": "eligible",
                "evidence_ref": "Staff card seen",
            }
        )
    )
    Card = w.env["fix.rate.card"].with_user(w.officer)
    # the public price carries no member-only promotion
    public = Card.price_for(product, partner=walk_in, channel="service")
    assert "R24-ALLY-1" not in public["promotions"]
    # the check grants it to the member it validated, through price_for
    granted = check.with_user(w.officer).price_for(product, channel="service")
    assert "R24-ALLY-1" in granted["promotions"]
    assert granted["promotion_discount"] > 0 and granted["price"] < public["price"]
    # a forged context for another customer grants nothing
    forged = Card.with_context(fix_alliance_check_id=check.id).price_for(
        product, partner=walk_in, channel="service"
    )
    assert "R24-ALLY-1" not in forged["promotions"]
    with pytest.raises(UserError, match="No alliance benefit"):
        check.with_user(w.officer).price_for(product, partner=walk_in)
    # a not-eligible check grants nothing either
    no = (
        w.env["fix.alliance.eligibility.check"]
        .with_user(w.officer)
        .create(
            {
                "scheme_id": scheme.id,
                "customer_id": walk_in.id,
                "member_ref": "EMP-2",
                "result": "not_eligible",
                "evidence_ref": "No card",
            }
        )
    )
    with pytest.raises(UserError, match="not eligible"):
        no.with_user(w.officer).price_for(product)


def test_f28_a_scheme_cannot_take_over_a_used_public_promotion(w):
    alliance = _partner(w, "alliance")
    used = _promotion(w, "R24-PUB-1", used=3)
    with pytest.raises(ValidationError, match="public discount"), w.env.cr.savepoint():
        _scheme(w, alliance, used, "R24-SCH-2")


def test_f28_activation_needs_a_released_promotion(w):
    alliance = _partner(w, "alliance")
    draft = (
        w.env["fix.promotion"]
        .sudo()
        .create(
            {
                "name": "R24 draft promo",
                "code": "R24-DRAFT-1",
                "discount_type": "percent",
                "value": 5.0,
                "company_id": w.company.id,
            }
        )
    )
    scheme = _scheme(w, alliance, draft, "R24-SCH-3")
    with pytest.raises(ValidationError, match="releases it"):
        scheme.with_user(w.manager).action_activate()
    assert scheme.state == "draft"


# =================================================================== F25
def _payout_scheme(w, tds=0.10, ptype="reseller"):
    return (
        w.env["fix.commission.scheme"]
        .sudo()
        .create(
            {
                "name": "R24 partner scheme",
                "scheme_type": "partner",
                "partner_type": ptype,
                "tds_rate": tds,
                "date_from": w.today - timedelta(days=30),
                "company_id": w.company.id,
            }
        )
    )


def _approved_claim(w, partner, amount=100000.0):
    fund = (
        w.env["fix.mdf.fund"]
        .with_user(w.officer)
        .create(
            {
                "name": "R24 MDF",
                "partner_id": partner.id,
                "period": "2026-Q4",
                "allocated": 200000.0,
            }
        )
    )
    fund.with_user(w.manager).action_open()
    claim = (
        w.env["fix.mdf.claim"]
        .with_user(w.officer)
        .create({"fund_id": fund.id, "amount": amount, "description": "R24 trade fair"})
    )
    claim.with_user(w.officer).write({"evidence_attachment_id": _doc(w, claim).id})
    claim.with_user(w.officer).action_submit()
    claim.with_user(w.manager2).action_approve()
    return claim


def _relay(w, etype, rec):
    event = (
        w.env["fix.event.outbox"]
        .sudo()
        .search(
            [("event_type", "=", etype), ("aggregate_id", "=", rec.id)], order="id desc", limit=1
        )
    )
    sub = w.env["fix.event.consumer"].sudo().search([("event_type", "=", etype)], limit=1)
    return getattr(w.env[sub.model].sudo(), sub.method)(event._relay_event_dict())


def test_f25_the_tds_withheld_on_a_payout_is_an_m51_deduction(w):
    configure_payout_accounts(w.env)
    _payout_scheme(w)
    p = _partner(w)
    claim = _approved_claim(w, p)
    result = _relay(w, "partner.mdf_claim_approved", claim)
    move = w.env["account.move"].sudo().browse(result["move_id"])
    line = w.env["fix.withholding.line"].sudo().browse(result["withholding_id"])
    # TIN on file, no PSR: one statutory default (x1.5) on the s.94 10% row
    assert (line.tax_kind, line.state, line.partner_id) == ("tds", "withheld", p.partner_id)
    assert (line.base_amount, line.rate, line.multiplier, line.amount) == (
        100000.0,
        10.0,
        1.5,
        15000.0,
    )
    assert line.rate_id.code == "commission" and line.partner_tin == "123456789012"
    assert (line.move_id, line.source_model) == (move, "fix.mdf.claim")
    assert line.paid_by_bank and not line.psr_received and line.statutory_shortfall == 0.0
    tds_lines = move.line_ids.filtered(lambda ml: ml.account_id.code == "200905")
    assert round(sum(tds_lines.mapped("credit")), 2) == 15000.0
    pay = w.env["fix.payment.execution"].sudo().browse(result["id"])
    assert pay.amount == 85000.0
    # the M51 TDS return sees it in its quarter
    assert (
        w.env["fix.withholding.line"]
        .sudo()
        .search_count(
            [("tax_kind", "=", "tds"), ("period", "=", line.period), ("id", "=", line.id)]
        )
    )


def test_f25_a_partner_with_no_tin_suffers_the_statutory_uplift(w):
    configure_payout_accounts(w.env)
    _payout_scheme(w, ptype="referral")
    # a referral partner onboards without an e-TIN (FLAW-33.1 names the others)
    p = _partner(w, "referral", tin_number=False)
    result = _relay(w, "partner.mdf_claim_approved", _approved_claim(w, p, 10000.0))
    line = w.env["fix.withholding.line"].sudo().browse(result["withholding_id"])
    # no PSR and no TIN: two defaults, 10% x 2.25 (the scheme's 1.5 under-withheld)
    assert (line.multiplier, line.amount, line.defaults_count) == (2.25, 2250.0, 2)
    assert w.env["fix.payment.execution"].sudo().browse(result["id"]).amount == 7750.0


def test_f25_the_tds_must_reach_m51s_payable(w):
    configure_payout_accounts(w.env)
    _payout_scheme(w)
    ensure_account(w.env, "200202")
    w.env["ir.config_parameter"].sudo().set_param(
        "cd_tax_engine_bd.account_code.tds_payable", "200202"
    )
    p = _partner(w)
    claim = _approved_claim(w, p)
    with pytest.raises(UserError, match="is not M51's"):
        _relay(w, "partner.mdf_claim_approved", claim)


def test_f25_two_tds_rates_are_refused(w):
    configure_payout_accounts(w.env)
    _payout_scheme(w, tds=0.05)
    p = _partner(w)
    claim = _approved_claim(w, p)
    with pytest.raises(UserError, match="One statutory rate"):
        _relay(w, "partner.mdf_claim_approved", claim)


# =================================================================== F14
def test_f14_authorisations_expiring_pack_is_scoped_and_banded(w):
    from odoo.addons.cd_p03_portal.controllers.a04 import m40

    p = _partner(w, "brand")
    other_co = w.env["res.company"].create({"name": "R24 Other Co"})
    q = w.env["fix.partner"].create(
        {
            "name": "R24 other-company partner",
            "partner_id": _party(w, "R24 oc").id,
            "partner_type": "brand",
            "company_id": other_co.id,
        }
    )
    made = {}
    for partner, days in ((p, 20), (p, 60), (p, 120), (p, 400), (q, 25)):
        auth = (
            w.env["fix.partner.authorisation"]
            .sudo()
            .create(
                {
                    "name": "R24 auth %s %d" % (partner.name, days),
                    "partner_id": partner.id,
                    "valid_from": w.today - timedelta(days=10),
                    "valid_to": w.today + timedelta(days=days),
                }
            )
        )
        guarded_write(auth, {"state": "active"})
        made[(partner.id, days)] = auth
    viewer = _mk(w.env, "r24_viewer", PA + "officer")
    env = w.env(user=viewer.id, context=dict(w.env.context, allowed_company_ids=[w.company.id]))
    pack = m40.authorisations_expiring(env)
    rows = {r["authorisation"]: r for r in pack["rows"]}
    assert rows[made[(p.id, 20)].name]["band"] == "T-30"
    assert rows[made[(p.id, 60)].name]["band"] == "T-90"
    assert rows[made[(p.id, 120)].name]["band"] == "T-180"
    assert made[(p.id, 400)].name not in rows  # beyond T-180, outside the default period
    assert made[(q.id, 25)].name not in rows  # another company
    # the requested period is honoured on valid_to
    narrow = m40.authorisations_expiring(
        env, date_from=w.today + timedelta(days=50), date_to=w.today + timedelta(days=70)
    )
    assert [r["authorisation"] for r in narrow["rows"]] == [made[(p.id, 60)].name]
    assert set(pack["cols"]) <= set(pack["labels"])


# =================================================================== wiring
class TestDeployment:
    def test_the_round2_wiring_exists(self, odoo_env):
        env = odoo_env
        from odoo.addons.cd_p03_portal.controllers.a04 import m40, writable

        assert "authorisations_expiring" in m40.REPORTS
        for model, fname in (
            ("crm.lead", "fix_partner_id"),
            ("crm.lead", "fix_partner_lead_id"),
            ("crm.lead", "fix_partner_deal_id"),
            ("fix.partner.deal", "opportunity_id"),
            ("fix.partner.lead", "opportunity_id"),
            ("fix.alliance.scheme", "benefit_promotion_id"),
            ("fix.promotion", "alliance_scheme_ids"),
        ):
            assert fname in env[model]._fields, (model, fname)
        assert {"fix_partner_id", "fix_partner_lead_id", "fix_partner_deal_id"} <= env[
            "crm.lead"
        ]._fix_guarded_fields()
        assert "benefit_promotion_id" in writable.WRITABLE["fix.alliance.scheme"]
        assert "kind" not in writable.WRITABLE["fix.partner.rebate"]
        assert (
            env["ir.module.module"].sudo().search([("name", "=", "cd_crm_ext")]).state
            == "installed"
        )
        consumer = (
            env["fix.event.consumer"]
            .sudo()
            .search([("event_type", "=", "partner.mdf_claim_approved")])
        )
        assert consumer and consumer.method == "consume_partner_mdf_claim_approved"
        # the default M51 rate row partner payouts are withheld under exists
        assert (
            env["fix.tax.rate"]
            .sudo()
            .find_rate("tds", "commission", fields.Date.today(), env.company)
        )
