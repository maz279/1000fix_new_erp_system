"""A06 M44 controls (Import, Trade Compliance & Landed Cost).

One test per gap probe of working/A06_evidence/probes/m44/probe_m44.py (named
after the probe id), each running the probe's attack as a NON-ADMIN user and
asserting the control now holds, plus proper-path tests: an Import Officer
runs the import end to end, an Import Approver approves, Finance pays the
duty, and finalising the landed cost revalues the stock and posts the right
journal entry. Live ORM inside the rolled-back odoo_env fixture.

Rates used below (CD 25, RD 3, SD 20, VAT 15, AT 5, AIT 5) are TEST INPUTS
chosen to exercise each base of the FR-ITC-033 cascade; they are not claimed
to be the NBR tariff for any heading.
"""

from __future__ import annotations

import json
import types
import uuid
from datetime import timedelta

import pytest
from odoo import fields
from odoo.addons.cd_import_order.models.fix_import_common import stock_valuation_code
from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
OFFICER = "cd_import_order.group_fix_import_officer"
APPROVER = "cd_import_order.group_fix_import_approver"
FINANCE = "account.group_account_user"
TIER4 = "cd_entity_config.group_dofa_tier_4"
MODELS = [
    "fix.import.order",
    "fix.import.proforma",
    "fix.import.lc",
    "fix.import.lca",
    "fix.import.hs",
    "fix.import.irc",
    "fix.import.shipdoc",
    "fix.import.arrival",
    "fix.import.boe",
    "fix.import.boe.line",
    "fix.import.landed",
]
ROLES = (
    "inventory",
    "duty_clearing",
    "landed_accrual",
    "vat_input",
    "at_input",
    "ait_advance",
    "variance",
    "grni",
    "lc_clearing",
    "fx_difference",
    "lc_margin",
)
FX = 117.5


_ENV = {}


def _refused(fn, *args, match=None, **kw):
    env = getattr(getattr(fn, "__self__", None), "env", None) or _ENV["env"]
    with pytest.raises(REFUSED, match=match), env.cr.savepoint():
        fn(*args, **kw)
        env.flush_all()


def _attempt(env, fn):
    """True when the system refused fn (ORM, ACL, rule or a DB constraint)."""
    try:
        with env.cr.savepoint():
            fn()
            env.flush_all()
    except REFUSED:
        return True
    except Exception as exc:  # IntegrityError / CheckViolation
        if "Violation" in type(exc).__name__ or "Integrity" in type(exc).__name__:
            return True
        raise
    return False


def _user(env, login, ous, *groups):
    ids = [env.ref("base.group_user").id] + [env.ref(g).id for g in groups]
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": login,
                "login": login,
                "group_ids": [(6, 0, ids)],
                "company_ids": [(6, 0, env.company.ids)],
                "company_id": env.company.id,
                "assigned_operating_unit_ids": [(6, 0, ous.ids)],
                "default_operating_unit_id": ous[:1].id,
            }
        )
    )


@pytest.fixture
def c(odoo_env):
    env = odoo_env
    _ENV["env"] = env
    tag = uuid.uuid4().hex[:6].upper()
    x = types.SimpleNamespace(env=env, tag=tag)
    x.co = env.company
    x.today = fields.Date.context_today(env["fix.import.order"])
    x.usd = env.ref("base.USD")
    x.bdt = env.ref("base.BDT")
    x.ou = env["operating.unit"].search([("company_id", "=", x.co.id)], limit=1)
    x.ou2 = env["operating.unit"].create(
        {
            "name": "M44T OU-B %s" % tag,
            "code": "M4B%s" % tag[:4],
            "company_id": x.co.id,
            "partner_id": env["res.partner"].create({"name": "M44T OU-B partner"}).id,
        }
    )
    x.clerk = _user(env, "m44t_clerk_%s" % tag, x.ou)
    x.officer = _user(env, "m44t_officer_%s" % tag, x.ou, OFFICER)
    x.officer2 = _user(env, "m44t_officer2_%s" % tag, x.ou, OFFICER)
    x.approver = _user(env, "m44t_approver_%s" % tag, x.ou, APPROVER, TIER4)
    x.approver2 = _user(env, "m44t_approver2_%s" % tag, x.ou, APPROVER)
    x.tier_only = _user(env, "m44t_tier_%s" % tag, x.ou, TIER4)
    x.finance = _user(env, "m44t_finance_%s" % tag, x.ou, FINANCE)
    x.outsider = _user(env, "m44t_outsider_%s" % tag, x.ou2, OFFICER)
    # ---- GL configuration (business decisions: configured, never defaulted) ----
    icp = env["ir.config_parameter"].sudo()
    x.acc = {}
    types_ = {
        "inventory": "asset_current",
        "duty_clearing": "asset_current",
        "landed_accrual": "liability_current",
        "vat_input": "asset_current",
        "at_input": "asset_current",
        "ait_advance": "asset_current",
        "variance": "expense",
        "grni": "liability_current",
        "lc_clearing": "asset_current",
        "fx_difference": "expense",
        "lc_margin": "asset_current",
    }
    for i, role in enumerate(ROLES):
        code = "M44%s%d" % (tag[:3], i)
        if role == "inventory":
            # The stock line posts to M15's valuation suspense account, which
            # the M19 cutover later moves to Inventory (no double count).
            code = stock_valuation_code(env)
            found = env["account.account"].search(
                [("code", "=", code), ("company_ids", "in", x.co.id)], limit=1
            )
            if found:
                x.acc[role] = found
                continue
        x.acc[role] = env["account.account"].create(
            {
                "code": code,
                "name": "M44T %s" % role,
                "account_type": types_[role],
                "company_ids": [(6, 0, x.co.ids)],
            }
        )
        icp.set_param("cd_import_order.account_code.%s" % role, code)
    bank_acc = env["account.account"].create(
        {
            "code": "M44%sB" % tag[:3],
            "name": "M44T bank",
            "account_type": "asset_cash",
            "company_ids": [(6, 0, x.co.ids)],
        }
    )
    x.bank = env["account.journal"].create(
        {
            "name": "M44T Duty Bank %s" % tag,
            "type": "bank",
            "code": "M%s" % tag[:4],
            "company_id": x.co.id,
            "default_account_id": bank_acc.id,
        }
    )
    icp.set_param("cd_import_order.payment_journal_code", x.bank.code)
    # A06 ERP D6: an LC remittance settles the supplier in AP (advance before
    # the bill); the advances account is a test account
    x.advance_acc = env["account.account"].create(
        {
            "code": "M44%sV" % tag[:3],
            "name": "M44T advances to suppliers",
            "account_type": "asset_current",
            "company_ids": [(6, 0, x.co.ids)],
        }
    )
    icp.set_param("cd_ap_ext.account_code.supplier_advance", x.advance_acc.code)
    icp.set_param("cd_import_order.landing_charge_pct", "1.0")
    # ---- the bank's LC facility (M50), sanctioned limit BDT 5,000,000 ----
    x.facility_liability = env["account.account"].create(
        {
            "code": "M44%sF" % tag[:3],
            "name": "M44T LC acceptances",
            "account_type": "liability_current",
            "company_ids": [(6, 0, x.co.ids)],
        }
    )
    x.facility = env["fix.bank.facility"].create(
        {
            "name": "M44T LC limit %s" % tag,
            "company_id": x.co.id,
            "lender_id": env["res.partner"].create({"name": "M44T AD Bank"}).id,
            "facility_type": "lc",
            "currency_id": x.bdt.id,
            "limit_amount": 5000000.0,
            "liability_account_id": x.facility_liability.id,
            "expiry_date": x.today + timedelta(days=365),
        }
    )
    x.facility.action_activate()
    # ---- master data (superuser: reference data set up for the test) ----
    env["fix.import.irc"].search([("company_id", "=", x.co.id)]).sudo()._guarded().write(
        {"state": "expired"}
    )
    x.irc = env["fix.import.irc"].create(
        {"irc_no": "IRC-%s" % tag, "company_id": x.co.id, "valid_to": x.today + timedelta(days=365)}
    )
    x.loc = env["fix.stock.location"].create(
        {
            "name": "M44T Central %s" % tag,
            "code": "M4%s" % tag,
            "location_type": "central",
            "company_id": x.co.id,
            "operating_unit_id": x.ou.id,
        }
    )
    x.product = env["product.product"].create({"name": "M44T LCD panel %s" % tag})
    x.product2 = env["product.product"].create({"name": "M44T battery %s" % tag})
    x.part = env["fix.spare.part"].create(
        {"name": "M44T LCD %s" % tag, "part_number": "M44-LCD-%s" % tag, "product_id": x.product.id}
    )
    x.part2 = env["fix.spare.part"].create(
        {
            "name": "M44T Battery %s" % tag,
            "part_number": "M44-BAT-%s" % tag,
            "product_id": x.product2.id,
        }
    )
    x.code = "8524.11.00"
    x.tariff = env["fix.import.tariff"].create(
        {
            "hs_code": x.code,
            "sro_ref": "TEST-SRO-%s" % tag,
            "date_from": x.today - timedelta(days=30),
            "cd_pct": 25,
            "rd_pct": 3,
            "sd_pct": 20,
            "vat_pct": 15,
            "at_pct": 5,
            "ait_pct": 5,
        }
    )
    x.tariff.action_activate()
    x.hs = env["fix.import.hs"].create(
        {"product_id": x.product.id, "hs_code": x.code, "ruling_ref": "RUL-%s" % tag}
    )
    x.hs.action_rule()
    x.hs2 = env["fix.import.hs"].create(
        {"product_id": x.product2.id, "hs_code": x.code, "ruling_ref": "RUL2-%s" % tag}
    )
    x.hs2.action_rule()
    x.supplier = env["res.partner"].create(
        {"name": "M44T Shenzhen Parts %s" % tag, "is_company": True}
    )
    x.order = _order(x)
    # BRU-ITC-12: a licensed C&F agent, active in M42, approved
    x.agent = _agent(x)
    x.agent.action_approve()
    # BRU-ITC-13: FOB puts the transit risk on 1000FiX: cover of the CIF value
    x.insurer = env["res.partner"].create({"name": "M44T Insurer %s" % tag, "is_company": True})
    x.cover = _cover(x)
    x.cover.action_verify()
    return x


def _agent(c, **kw):
    supplier = c.env["fix.supplier"].create(
        {
            "name": "M44T C&F Agent %s %s" % (c.tag, kw.get("suffix", "1")),
            "partner_id": c.env["res.partner"].create({"name": "M44T C&F %s" % c.tag}).id,
            "status": kw.pop("status", "active"),
        }
    )
    vals = {
        "name": "M44T Clearing %s" % c.tag,
        "supplier_id": supplier.id,
        "licence_no": "CNF-%s-%s" % (c.tag, kw.pop("suffix", "1")),
        "licence_expiry": c.today + timedelta(days=200),
    }
    vals.update(kw)
    return c.env["fix.import.cnf.agent"].create(vals)


def _cover(c, order=None, user=None, **kw):
    vals = {
        "order_id": (order or c.order).id,
        "insurer_id": c.insurer.id,
        "policy_no": "MC-%s" % c.tag,
        "currency_id": c.usd.id,
        "sum_insured": 10600.0,
        "premium": 100.0,
        "cover_from": c.today - timedelta(days=1),
        "cover_to": c.today + timedelta(days=120),
    }
    vals.update(kw)
    Insurance = c.env["fix.import.insurance"]
    return (Insurance.with_user(user) if user else Insurance).create(vals)


def _order(c, user=None, **kw):
    vals = {
        "name": "M44T-IMP-%s" % c.tag,
        "supplier_id": c.supplier.id,
        "operating_unit_id": c.ou.id,
        "currency_id": c.usd.id,
        "fob_value": 10000.0,
        "freight_cost": 500.0,
        "insurance_cost": 100.0,
        "fx_rate": FX,
        "fx_rate_source": "AD bank contract",
        "fx_rate_date": c.today,
        "incoterm": "fob",
        "location_id": c.loc.id,
        "line_ids": [
            (0, 0, {"part_id": c.part.id, "hs_id": c.hs.id, "quantity": 10, "unit_price": 600.0}),
            (0, 0, {"part_id": c.part2.id, "hs_id": c.hs2.id, "quantity": 20, "unit_price": 200.0}),
        ],
    }
    vals.update(kw)
    return c.env["fix.import.order"].with_user(user or c.officer).create(vals)


@pytest.fixture
def p03(c):
    import odoo.addons.cd_p03_portal.controllers.p03_generic_api as g
    import odoo.addons.cd_p03_portal.controllers.p03_service_order_api as s

    ctl = g.P03GenericApiController()
    cls = g.P03GenericApiController
    mw = getattr(cls.model_write, "original_endpoint", cls.model_write)
    ma = getattr(cls.model_action, "original_endpoint", cls.model_action)
    old_g, old_s = getattr(g, "request", None), getattr(s, "request", None)

    def as_user(user):
        req = types.SimpleNamespace(env=c.env(user=user.id))
        g.request = req
        s.request = req

    as_user(c.officer)
    try:
        yield types.SimpleNamespace(
            write=lambda **kw: mw(ctl, **kw), action=lambda **kw: ma(ctl, **kw), as_user=as_user
        )
    finally:
        g.request, s.request = old_g, old_s


# ---------------------------------------------------------------- stage helpers
def proforma(c, user=None, **kw):
    vals = {
        "order_id": c.order.id,
        "proforma_no": "PI-%s" % c.tag,
        "currency_id": c.usd.id,
        "amount": 10000.0,
    }
    vals.update(kw)
    return c.env["fix.import.proforma"].with_user(user or c.officer).create(vals)


def stage_proforma(c):
    pf = proforma(c)
    pf.with_user(c.approver).action_approve()
    return pf


def lc(c, user=None, **kw):
    vals = {
        "order_id": c.order.id,
        "lc_no": "LC-%s" % c.tag,
        "bank": "Test AD Bank",
        "amount": 1175000.0,
        "currency_id": c.bdt.id,
        "expiry": c.today + timedelta(days=90),
        "margin_pct": 10,
        "facility_id": c.facility.id,
    }
    vals.update(kw)
    return c.env["fix.import.lc"].with_user(user or c.officer).create(vals)


def lca(c, letter, user=None, **kw):
    vals = {
        "lc_id": letter.id,
        "lca_no": "LCA-%s-%d" % (c.tag, letter.id),
        "amount": letter.amount,
        "currency_id": letter.currency_id.id,
    }
    vals.update(kw)
    return c.env["fix.import.lca"].with_user(user or c.officer).create(vals)


def stage_lc_applied(c, **kw):
    stage_proforma(c)
    letter = lc(c, **kw)
    lca(c, letter).with_user(c.approver).action_approve()
    letter.with_user(c.officer).action_apply()
    return letter


def stage_lc_open(c):
    letter = stage_lc_applied(c)
    approve_via_inbox(letter, c.approver, requester=c.officer, justification="Import of LCD panels")
    letter.with_user(c.officer).action_open()
    return letter


def shipdoc(c, doc_type, user=None, ref=None):
    return (
        c.env["fix.import.shipdoc"]
        .with_user(user or c.officer)
        .create(
            {
                "order_id": c.order.id,
                "doc_type": doc_type,
                "ref": ref or "%s-%s" % (doc_type.upper(), c.tag),
            }
        )
    )


def stage_advance(c, order=None):
    """Scorecard 24: an approved advance, the instrument a B/L ships against
    when there is no LC."""
    advance = (
        c.env["fix.import.advance"]
        .with_user(c.officer)
        .create(
            {
                "order_id": (order or c.order).id,
                "amount": 100.0,
                "currency_id": c.usd.id,
                "bank": "Test AD Bank",
                "guarantee_ref": "APG-%s" % c.tag,
            }
        )
    )
    advance.action_request()
    advance.with_user(c.approver).action_approve("Test instrument for the fixture")
    return advance


def stage_shipped(c):
    if not (
        c.env["fix.import.lc"].search_count(
            [("order_id", "=", c.order.id), ("state", "=", "opened")]
        )
        or c.env["fix.import.advance"].search_count(
            [("order_id", "=", c.order.id), ("state", "=", "approved")]
        )
    ):
        stage_advance(c)
    for doc_type in ("bl", "invoice", "packing"):
        shipdoc(c, doc_type).with_user(c.officer).action_receive()


def arrival(c, user=None, **kw):
    vals = {
        "order_id": c.order.id,
        "vessel": "MV M44T",
        "eta": c.today,
        "etd": c.today - timedelta(days=20),
        "free_days": 7,
        "cnf_agent_id": c.agent.id,
    }
    vals.update(kw)
    return c.env["fix.import.arrival"].with_user(user or c.officer).create(vals)


def boe(c, user=None, lines=None, **kw):
    lines = (
        lines
        if lines is not None
        else [(0, 0, {"order_line_id": ln.id, "quantity": ln.quantity}) for ln in c.order.line_ids]
    )
    vals = {
        "order_id": c.order.id,
        "boe_no": "BE-%s" % c.tag,
        "line_ids": lines,
        "cnf_agent_id": c.agent.id,
        # M44-07: the customs rate of the BoE date (here equal to the commitment)
        "customs_fx_rate": FX,
    }
    vals.update(kw)
    return c.env["fix.import.boe"].with_user(user or c.officer).create(vals)


def assess_and_pay(c, bill):
    bill.with_user(c.officer).action_assess()
    bill.with_user(c.officer).write(
        {"customs_assessed_total": bill.total_tax, "payment_ref": "CH-%s" % c.tag}
    )
    bill.with_user(c.finance).action_pay()
    return bill


def stage_cleared(c):
    stage_shipped(c)
    arr = arrival(c)
    arr.with_user(c.officer).action_arrive()
    bill = assess_and_pay(c, boe(c))
    arr.with_user(c.officer).write({"release_ref": "RO-%s" % c.tag})
    arr.with_user(c.officer).action_clear()
    return arr, bill


def stage_received(c):
    arr, bill = stage_cleared(c)
    c.order.with_user(c.officer).action_receive()
    return arr, bill


def landed(c, user=None, **kw):
    vals = {
        "order_id": c.order.id,
        "sheet_type": "final",
        "freight": 45000.0,
        "insurance": 8000.0,
        "clearing_charges": 25000.0,
    }
    vals.update(kw)
    return c.env["fix.import.landed"].with_user(user or c.officer).create(vals)


def _lines(move):
    return {(ln.account_id.id, round(ln.debit - ln.credit, 2)) for ln in move.line_ids}


def _net(move, account):
    return round(sum(ln.debit - ln.credit for ln in move.line_ids if ln.account_id == account), 2)


def _bucket(c, part):
    return c.env["fix.stock.onhand"]._bucket(part, c.loc, "owned")


# ================================================================ S1 roles
def test_m44_s1_plain_user_has_read_only(c):
    """S1/M44-8: a plain employee reads the import documents but writes none."""
    for model in [*MODELS, "fix.import.tariff", "fix.import.lc.amendment", "fix.import.lc.payment"]:
        records = c.env[model].with_user(c.clerk)
        assert records.has_access("read"), model
        assert not records.has_access("write"), model
        assert not records.has_access("create"), model
    assert _attempt(
        c.env, lambda: c.env["fix.import.order"].with_user(c.clerk).create({"name": "CLERK-ORDER"})
    )


def test_m44_s1_groups_shipped_approver_empty(c):
    """The officer group carries the admin; the approver group ships EMPTY."""
    officer = c.env.ref(OFFICER)
    approver = c.env.ref(APPROVER)
    assert c.env.ref("base.user_admin") in officer.user_ids
    assert approver.user_ids <= (c.approver | c.approver2)


# ================================================================ proforma
def test_m44_p01_proforma_not_approved_by_creator(c):
    pf = proforma(c)
    _refused(pf.with_user(c.officer).action_approve, match="Import Approver")
    # an approver who also recorded it is refused too
    own = proforma(c, user=c.officer, proforma_no="PI-OWN")
    c.env.ref(APPROVER).sudo().write({"user_ids": [(4, c.officer.id)]})
    _refused(own.with_user(c.officer).action_approve, match="Segregation of duties")


def test_m44_p02_rejected_proforma_not_reapproved(c):
    _refused(lambda: proforma(c, state="rejected"), match="workflow")
    pf = proforma(c)
    pf.with_user(c.approver).action_reject("wrong price")
    _refused(pf.with_user(c.approver2).action_approve, match="received")


def test_m44_p03_proforma_reconciled_to_order(c):
    pf = proforma(c, amount=100000.0)
    _refused(pf.with_user(c.approver).action_approve, match="does not reconcile")


def test_m44_p04_proforma_state_by_write(c):
    pf = proforma(c)
    _refused(pf.with_user(c.officer).write, {"state": "approved"}, match="workflow")


def test_m44_p05_proforma_state_via_p03(c, p03):
    pf = proforma(c)
    out = p03.write(model="fix.import.proforma", record_id=pf.id, values={"state": "approved"})
    pf.invalidate_recordset()
    assert out.get("error") and pf.state == "received", out


def test_m44_p06_proforma_needs_valid_irc(c):
    c.irc.sudo()._guarded().write({"state": "suspended"})
    pf = proforma(c)
    _refused(pf.with_user(c.approver).action_approve, match="Import Registration Certificate")


def test_m44_p07_proforma_amount_pinned_after_approval(c):
    pf = stage_proforma(c)
    _refused(pf.with_user(c.officer).write, {"amount": 99999.0}, match="cannot be changed")
    assert pf.state == "approved" and pf.amount == 10000.0


def test_m44_p08_proforma_p03_action_by_creator(c, p03):
    pf = proforma(c)
    out = p03.action(model="fix.import.proforma", ids=[pf.id], method="action_approve")
    pf.invalidate_recordset()
    assert not out.get("success") and pf.state == "received", out
    p03.as_user(c.approver)
    out = p03.action(model="fix.import.proforma", ids=[pf.id], method="action_approve")
    pf.invalidate_recordset()
    assert out.get("success") and pf.state == "approved" and pf.decided_by_id == c.approver, out


# ================================================================ letter of credit
def test_m44_l01_open_from_draft_refused(c):
    letter = lc(c)
    _refused(letter.with_user(c.officer).action_open, match="applied")


def test_m44_l02_applicant_cannot_open_without_routed_approval(c):
    letter = stage_lc_applied(c)
    _refused(letter.with_user(c.officer).action_open, match="not approved")
    # nor approve it directly, nor decide it in the inbox as the applicant
    _refused(letter.with_user(c.approver).action_dofa_approve, match="inbox")
    letter.with_user(c.officer).action_request_approval(justification="Import")
    assigned = letter.approval_request_id.task_ids.mapped("assigned_user_id")
    assert c.officer not in assigned and c.approver in assigned
    # a DOFA tier holder who is not an Import Approver gets no task
    assert c.tier_only not in assigned


def test_m44_l03_lc_needs_approved_lca(c):
    stage_proforma(c)
    letter = lc(c)
    _refused(letter.with_user(c.officer).action_apply, match="LCA")


def test_m44_l04_lc_needs_approved_proforma(c):
    letter = lc(c)
    lca(c, letter).with_user(c.approver).action_approve()
    _refused(letter.with_user(c.officer).action_apply, match="proforma")


def test_m44_l05_lc_above_order_value_refused(c):
    stage_proforma(c)
    letter = lc(c, amount=500_000_000.0)
    lca(c, letter).with_user(c.approver).action_approve()
    _refused(letter.with_user(c.officer).action_apply, match="needs an approved amendment")


def test_m44_l05b_lc_tolerance_is_configurable(c):
    c.env["ir.config_parameter"].sudo().set_param("cd_import_order.lc_value_tolerance_pct", "10")
    stage_proforma(c)
    letter = lc(c, amount=1175000.0 * 1.05)
    lca(c, letter).with_user(c.approver).action_approve()
    letter.with_user(c.officer).action_apply()
    assert letter.state == "applied"


def test_m44_l06_margin_out_of_range(c):
    assert _attempt(c.env, lambda: lc(c, lc_no="LC-NEG", margin_pct=-50))
    assert _attempt(c.env, lambda: lc(c, lc_no="LC-BIG", margin_pct=500))


def test_m44_l07_expired_lc_not_applied_or_opened(c):
    stage_proforma(c)
    letter = lc(c, expiry=c.today - timedelta(days=10))
    lca(c, letter).with_user(c.approver).action_approve()
    _refused(letter.with_user(c.officer).action_apply, match="future")


def test_m44_l08_opened_lc_amount_changes_only_by_amendment(c):
    letter = stage_lc_open(c)
    _refused(letter.with_user(c.officer).write, {"amount": letter.amount * 10}, match="amendment")
    assert letter.amount == 1175000.0


def test_m44_l08b_amendment_record_reapproved_at_new_band(c):
    """BRU-ITC-20: amendment = a record with history, approved on the NEW total."""
    letter = stage_lc_open(c)
    am = (
        c.env["fix.import.lc.amendment"]
        .with_user(c.officer)
        .create({"lc_id": letter.id, "new_amount": 1300000.0, "reason": "Price revision"})
    )
    _refused(am.with_user(c.officer).action_apply_amendment, match="not approved")
    approve_via_inbox(am, c.approver, requester=c.officer, justification="Price revision")
    assert am.dofa_approved_amount == pytest.approx(1300000.0)
    am.with_user(c.officer).action_apply_amendment()
    assert letter.amount == 1300000.0 and am.old_amount == 1175000.0 and am.state == "applied"
    _refused(am.with_user(c.officer).write, {"new_amount": 9_000_000.0}, match="applied")


def test_m44_l09_amended_state_not_writable(c):
    letter = stage_lc_open(c)
    _refused(letter.with_user(c.officer).write, {"state": "amended"}, match="workflow")


def test_m44_l10_lc_state_by_write(c):
    letter = lc(c)
    _refused(letter.with_user(c.officer).write, {"state": "opened"}, match="workflow")


def test_m44_l11_lc_state_via_p03(c, p03):
    letter = lc(c)
    out = p03.write(model="fix.import.lc", record_id=letter.id, values={"state": "opened"})
    letter.invalidate_recordset()
    assert out.get("error") and letter.state == "draft", out


def test_m44_l12_duplicate_lc_number(c):
    lc(c)
    assert _attempt(c.env, lambda: lc(c, user=c.officer2))


def test_m44_l13_close_needs_documents_and_retirement(c):
    letter = stage_lc_open(c)
    _refused(letter.with_user(c.officer).action_close, match="retired")


def test_m44_l13b_payments_cannot_exceed_lc(c):
    letter = stage_lc_open(c)
    Pay = c.env["fix.import.lc.payment"]
    _refused(
        lambda: Pay.with_user(c.officer).create(
            {"lc_id": letter.id, "amount": 1000.0, "reference": "X"}
        )
    )
    Pay.with_user(c.finance).create({"lc_id": letter.id, "amount": 1000000.0, "reference": "TT-1"})
    _refused(
        lambda: Pay.with_user(c.finance).create(
            {"lc_id": letter.id, "amount": 175001.0, "reference": "TT-2"}
        ),
        match="above the LC amount",
    )
    shipdoc(c, "bl").with_user(c.officer).action_receive()
    letter.with_user(c.officer).action_close()
    assert letter.state == "closed"


def test_m44_l14_lc_closed_by_write(c):
    letter = lc(c)
    _refused(letter.with_user(c.officer).write, {"state": "closed"}, match="workflow")


def test_m44_r4_lc_routing_ignores_repointed_matrix_group(c):
    letter = lc(c)
    rule = c.env["fix.approval.matrix"].new({"approver_group_id": c.env.ref("base.group_user").id})
    assert letter._approval_group_for(rule, "tier_4") == c.env.ref(TIER4)


def test_m44_r4_lc_terms_change_voids_approval(c):
    letter = stage_lc_applied(c)
    approve_via_inbox(letter, c.approver, requester=c.officer, justification="Import")
    assert letter.dofa_approved
    letter.with_user(c.officer2).write({"expiry": c.today + timedelta(days=60)})
    assert not letter.dofa_approved and letter.approval_state == "none"
    assert letter.terms_changed_by_id == c.officer2


# ================================================================ LCA
def test_m44_a01_lca_not_approved_by_creator(c):
    letter = lc(c)
    rec = lca(c, letter)
    _refused(rec.with_user(c.officer).action_approve, match="Import Approver")


def test_m44_a02_lca_must_cover_lc(c):
    letter = lc(c)
    rec = lca(c, letter, amount=1.0)
    _refused(rec.with_user(c.approver).action_approve, match="cover the LC")


def test_m44_a03_lca_state_by_write(c):
    rec = lca(c, lc(c))
    _refused(rec.with_user(c.officer).write, {"state": "approved"}, match="workflow")


def test_m44_a04_lca_state_via_p03(c, p03):
    rec = lca(c, lc(c))
    out = p03.write(model="fix.import.lca", record_id=rec.id, values={"state": "approved"})
    rec.invalidate_recordset()
    assert out.get("error") and rec.state == "applied", out


def test_m44_a05_lca_reapprove_refused(c):
    rec = lca(c, lc(c))
    rec.with_user(c.approver).action_reject("Bank declined")
    _refused(rec.with_user(c.approver2).action_approve, match="applied")


def test_m44_a06_lca_amount_pinned(c):
    letter = lc(c)
    rec = lca(c, letter)
    rec.with_user(c.approver).action_approve()
    _refused(
        rec.with_user(c.officer).write, {"amount": letter.amount * 100}, match="cannot be changed"
    )


# ================================================================ HS / tariff
def test_m44_h01_hs_code_format_and_tariff(c):
    _refused(
        lambda: (
            c.env["fix.import.hs"]
            .with_user(c.officer)
            .create(
                {
                    "product_id": c.env["product.product"].create({"name": "M44T unclassified"}).id,
                    "hs_code": "ABC",
                }
            )
        ),
        match="not a tariff heading",
    )
    hs = (
        c.env["fix.import.hs"]
        .with_user(c.officer)
        .create(
            {
                "product_id": c.env["product.product"].create({"name": "M44T unclassified"}).id,
                "hs_code": "9999.99.99",
                "ruling_ref": "R",
            }
        )
    )
    _refused(hs.with_user(c.approver).action_rule, match="no active tariff")


def test_m44_h01b_rates_not_typed_on_hs(c):
    """Rates live on the tariff master; on the HS line they are computed."""
    assert c.env["fix.import.hs"]._fields["cd_pct"].compute
    assert c.hs.cd_pct == 25 and c.hs.tariff_id == c.tariff


def test_m44_h02_rate_upper_bound(c):
    row = (
        c.env["fix.import.tariff"]
        .with_user(c.officer)
        .create({"hs_code": "8471.30.00", "sro_ref": "S", "date_from": c.today, "cd_pct": 10})
    )
    assert _attempt(c.env, lambda: row.with_user(c.officer).write({"cd_pct": 9999}))


def test_m44_h03_negative_rate_refused(c):
    row = (
        c.env["fix.import.tariff"]
        .with_user(c.officer)
        .create({"hs_code": "8471.30.00", "sro_ref": "S", "date_from": c.today})
    )
    assert _attempt(c.env, lambda: row.with_user(c.officer).write({"cd_pct": -1}))


def test_m44_h03b_tariff_activation_two_person_and_frozen(c):
    row = (
        c.env["fix.import.tariff"]
        .with_user(c.officer)
        .create({"hs_code": "8471.30.00", "sro_ref": "S", "date_from": c.today, "cd_pct": 10})
    )
    _refused(row.with_user(c.officer).action_activate, match="Import Approver")
    row.with_user(c.approver).action_activate()
    _refused(row.with_user(c.officer).write, {"cd_pct": 0}, match="frozen")
    # a new rate is a new row; activating it ends the open-ended predecessor
    nxt = (
        c.env["fix.import.tariff"]
        .with_user(c.officer)
        .create(
            {
                "hs_code": "8471.30.00",
                "sro_ref": "S2",
                "date_from": c.today + timedelta(days=10),
                "cd_pct": 5,
            }
        )
    )
    nxt.with_user(c.approver).action_activate()
    assert row.state == "retired" and row.date_to == c.today + timedelta(days=9)


def test_m44_h04_classifier_cannot_rule(c):
    hs = (
        c.env["fix.import.hs"]
        .with_user(c.officer)
        .create(
            {
                "product_id": c.env["product.product"].create({"name": "M44T unclassified"}).id,
                "hs_code": c.code,
                "ruling_ref": "R2",
            }
        )
    )
    _refused(hs.with_user(c.officer).action_rule, match="Import Approver")
    c.env.ref(APPROVER).sudo().write({"user_ids": [(4, c.officer.id)]})
    _refused(hs.with_user(c.officer).action_rule, match="Segregation")
    nr = (
        c.env["fix.import.hs"]
        .with_user(c.officer2)
        .create(
            {"product_id": c.env["product.product"].create({"name": "x"}).id, "hs_code": c.code}
        )
    )
    _refused(nr.with_user(c.approver).action_rule, match="ruling reference")
    hs.with_user(c.approver).action_rule()
    assert hs.state == "ruled" and hs.ruled_by_id == c.approver


def test_m44_h05_ruled_hs_not_reclassified_in_place(c):
    _refused(c.hs.with_user(c.officer2).write, {"hs_code": "8524.99.99"}, match="reclassified")
    c.hs.with_user(c.officer).action_reopen()
    assert c.hs.state == "draft"
    c.hs.with_user(c.officer).write({"hs_code": "8524.99.99"})
    assert c.hs.classified_by_id == c.officer


def test_m44_h06_boe_needs_ruled_hs(c):
    stage_shipped(c)
    c.hs.with_user(c.officer).action_reopen()
    bill = boe(c)
    _refused(bill.with_user(c.officer).action_assess, match="not ruled")


def test_m44_h07_assessed_rates_frozen(c):
    stage_shipped(c)
    bill = boe(c)
    bill.with_user(c.officer).action_assess()
    before = bill.cd_amount
    # a new tariff row and a reclassification do not reach the assessed lines
    c.hs.with_user(c.officer).action_reopen()
    _refused(bill.line_ids.with_user(c.officer).write, {"quantity": 1}, match="final")
    bill.invalidate_recordset()
    assert bill.cd_amount == pytest.approx(before) and bill.line_ids[0].cd_rate == 25


def test_m44_h08_hs_ruled_by_write(c):
    hs = (
        c.env["fix.import.hs"]
        .with_user(c.officer)
        .create(
            {
                "product_id": c.env["product.product"].create({"name": "M44T unclassified"}).id,
                "hs_code": c.code,
            }
        )
    )
    _refused(hs.with_user(c.officer).write, {"state": "ruled"}, match="workflow")


# ================================================================ duty cascade
def _spec_order(c, av_bdt=100000.0):
    """A BDT order whose single line's CIF is exactly av_bdt."""
    c.env["ir.config_parameter"].sudo().set_param("cd_import_order.landing_charge_pct", "0")
    return _order(
        c,
        name="M44T-SPEC-%s" % c.tag,
        currency_id=c.bdt.id,
        fx_rate=1.0,
        fob_value=av_bdt,
        freight_cost=0.0,
        insurance_cost=0.0,
        line_ids=[
            (0, 0, {"part_id": c.part.id, "hs_id": c.hs.id, "quantity": 1, "unit_price": av_bdt})
        ],
    )


def _spec_line(c):
    order = _spec_order(c)
    bill = (
        c.env["fix.import.boe"]
        .with_user(c.officer)
        .create(
            {
                "order_id": order.id,
                "boe_no": "BE-SPEC-%s" % c.tag,
                "line_ids": [(0, 0, {"order_line_id": order.line_ids.id, "quantity": 1})],
            }
        )
    )
    return bill.line_ids


def test_m44_d01_cd_rd_ait_on_av(c):
    line = _spec_line(c)
    assert line.assessable_value == pytest.approx(100000.0)
    assert (line.cd_amount, line.rd_amount, line.ait_amount) == (
        pytest.approx(25000.0),
        pytest.approx(3000.0),
        pytest.approx(5000.0),
    )


def test_m44_d02_sd_on_av_cd_rd(c):
    assert _spec_line(c).sd_amount == pytest.approx(25600.0)  # 20% x 128,000


def test_m44_d03_vat_on_av_cd_rd_sd(c):
    assert _spec_line(c).vat_amount == pytest.approx(23040.0)  # 15% x 153,600


def test_m44_d04_at_on_av_cd_sd(c):
    assert _spec_line(c).at_amount == pytest.approx(7530.0)  # 5% x 150,600


def test_m44_d05_av_derived_from_cif_fx_landing_charge(c):
    """AV = CIF x FX x (1 + landing charge), never typed."""
    stage_shipped(c)
    bill = boe(c)
    line = bill.line_ids.filtered(lambda ln: ln.order_line_id.part_id == c.part)
    # line value 6,000 + its 60% share of freight 500 + insurance 100 = 6,360 USD
    assert line.cif_value_bdt == pytest.approx(6360.0 * FX)
    assert line.assessable_value == pytest.approx(6360.0 * FX * 1.01)
    assert line.formula_version == "FR-ITC-033/v1"
    _refused(line.with_user(c.officer).write, {"assessable_value": 1.0}, match="workflow")
    _refused(
        lambda: (
            c.env["fix.import.boe"]
            .with_user(c.officer)
            .create(
                {
                    "order_id": c.order.id,
                    "boe_no": "BE-TYPED-%s" % c.tag,
                    "line_ids": [(0, 0, {"hs_id": c.hs.id, "assessable_value": 1.0})],
                }
            )
        ),
        match="workflow",
    )


def test_m44_d06_paid_boe_final(c):
    stage_shipped(c)
    bill = assess_and_pay(c, boe(c))
    _refused(bill.line_ids.with_user(c.officer).write, {"quantity": 1}, match="final")
    _refused(
        bill.with_user(c.finance).write, {"customs_assessed_total": 1.0}, match="cannot be changed"
    )
    assert bill.state == "paid"


def test_m44_d06b_correction_by_reversal(c):
    stage_shipped(c)
    bill = assess_and_pay(c, boe(c))
    _refused(bill.with_user(c.officer).action_reverse, "typo", match="role")
    bill.with_user(c.finance).action_reverse("AV declared on the wrong invoice")
    assert bill.state == "reversed" and bill.reversal_move_id.state == "posted"
    assert _net(bill.reversal_move_id, c.acc["vat_input"]) == pytest.approx(-bill.vat_amount)
    # the corrected Bill of Entry may reuse the number once the first is reversed
    boe(c, boe_no=bill.boe_no)


def test_m44_d07_assessed_lines_not_deleted(c):
    stage_shipped(c)
    bill = boe(c)
    bill.with_user(c.officer).action_assess()
    _refused(bill.line_ids.with_user(c.officer2).unlink)
    _refused(bill.line_ids.with_user(c.clerk).unlink)


def test_m44_d08_boe_paid_by_write(c):
    bill = boe(c)
    _refused(bill.with_user(c.officer).write, {"state": "paid"}, match="workflow")


def test_m44_d09_boe_paid_via_p03(c, p03):
    bill = boe(c)
    out = p03.write(model="fix.import.boe", record_id=bill.id, values={"state": "paid"})
    bill.invalidate_recordset()
    assert out.get("error") and bill.state == "draft", out


def test_m44_d10_payment_posts_the_tax_split(c):
    stage_shipped(c)
    bill = boe(c)
    bill.with_user(c.officer).action_assess()
    bill.with_user(c.officer).write({"customs_assessed_total": bill.total_tax})
    _refused(bill.with_user(c.officer).action_pay, match="role")
    _refused(bill.with_user(c.finance).action_pay, match="payment reference")
    bill.with_user(c.finance).write({"payment_ref": "CH-1"})
    bill.with_user(c.finance).action_pay()
    move = bill.move_id
    assert move.state == "posted" and bill.paid_by_id == c.finance
    assert _net(move, c.acc["duty_clearing"]) == pytest.approx(
        bill.cd_amount + bill.rd_amount + bill.sd_amount
    )
    assert _net(move, c.acc["vat_input"]) == pytest.approx(bill.vat_amount)
    assert _net(move, c.acc["at_input"]) == pytest.approx(bill.at_amount)
    assert _net(move, c.acc["ait_advance"]) == pytest.approx(bill.ait_amount)
    assert _net(move, c.bank.default_account_id) == pytest.approx(-bill.total_tax)


def test_m44_d10b_unconfigured_account_refuses(c):
    stage_shipped(c)
    bill = boe(c)
    bill.with_user(c.officer).action_assess()
    bill.with_user(c.officer).write({"customs_assessed_total": bill.total_tax, "payment_ref": "CH"})
    c.env["ir.config_parameter"].sudo().set_param("cd_import_order.account_code.vat_input", "")
    _refused(bill.with_user(c.finance).action_pay, match="cd_import_order.account_code.vat_input")
    assert bill.state == "assessed"


def test_m44_d11_customs_variance_blocks_payment(c):
    stage_shipped(c)
    bill = boe(c)
    bill.with_user(c.officer).action_assess()
    bill.with_user(c.officer).write(
        {"customs_assessed_total": bill.total_tax + 500, "payment_ref": "CH"}
    )
    assert bill.duty_variance == pytest.approx(500)
    _refused(bill.with_user(c.finance).action_pay, match="variance")


def test_m44_d12_duplicate_boe_number(c):
    boe(c)
    assert _attempt(c.env, lambda: boe(c, user=c.officer2))


def test_m44_d13_document_checklist(c):
    bill = boe(c)
    _refused(bill.with_user(c.officer).action_assess, match="checklist")


def test_m44_d13b_quantity_cannot_exceed_order(c):
    stage_shipped(c)
    ln = c.order.line_ids[0]
    bill = boe(c, lines=[(0, 0, {"order_line_id": ln.id, "quantity": ln.quantity + 5})])
    _refused(bill.with_user(c.officer).action_assess, match="declared")


# ================================================================ arrival / clearance
def test_m44_r01_clear_in_transit_refused(c):
    arr = arrival(c)
    _refused(arr.with_user(c.officer).action_clear, match="arrived")


def test_m44_r02_clear_needs_paid_boe_and_release(c):
    stage_shipped(c)
    arr = arrival(c)
    arr.with_user(c.officer).action_arrive()
    _refused(arr.with_user(c.officer).action_clear, match="release order")
    arr.with_user(c.officer).write({"release_ref": "RO-1"})
    _refused(arr.with_user(c.officer).action_clear, match="no Bill of Entry is paid")
    bill = boe(c)
    bill.with_user(c.officer).action_assess()
    _refused(arr.with_user(c.officer).action_clear, match="no Bill of Entry is paid")


def test_m44_r03_cleared_by_write(c):
    arr = arrival(c)
    _refused(arr.with_user(c.officer).write, {"state": "cleared"}, match="workflow")
    _refused(arr.with_user(c.officer).write, {"cleared_on": c.today}, match="workflow")


def test_m44_r04_cleared_via_p03(c, p03):
    arr = arrival(c)
    out = p03.write(model="fix.import.arrival", record_id=arr.id, values={"state": "cleared"})
    arr.invalidate_recordset()
    assert out.get("error") and arr.state == "in_transit", out


def test_m44_r05_demurrage_from_actual_arrival(c, monkeypatch):
    stage_shipped(c)
    arr = arrival(c, free_days=7)
    arr.with_user(c.officer).action_arrive()
    later = c.today + timedelta(days=30)
    monkeypatch.setattr(fields.Date, "context_today", staticmethod(lambda *a, **k: later))
    arr.invalidate_recordset()
    assert arr.demurrage_days == 23


def test_m44_r06_demurrage_not_typed(c):
    assert c.env["fix.import.arrival"]._fields["demurrage_days"].compute
    assert not c.env["fix.import.arrival"]._fields["demurrage_days"].store
    stage_shipped(c)
    arr = arrival(c)
    arr.with_user(c.officer).action_arrive()
    _refused(arr.with_user(c.officer).write, {"free_days": 60}, match="cannot be changed")


def test_m44_r07_clearance_advances_order_and_publishes(c):
    arr, _bill = stage_cleared(c)
    assert c.order.state == "cleared" and arr.cleared_by_id == c.officer
    evts = (
        c.env["fix.event.outbox"]
        .search([("aggregate", "=", "fix.import.arrival"), ("aggregate_id", "=", arr.id)])
        .mapped("event_type")
    )
    assert "import.arrived" in evts and "import.cleared" in evts


# ================================================================ shipping documents
def test_m44_s01_shipdoc_verified_only_by_action(c):
    stage_advance(c)
    doc = shipdoc(c, "bl")
    _refused(doc.with_user(c.officer).write, {"state": "verified"}, match="workflow")
    doc.with_user(c.officer).action_receive()
    _refused(doc.with_user(c.officer).action_verify, match="Segregation")
    doc.with_user(c.officer2).action_verify()
    assert doc.state == "verified" and doc.verified_by_id == c.officer2


def test_m44_s02_document_needs_reference(c):
    doc = (
        c.env["fix.import.shipdoc"]
        .with_user(c.officer)
        .create({"order_id": c.order.id, "doc_type": "bl"})
    )
    _refused(doc.with_user(c.officer).action_receive, match="reference")


# ================================================================ import order
def test_m44_o01_receive_only_when_cleared(c):
    _refused(c.order.with_user(c.officer).action_receive, match="cleared")
    _refused(c.order.with_user(c.clerk).action_receive, match="role")


def test_m44_o02_receive_posts_m15_receipt(c):
    stage_cleared(c)
    c.order.with_user(c.officer).action_receive()
    receipt = c.order.receipt_id
    assert receipt.state == "posted" and c.order.state == "received"
    lines = {ln.part_id: ln for ln in receipt.line_ids}
    assert lines[c.part].qty_accepted == 10 and lines[c.part2].qty_accepted == 20
    # provisional cost = goods at the commitment rate (no estimate posted)
    assert _bucket(c, c.part).qty == 10
    assert _bucket(c, c.part).unit_cost == pytest.approx(600.0 * FX)
    evt = c.env["fix.event.outbox"].search(
        [
            ("event_type", "=", "goods.received"),
            ("aggregate", "=", "fix.import.order"),
            ("aggregate_id", "=", c.order.id),
        ]
    )
    payload = json.loads(evt.payload)
    assert payload["receipt_id"] == receipt.id and payload["vendor_id"] == c.supplier.id


def test_m44_o03_receive_once(c):
    stage_received(c)
    _refused(c.order.with_user(c.officer).action_receive)
    n = c.env["fix.event.outbox"].search_count(
        [
            ("event_type", "=", "goods.received"),
            ("aggregate", "=", "fix.import.order"),
            ("aggregate_id", "=", c.order.id),
        ]
    )
    assert n == 1 and _bucket(c, c.part).qty == 10


def test_m44_o04_order_state_by_write(c):
    _refused(c.order.with_user(c.officer).write, {"state": "landed"}, match="workflow")


def test_m44_o05_order_state_via_p03(c, p03):
    out = p03.write(model="fix.import.order", record_id=c.order.id, values={"state": "landed"})
    c.order.invalidate_recordset()
    assert out.get("error") and c.order.state == "draft", out


def test_m44_o06_order_duty_from_paid_boe(c):
    stage_shipped(c)
    bill = assess_and_pay(c, boe(c))
    c.order.invalidate_recordset()
    inventoriable = bill.cd_amount + bill.rd_amount + bill.sd_amount
    assert c.order.customs_duty == pytest.approx(inventoriable / FX, abs=0.01)
    assert c.env["fix.import.order"]._fields["customs_duty"].compute


def test_m44_o07_fx_rate_pinned_after_commitment(c):
    stage_proforma(c)
    _refused(c.order.with_user(c.officer2).write, {"fx_rate": 0.0001}, match="pinned")
    _refused(c.order.line_ids[0].with_user(c.officer).write, {"unit_price": 1.0}, match="pinned")


def test_m44_o08_order_hidden_from_other_ou(c):
    assert not c.env["fix.import.order"].with_user(c.outsider).search([("id", "=", c.order.id)])


def test_m44_o09_child_records_cross_ou(c):
    letter = lc(c)
    bill = boe(c)
    assert _attempt(c.env, lambda: letter.with_user(c.outsider).write({"amount": 1}))
    assert _attempt(c.env, lambda: bill.line_ids.with_user(c.outsider).write({"quantity": 1}))
    assert not c.env["fix.import.lc"].with_user(c.outsider).search_count([("id", "=", letter.id)])
    assert letter.operating_unit_id == c.ou and bill.line_ids[0].operating_unit_id == c.ou


# ================================================================ landed cost
def test_m44_c01_duty_from_paid_boe_not_typed(c):
    _arr, bill = stage_received(c)
    sheet = landed(c)
    assert sheet.duty == pytest.approx(bill.cd_amount + bill.rd_amount + bill.sd_amount)
    _refused(sheet.with_user(c.officer).write, {"duty": 1.0}, match="")


def test_m44_c02_recoverable_taxes_not_capitalised(c):
    _arr, bill = stage_received(c)
    sheet = landed(c)
    assert sheet.total_landed == pytest.approx(
        45000 + 8000 + 25000 + bill.cd_amount + bill.rd_amount + bill.sd_amount
    )
    assert sheet.vat_amount == pytest.approx(bill.vat_amount)
    assert sheet.total_landed < 78000 + bill.total_tax


def test_m44_c03_finalise_revalues_stock_and_posts(c):
    """R2 proper path: the approver finalises; the stock on hand carries the
    landed cost and the GL takes the true-up."""
    _arr, bill = stage_received(c)
    sheet = landed(c)
    cost_before = _bucket(c, c.part).unit_cost
    sheet.with_user(c.approver).action_finalise()
    duty = bill.cd_amount + bill.rd_amount + bill.sd_amount
    total = 45000 + 8000 + 25000 + duty
    assert sheet.state == "finalised" and c.order.state == "landed"
    move = sheet.move_id
    assert move.state == "posted"
    assert _net(move, c.acc["inventory"]) == pytest.approx(total)
    assert _net(move, c.acc["duty_clearing"]) == pytest.approx(-duty)
    assert _net(move, c.acc["landed_accrual"]) == pytest.approx(-78000)
    assert not any(
        ln.account_id in (c.acc["vat_input"], c.acc["at_input"], c.acc["ait_advance"])
        for ln in move.line_ids
    )
    # allocation by value: the LCD line carries 60% of the landed cost
    share = sheet.line_ids.filtered(lambda ln: ln.part_id == c.part).amount
    assert share == pytest.approx(total * 0.6, abs=0.02)
    assert _bucket(c, c.part).unit_cost == pytest.approx(cost_before + share / 10, abs=0.01)
    assert sum(sheet.line_ids.mapped("amount")) == pytest.approx(total)
    evt = c.env["fix.event.outbox"].search(
        [("event_type", "=", "landed_cost.finalised"), ("aggregate_id", "=", sheet.id)]
    )
    assert evt


def test_m44_c03b_estimate_at_shipment_true_up_at_final(c):
    """Estimate at shipment -> provisional cost at receipt; final true-up;
    the part already consumed goes to the variance account."""
    stage_shipped(c)
    est = landed(
        c,
        sheet_type="estimate",
        freight=40000.0,
        insurance=8000.0,
        clearing_charges=20000.0,
        duty_estimate=300000.0,
    )
    est.with_user(c.officer).action_post_estimate()
    assert est.state == "estimated"
    arr = arrival(c)
    arr.with_user(c.officer).action_arrive()
    bill = assess_and_pay(c, boe(c))
    arr.with_user(c.officer).write({"release_ref": "RO"})
    arr.with_user(c.officer).action_clear()
    c.order.with_user(c.officer).action_receive()
    E = est.total_landed
    assert _net(est.move_id, c.acc["inventory"]) == pytest.approx(E)
    assert _net(est.move_id, c.acc["landed_accrual"]) == pytest.approx(-E)
    est_lcd = est.line_ids.filtered(lambda ln: ln.part_id == c.part).amount
    assert _bucket(c, c.part).unit_cost == pytest.approx((6000 * FX + est_lcd) / 10, abs=0.01)
    # half the LCD panels are consumed before the final cost arrives
    c.env["fix.stock.onhand"]._apply(c.part, c.loc, "owned", -5)
    sheet = landed(c)
    sheet.with_user(c.approver).action_finalise()
    A = sheet.total_landed
    move = sheet.move_id
    assert sheet.estimate_id == est
    assert round(sheet.revalued_amount + sheet.variance_amount, 2) == pytest.approx(A - E, abs=0.02)
    lcd_diff = sheet.line_ids.filtered(lambda ln: ln.part_id == c.part).amount - est_lcd
    assert sheet.variance_amount == pytest.approx(lcd_diff * 0.5, abs=0.02)
    assert _net(move, c.acc["variance"]) == pytest.approx(sheet.variance_amount)
    assert _net(move, c.acc["inventory"]) == pytest.approx(sheet.revalued_amount)
    # the accrual is cleared of the estimate and carries the actual charges
    assert _net(move, c.acc["landed_accrual"]) == pytest.approx(E - 78000)
    assert sum(ln.debit for ln in move.line_ids) == pytest.approx(
        sum(ln.credit for ln in move.line_ids)
    )
    assert bill.state == "paid"


def test_m44_c03c_unconfigured_account_refuses_finalise(c):
    stage_received(c)
    sheet = landed(c)
    c.env["ir.config_parameter"].sudo().set_param("cd_import_order.account_code.duty_clearing", "")
    cost = _bucket(c, c.part).unit_cost
    _refused(
        sheet.with_user(c.approver).action_finalise,
        match="cd_import_order.account_code.duty_clearing",
    )
    assert sheet.state == "draft" and _bucket(c, c.part).unit_cost == pytest.approx(cost)


def test_m44_c04_allocation_lines(c):
    stage_received(c)
    sheet = landed(c, allocation_method="qty")
    sheet.with_user(c.approver).action_finalise()
    by_part = {ln.part_id: ln.amount for ln in sheet.line_ids}
    assert by_part[c.part2] == pytest.approx(2 * by_part[c.part], abs=0.02)  # 20 vs 10 units
    # import lines carry no weight: the option that was always refused is gone
    with pytest.raises(ValueError), c.env.cr.savepoint():
        landed(c, allocation_method="weight")


def test_m44_c05_one_final_sheet_per_order(c):
    stage_received(c)
    landed(c).with_user(c.approver).action_finalise()
    second = landed(c, user=c.officer2)
    _refused(second.with_user(c.approver).action_finalise, match="already has a final")


def test_m44_c06_finalised_sheet_immutable(c):
    stage_received(c)
    sheet = landed(c)
    sheet.with_user(c.approver).action_finalise()
    _refused(sheet.with_user(c.officer2).write, {"freight": 450000.0}, match="final")


def test_m44_c07_finalised_not_by_write_or_p03(c, p03):
    sheet = landed(c)
    _refused(sheet.with_user(c.officer).write, {"state": "finalised"}, match="workflow")
    out = p03.write(model="fix.import.landed", record_id=sheet.id, values={"state": "finalised"})
    sheet.invalidate_recordset()
    assert out.get("error") and sheet.state == "draft", out


def test_m44_c08_preparer_cannot_finalise(c):
    stage_received(c)
    sheet = landed(c)
    _refused(sheet.with_user(c.officer).action_finalise, match="Import Approver")
    c.env.ref(APPROVER).sudo().write({"user_ids": [(4, c.officer2.id)]})
    sheet.with_user(c.officer2).write({"clearing_charges": 26000.0})
    _refused(sheet.with_user(c.officer2).action_finalise, match="Segregation")


def test_m44_c08b_finalise_needs_received_stock_and_paid_boe(c):
    sheet = landed(c)
    _refused(sheet.with_user(c.approver).action_finalise, match="receive the consignment")


# ================================================================ IRC
def test_m44_i01_validity_computed_and_cron(c, monkeypatch):
    irc = (
        c.env["fix.import.irc"]
        .with_user(c.officer)
        .create(
            {
                "irc_no": "IRC-STALE-%s" % c.tag,
                "issued_on": c.today - timedelta(days=300),
                "valid_to": c.today,
            }
        )
    )
    assert irc.is_valid
    future = c.today + timedelta(days=2)
    monkeypatch.setattr(fields.Date, "context_today", staticmethod(lambda *a, **k: future))
    assert not c.env["fix.import.irc"].search_count([("id", "=", irc.id), ("is_valid", "=", True)])
    irc.invalidate_recordset()
    assert not irc.is_valid
    c.env["fix.import.irc"]._cron_expire()
    assert irc.state == "expired"


def test_m44_i02_suspended_irc_not_reinstated_by_write(c):
    irc = c.irc
    irc.with_user(c.approver).action_suspend("customs notice")
    _refused(irc.with_user(c.officer).write, {"state": "valid"}, match="workflow")
    _refused(irc.with_user(c.approver).action_reinstate, match="Segregation")
    irc.with_user(c.approver2).action_reinstate()
    assert irc.state == "valid"


def test_m44_i03_irc_linked_and_checked_at_lc(c):
    assert c.env["fix.import.irc"]._fields["company_id"].comodel_name == "res.company"
    stage_proforma(c)
    letter = lc(c)
    lca(c, letter).with_user(c.approver).action_approve()
    c.irc.sudo()._guarded().write({"state": "expired"})
    _refused(letter.with_user(c.officer).action_apply, match="Import Registration Certificate")


# ================================================================ wiring
def test_m44_w01_models_guarded_and_lc_routed(c):
    for model in MODELS:
        assert hasattr(c.env[model], "_fix_guarded_fields"), model
        assert c.env[model].browse()._fix_guarded_fields(), model
    for model in ("fix.import.lc", "fix.import.lc.amendment"):
        assert c.env[model]._approval_routed and "approval_state" in c.env[model]._fields


def test_m44_w02_forms_offer_no_guarded_field(c):
    import importlib.util
    from pathlib import Path

    import odoo.addons.cd_p03_portal as portal
    from odoo.addons.cd_p03_portal.controllers import a06
    from odoo.addons.cd_p03_portal.controllers.a06 import m44

    path = Path(portal.__file__).parent / "controllers" / "form_fields.py"
    spec = importlib.util.spec_from_file_location("m44_form_fields", path)
    ff = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ff)
    editable = ff.editable_by_model()
    for model in m44.SURFACES:
        guarded = (
            c.env[model].browse()._fix_guarded_fields()
            if hasattr(c.env[model], "_fix_guarded_fields")
            else set()
        )
        assert not guarded & editable.get(model, set()), (
            model,
            guarded & editable.get(model, set()),
        )
    for model in m44.SURFACES:
        assert a06.SURFACES[model].get("writable") is not None, model


def test_m44_w03_irc_cron_shipped(c):
    cron = c.env.ref("cd_import_order.ir_cron_import_irc_expire")
    assert cron.active and cron.model_id.model == "fix.import.irc" and "_cron_expire" in cron.code


def test_m44_w04_import_events_published(c):
    stage_lc_open(c)
    stage_received(c)
    landed(c).with_user(c.approver).action_finalise()
    types_ = set(
        c.env["fix.event.outbox"].search([("aggregate", "like", "fix.import")]).mapped("event_type")
    )
    assert {
        "import.lc_opened",
        "import.arrived",
        "import.duty_paid",
        "import.cleared",
        "goods.received",
        "landed_cost.finalised",
    } <= types_, types_


# ================================================================ proper path and KPIs
def test_m44_proper_path_officer_approver_finance(c):
    """An officer runs the import end to end; the approver approves; Finance
    pays; the stock and GL carry the landed cost; the LC is retired."""
    letter = stage_lc_open(c)
    assert letter.state == "opened" and letter.dofa_approved_by == c.approver
    stage_received(c)
    sheet = landed(c)
    sheet.with_user(c.approver).action_finalise()
    c.env["fix.import.lc.payment"].with_user(c.finance).create(
        {"lc_id": letter.id, "amount": 1175000.0, "reference": "TT-FULL"}
    )
    letter.with_user(c.officer).action_close()
    assert (letter.state, c.order.state, sheet.state) == ("closed", "landed", "finalised")


def test_m44_15_kpis_as_caller_and_fx_commitment(c):
    from odoo.addons.cd_p03_portal.controllers.a06 import m44

    other_co = c.env["res.company"].create({"name": "M44T Other Co %s" % c.tag})
    c.env["fix.import.order"].create(
        {
            "name": "M44T-OTHER",
            "company_id": other_co.id,
            "currency_id": c.usd.id,
            "fob_value": 99999,
            "fx_rate": 120,
        }
    )
    k = m44.kpis(c.env(user=c.officer.id))
    assert "fx_exposure" not in k
    # 10,000 USD FOB x 117.5 = 1,175,000 BDT open commitment; the other company is not counted
    assert k["fx_commitment"] == pytest.approx(1175000.0)
    pack = m44.fx_exposure(c.env(user=c.officer.id))
    assert [r["order"] for r in pack["rows"]] == [c.order.name]


# ================================================================ follow-up: facility, PO, GRNI
def test_m44_l05c_lc_within_facility_available_limit(c):
    """BRU-ITC-06: the LC fits the M50 LC facility after the other LCs on it."""
    stage_proforma(c)
    other_order = _order(
        c,
        name="M44T-IMP2-%s" % c.tag,
        fob_value=40000.0,
        line_ids=[
            (0, 0, {"part_id": c.part.id, "hs_id": c.hs.id, "quantity": 40, "unit_price": 1000.0})
        ],
    )
    other = c.env["fix.import.lc"].create(
        {
            "order_id": other_order.id,
            "lc_no": "LC-BIG-%s" % c.tag,
            "amount": 4000000.0,
            "currency_id": c.bdt.id,
            "expiry": c.today + timedelta(days=60),
            "facility_id": c.facility.id,
        }
    )
    other.sudo()._guarded().write({"state": "opened"})
    letter = lc(c)
    lca(c, letter).with_user(c.approver).action_approve()
    # 5,000,000 limit - 4,000,000 committed = 1,000,000 < 1,175,000
    _refused(letter.with_user(c.officer).action_apply, match="exceeds what facility")
    other.sudo()._guarded().write({"state": "closed"})
    letter.with_user(c.officer).action_apply()
    assert letter.state == "applied"


def test_m44_l05d_lc_needs_an_active_lc_facility(c):
    stage_proforma(c)
    letter = lc(c, facility_id=False)
    lca(c, letter).with_user(c.approver).action_approve()
    _refused(letter.with_user(c.officer).action_apply, match="LC facility")
    c.facility.sudo().write({"expiry_date": c.today + timedelta(days=30)})
    letter.with_user(c.officer).write({"facility_id": c.facility.id})
    _refused(letter.with_user(c.officer).action_apply, match="after facility")


def test_m44_l08c_amendment_within_facility(c):
    letter = stage_lc_open(c)
    am = (
        c.env["fix.import.lc.amendment"]
        .with_user(c.officer)
        .create({"lc_id": letter.id, "new_amount": 6000000.0, "reason": "Scope increase"})
    )
    approve_via_inbox(am, c.approver, requester=c.officer, justification="Scope increase")
    _refused(am.with_user(c.officer).action_apply_amendment, match="exceeds what facility")
    assert letter.amount == 1175000.0


def test_m44_1_po_link_and_grni_at_receipt(c):
    """M44-1: the import is linked to its M16 PO; the receipt carries the PO
    and posts the goods value once: Dr stock valuation / Cr GRNI."""
    po = c.env["fix.purchase.order"].create(
        {
            "vendor_id": c.supplier.id,
            "operating_unit_id": c.ou.id,
            "line_ids": [
                (0, 0, {"product_id": c.product.id, "qty_ordered": 10, "unit_price": 600.0 * FX}),
                (0, 0, {"product_id": c.product2.id, "qty_ordered": 20, "unit_price": 200.0 * FX}),
            ],
        }
    )
    po._guarded().write({"state": "sent"})
    stranger = c.env["fix.purchase.order"].create(
        {
            "vendor_id": c.env["res.partner"].create({"name": "M44T other vendor"}).id,
            "operating_unit_id": c.ou.id,
            "state": "sent",
        }
    )
    _refused(
        c.order.with_user(c.officer).write, {"purchase_order_id": stranger.id}, match="is with"
    )
    draft_po = c.env["fix.purchase.order"].create(
        {"vendor_id": c.supplier.id, "operating_unit_id": c.ou.id}
    )
    _refused(c.order.with_user(c.officer).write, {"purchase_order_id": draft_po.id}, match="issued")
    c.order.with_user(c.officer).write({"purchase_order_id": po.id})
    stage_proforma(c)
    _refused(c.order.with_user(c.officer).write, {"purchase_order_id": False}, match="pinned")
    stage_received(c)
    receipt = c.order.receipt_id
    assert receipt.purchase_order_id == po
    move = c.order.goods_move_id
    goods = 10000.0 * FX
    assert move.state == "posted"
    assert _net(move, c.acc["inventory"]) == pytest.approx(goods)
    assert _net(move, c.acc["grni"]) == pytest.approx(-goods)
    assert sum(move.line_ids.mapped("debit")) == pytest.approx(sum(move.line_ids.mapped("credit")))
    # once: a second receipt is refused, so no second goods entry
    _refused(c.order.with_user(c.officer).action_receive)
    n = c.env["account.move"].search_count([("ref", "like", "Import receipt %s" % c.order.name)])
    assert n == 1


def test_m44_1_grni_unconfigured_refuses_receipt(c):
    stage_cleared(c)
    c.env["ir.config_parameter"].sudo().set_param("cd_import_order.account_code.grni", "")
    _refused(c.order.with_user(c.officer).action_receive, match="cd_import_order.account_code.grni")
    assert c.order.state == "cleared" and not c.order.receipt_id and not _bucket(c, c.part)


# ================================================================ BRU-ITC-10 restricted goods
def _restriction(c, user=None, **kw):
    vals = {
        "name": "M44T test restriction %s" % c.tag,
        "hs_code_pattern": "8524",
        "restriction_type": "restricted",
        "permit_type": "TEST-NOC",
        "issuing_authority": "Test agency",
        "date_from": c.today - timedelta(days=5),
    }
    vals.update(kw)
    return c.env["fix.import.restriction"].with_user(user or c.officer).create(vals)


def _permit(c, restriction, user=None, **kw):
    vals = {
        "order_id": c.order.id,
        "restriction_id": restriction.id,
        "permit_no": "NOC-%s" % c.tag,
        "issuer": "Test agency",
        "valid_to": c.today + timedelta(days=60),
        "document": "UERGIHRlc3Q=",
        "document_name": "noc.pdf",
    }
    vals.update(kw)
    return c.env["fix.import.permit"].with_user(user or c.officer).create(vals)


def test_m44_bru10_restriction_activated_by_another_approver(c):
    r = _restriction(c)
    _refused(r.with_user(c.officer).action_activate, match="Import Approver")
    c.env.ref(APPROVER).sudo().write({"user_ids": [(4, c.officer.id)]})
    _refused(r.with_user(c.officer).action_activate, match="Segregation")
    r.with_user(c.approver).action_activate()
    _refused(r.with_user(c.officer2).write, {"restriction_type": "prohibited"}, match="frozen")
    _refused(r.with_user(c.officer).write, {"state": "draft"}, match="workflow")


def test_m44_bru10_prohibited_refused_outright(c):
    r = _restriction(c, restriction_type="prohibited", permit_type=False)
    r.with_user(c.approver).action_activate()
    pf = proforma(c)
    _refused(pf.with_user(c.approver).action_approve, match="prohibited")
    _refused(
        lambda: (
            c.env["fix.import.order.line"]
            .with_user(c.officer)
            .create(
                {
                    "order_id": c.order.id,
                    "part_id": c.part.id,
                    "hs_id": c.hs.id,
                    "quantity": 1,
                    "unit_price": 1,
                }
            )
        ),
        match="prohibited",
    )


def test_m44_bru10_restricted_needs_verified_valid_permit(c):
    r = _restriction(c)
    r.with_user(c.approver).action_activate()
    pf = proforma(c)
    _refused(pf.with_user(c.approver).action_approve, match="restricted")
    permit = _permit(c, r)
    _refused(pf.with_user(c.approver).action_approve, match="restricted")  # not verified
    _refused(permit.with_user(c.officer).action_verify, match="Import Approver")
    nodoc = _permit(c, r, permit_no="NOC-NODOC", document=False)
    _refused(nodoc.with_user(c.approver).action_verify, match="document")
    permit.with_user(c.approver).action_verify()
    _refused(
        permit.with_user(c.officer).write,
        {"valid_to": c.today + timedelta(days=900)},
        match="evidence",
    )
    pf.with_user(c.approver).action_approve()
    assert pf.state == "approved"


def test_m44_bru10_expired_permit_blocks_lc(c, monkeypatch):
    r = _restriction(c)
    r.with_user(c.approver).action_activate()
    _permit(c, r, valid_to=c.today + timedelta(days=3)).with_user(c.approver).action_verify()
    stage_proforma(c)
    letter = lc(c)
    lca(c, letter).with_user(c.approver).action_approve()
    later = c.today + timedelta(days=10)
    monkeypatch.setattr(fields.Date, "context_today", staticmethod(lambda *a, **k: later))
    _refused(letter.with_user(c.officer).action_apply, match="restricted")


def test_m44_bru10_product_restriction(c):
    r = _restriction(c, hs_code_pattern=False, product_id=c.product.id)
    r.with_user(c.approver).action_activate()
    _refused(proforma(c).with_user(c.approver).action_approve, match="restricted")


# ================================================================ BRU-ITC-12 C&F agent
def test_m44_bru12_agent_approval_two_person_and_m42_active(c):
    agent = _agent(c, suffix="2").with_user(c.officer)
    agent = (
        c.env["fix.import.cnf.agent"]
        .with_user(c.officer)
        .create(
            {
                "name": "M44T officer agent",
                "supplier_id": agent.supplier_id.id,
                "licence_no": "CNF-%s-OFF" % c.tag,
                "licence_expiry": c.today + timedelta(days=200),
            }
        )
    )
    _refused(agent.with_user(c.officer).action_approve, match="Import Approver")
    c.env.ref(APPROVER).sudo().write({"user_ids": [(4, c.officer.id)]})
    _refused(agent.with_user(c.officer).action_approve, match="Segregation")
    inactive = _agent(c, suffix="3", status="qualified")
    _refused(inactive.with_user(c.approver).action_approve, match="active in M42")
    _refused(agent.with_user(c.officer).write, {"state": "approved"}, match="workflow")
    agent.with_user(c.approver).action_approve()
    assert agent.is_usable
    _refused(
        agent.with_user(c.officer).write,
        {"licence_expiry": c.today + timedelta(days=900)},
        match="evidence",
    )


def test_m44_bru12_boe_and_clearance_need_usable_agent(c):
    stage_shipped(c)
    bill = boe(c, cnf_agent_id=False)
    _refused(bill.with_user(c.officer).action_assess, match="name the C&F agent")
    blocked = _agent(c, suffix="B")
    blocked.action_approve()
    blocked.with_user(c.approver).action_block("missed filings")
    bill.with_user(c.officer).write({"cnf_agent_id": blocked.id})
    _refused(bill.with_user(c.officer).action_assess, match="not approved")
    _refused(blocked.with_user(c.approver).action_unblock, match="Segregation")
    blocked.with_user(c.approver2).action_unblock()
    bill.with_user(c.officer).action_assess()
    assert bill.state == "assessed"
    arr = arrival(c, cnf_agent_id=False)
    arr.with_user(c.officer).action_arrive()
    bill.with_user(c.officer).write({"customs_assessed_total": bill.total_tax, "payment_ref": "CH"})
    bill.with_user(c.finance).action_pay()
    arr.with_user(c.officer).write({"release_ref": "RO-1"})
    _refused(arr.with_user(c.officer).action_clear, match="name the C&F agent")
    # M42 suspends the agent's supplier record: it can no longer be instructed
    c.agent.supplier_id.sudo()._guarded().write({"status": "suspended"})
    arr.with_user(c.officer).write({"cnf_agent_id": c.agent.id})
    _refused(arr.with_user(c.officer).action_clear, match="not active in M42")


def test_m44_bru12_licence_expiry_cron(c, monkeypatch):
    cron = c.env.ref("cd_import_order.ir_cron_import_cnf_expire")
    assert cron.active and cron.model_id.model == "fix.import.cnf.agent"
    later = c.today + timedelta(days=201)
    monkeypatch.setattr(fields.Date, "context_today", staticmethod(lambda *a, **k: later))
    c.agent.invalidate_recordset()
    assert not c.agent.is_usable
    c.env["fix.import.cnf.agent"]._cron_expire()
    assert c.agent.state == "expired"


# ================================================================ BRU-ITC-13 insurance
def test_m44_bru13_shipment_needs_cover_of_consignment_value(c):
    stage_advance(c)
    doc = shipdoc(c, "bl")
    c.cover.with_user(c.approver).action_cancel()
    _refused(doc.with_user(c.officer).action_receive, match="cargo cover")
    short = _cover(c, policy_no="MC-SHORT", sum_insured=5000.0, premium=100.0)
    short.with_user(c.approver).action_verify()
    _refused(doc.with_user(c.officer).action_receive, match="below 100%")
    c.env["ir.config_parameter"].sudo().set_param("cd_import_order.insurance_cover_pct", "40")
    doc.with_user(c.officer).action_receive()
    assert c.order.state == "shipped"


def test_m44_bru13_cover_verified_by_another_and_frozen(c):
    cover = _cover(c, user=c.officer, policy_no="MC-2")
    _refused(cover.with_user(c.officer).action_verify, match="Import Approver")
    _refused(cover.with_user(c.officer).write, {"state": "active"}, match="workflow")
    cover.with_user(c.approver).action_verify()
    _refused(cover.with_user(c.officer).write, {"sum_insured": 1.0}, match="evidence")


def test_m44_bru13_seller_insures_under_cif(c):
    order = _order(c, name="M44T-CIF-%s" % c.tag, incoterm="cif")
    c.order = order
    stage_advance(c)
    shipdoc(c, "bl").with_user(c.officer).action_receive()
    assert order.state == "shipped"


def test_m44_bru13_premium_feeds_cif(c):
    line = c.order.line_ids.filtered(lambda ln: ln.part_id == c.part)
    assert line.cif_amount == pytest.approx(6000 + 0.6 * (500 + 100))
    c.cover.with_user(c.approver).action_cancel()
    _cover(c, policy_no="MC-3", premium=400.0, sum_insured=11000.0).with_user(
        c.approver
    ).action_verify()
    line.invalidate_recordset()
    assert line.cif_amount == pytest.approx(6000 + 0.6 * (500 + 400))
