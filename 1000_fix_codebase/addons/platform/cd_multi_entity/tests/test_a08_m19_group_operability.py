# A08 finish, M19-13: transfer pricing is operable on screen, and the inter-company
# match is the counterparty's acceptance. Non-admin users with real finance roles,
# through the P03 endpoints. The `whitelist` fixture applies what the generation of
# writable.py produces from the forms as they stand.
import json
import re
import shutil
import subprocess
import types
from datetime import date
from pathlib import Path

import pytest
from odoo.exceptions import UserError

ACC_USER = "account.group_account_user"
ACC_MGR = "account.group_account_manager"
_SEQ = iter(range(1, 100000))
PORTAL = Path(__file__).resolve().parents[2] / "cd_p03_portal"
IMPORT = re.compile(r'from\s+"(\./a\d\d/\w+)"')


class Ctx:
    pass


def _user(env, login, groups=(), companies=None):
    companies = companies or env.company
    ou = env["operating.unit"].search([], limit=1)
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": login,
                "login": login,
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id] + [env.ref(g).id for g in groups])
                ],
                "company_ids": [(6, 0, companies.ids)],
                "company_id": companies[0].id,
                "assigned_operating_unit_ids": [(6, 0, ou.ids)],
                "default_operating_unit_id": ou.id,
            }
        )
    )


@pytest.fixture
def ic(odoo_env):
    env = odoo_env
    bdt = env.ref("base.BDT")
    n = next(_SEQ)
    co1 = env["res.company"].create({"name": "Op IC Parent %d" % n, "currency_id": bdt.id})
    co2 = env["res.company"].create({"name": "Op IC Sub %d" % n, "currency_id": bdt.id})
    e1 = env["fix.entity"].create(
        {"code": "OPP%d" % n, "legal_name": "Op Parent", "company_id": co1.id}
    )
    e2 = env["fix.entity"].create(
        {"code": "OPS%d" % n, "legal_name": "Op Sub", "company_id": co2.id}
    )

    def acc(co, t, rec=False):
        k = next(_SEQ)
        return env["account.account"].create(
            {
                "code": "7%05d" % k,
                "name": "Op %s %d" % (t, k),
                "account_type": t,
                "reconcile": rec,
                "company_ids": [(6, 0, co.ids)],
            }
        )

    def jr(co):
        k = next(_SEQ)
        return env["account.journal"].create(
            {"name": "Op J%d" % k, "code": "O%04d" % k, "type": "general", "company_id": co.id}
        )

    y = Ctx()
    y.env, y.bdt = env, bdt
    y.co1, y.co2, y.e1, y.e2 = co1, co2, e1, e2
    both = co1 | co2
    y.ctx = {"allowed_company_ids": both.ids}
    y.poster = _user(env, "opic_poster", [ACC_USER], both)
    y.group_acct = _user(env, "opic_group", [ACC_USER], both)
    y.source_only = _user(env, "opic_source", [ACC_USER], co1)
    y.target_only = _user(env, "opic_target", [ACC_USER], co2)
    y.target_plain = _user(env, "opic_target_plain", [], co2)
    y.mgr = _user(env, "opic_mgr", [ACC_USER, ACC_MGR], both)
    y.mgr2 = _user(env, "opic_mgr2", [ACC_USER, ACC_MGR], both)
    y.rule = env["fix.intercompany.rule"].create(
        {
            "name": "IT shared service",
            "code": "OPIC%d" % n,
            "company_id": co1.id,
            "source_entity_id": e1.id,
            "target_entity_id": e2.id,
            "transaction_type": "shared_service",
            "source_journal_id": jr(co1).id,
            "source_receivable_account_id": acc(co1, "asset_receivable", True).id,
            "source_income_account_id": acc(co1, "income").id,
            "target_journal_id": jr(co2).id,
            "target_expense_account_id": acc(co2, "expense").id,
            "target_payable_account_id": acc(co2, "liability_payable", True).id,
        }
    )
    return y


def _txn(y, user, amount=100000.0):
    return (
        y.env["fix.intercompany.transaction"]
        .with_user(user)
        .with_context(**y.ctx)
        .with_company(y.co1)
        .create(
            {
                "name": "IT recharge",
                "company_id": y.co1.id,
                "source_entity_id": y.e1.id,
                "target_entity_id": y.e2.id,
                "rule_id": y.rule.id,
                "amount": amount,
                "currency_id": y.bdt.id,
                "transaction_date": date(2026, 9, 20),
            }
        )
    )


def _as(rec, user, y):
    return rec.with_user(user).with_context(**y.ctx)


@pytest.fixture
def whitelist():
    from odoo.addons.cd_p03_portal.controllers import a08, form_fields

    editable = form_fields.editable_by_model()
    saved = {model: conf.get("writable") for model, conf in a08.SURFACES.items()}
    for model, conf in a08.SURFACES.items():
        conf["writable"] = frozenset(editable.get(model, ()))
    try:
        yield
    finally:
        for model, conf in a08.SURFACES.items():
            conf["writable"] = saved[model]


@pytest.fixture
def p03(ic, whitelist):
    import odoo.addons.cd_p03_portal.controllers.p03_generic_api as g
    import odoo.addons.cd_p03_portal.controllers.p03_service_order_api as s

    def orig(name):
        f = getattr(g.P03GenericApiController, name)
        return getattr(f, "original_endpoint", f)

    ctl = g.P03GenericApiController()
    old = (getattr(g, "request", None), getattr(s, "request", None))

    def as_user(user):
        req = types.SimpleNamespace(
            env=ic.env(user=user.id, context=dict(ic.env.context, **ic.ctx))
        )
        g.request = req
        s.request = req

    try:
        yield types.SimpleNamespace(
            as_user=as_user,
            write=lambda **kw: orig("model_write")(ctl, **kw),
            action=lambda **kw: orig("model_action")(ctl, **kw),
            form=lambda **kw: orig("model_form")(ctl, **kw),
            records=lambda **kw: orig("model_records")(ctl, **kw),
        )
    finally:
        g.request, s.request = old


@pytest.fixture(scope="module")
def screens(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    src = PORTAL / "static" / "src"
    tmp = tmp_path_factory.mktemp("p03_m19_ic")
    for area in sorted(d for d in src.iterdir() if re.fullmatch(r"a\d\d", d.name)):
        (tmp / area.name).mkdir()
        for js in area.glob("*.js"):
            (tmp / area.name / (js.stem + ".mjs")).write_text(
                js.read_text(encoding="utf-8"), "utf-8"
            )
    meta = (src / "p03_modules_meta.js").read_text(encoding="utf-8")
    (tmp / "meta.mjs").write_text(IMPORT.sub(r'from "\1.mjs"', meta), "utf-8")
    probe = tmp / "probe.mjs"
    probe.write_text(
        "import * as M from './meta.mjs';\n"
        "console.log(JSON.stringify({screens: Object.fromEntries(Object.entries(M.P03_DATA_SCREENS)"
        ".filter(([k]) => k.startsWith('M19'))), chips: M.P03_FORM_CHIPS,"
        " nav: M.P03_MODULES.M19.groups.flatMap((g) => g.screens.map((s) => s.id))}));\n",
        "utf-8",
    )
    out = subprocess.run(  # noqa: S603 - fixed argv: the node binary and our own probe file
        [node, str(probe)], capture_output=True, encoding="utf-8", check=True, timeout=60
    )
    return json.loads(out.stdout)


def _fields(screens, sid):
    return [f for s in screens["screens"][sid]["sections"] for f in s["fields"]]


# ===================================================== 3. transfer pricing on screen
def test_item3_rate_is_proposed_approved_and_prices_the_charge(ic, p03, screens):
    assert "M19-tp-rates" in screens["nav"]
    assert screens["chips"]["M19:__by_screen__"]["M19-tp-rates"] == "M19-form-tp-rate"
    assert {"action_activate", "action_retire"} == {
        a["m"] for a in screens["screens"]["M19-tp-rates"]["actions"]
    }
    p03.as_user(ic.group_acct)
    form = p03.form(model="fix.transfer.price.rate", fields=_fields(screens, "M19-form-tp-rate"))
    inputs = {f["name"] for f in form["fields"] if not f["readonly"]}
    assert inputs == {"rule_id", "markup_percent", "date_from", "date_to", "study_ref"}

    # the rule's markup is on its form now, for the administrator who owns the rule
    rule_form = p03.form(model="fix.intercompany.rule", fields=_fields(screens, "M19-form-icrule"))
    assert "markup_percent" in {f["name"] for f in rule_form["fields"]}
    p03.as_user(ic.mgr)
    res = p03.write(
        model="fix.intercompany.rule", record_id=ic.rule.id, values={"markup_percent": 5.0}
    )
    assert "id" in res, res
    assert ic.rule.markup_percent == 5.0

    # no approved rate: the priced charge is refused
    txn = _txn(ic, ic.poster)
    with pytest.raises(UserError, match="no transfer-pricing rate is approved"):
        _as(txn, ic.poster, ic).action_generate_mirror()

    p03.as_user(ic.group_acct)
    made = p03.write(
        model="fix.transfer.price.rate",
        values={
            "rule_id": ic.rule.id,
            "markup_percent": 5.0,
            "date_from": "2026-07-01",
            "study_ref": "TP study FY27",
        },
    )
    assert "id" in made, made
    rate = ic.env["fix.transfer.price.rate"].browse(made["id"])
    assert "OPIC" in rate.display_name and rate.state == "draft"
    # the proposer does not approve; an accountant does not approve
    res = p03.action(model="fix.transfer.price.rate", ids=[rate.id], method="action_activate")
    assert not res["success"] and rate.state == "draft"
    p03.as_user(ic.mgr)
    res = p03.action(model="fix.transfer.price.rate", ids=[rate.id], method="action_activate")
    assert res["success"], res
    assert rate.state == "active" and rate.approved_by_id == ic.mgr
    # frozen once approved
    res = p03.write(
        model="fix.transfer.price.rate", record_id=rate.id, values={"markup_percent": 9.0}
    )
    assert "error" in res and rate.markup_percent == 5.0

    _as(txn, ic.poster, ic).action_generate_mirror()
    assert txn.amount == 105000.0 and txn.cost_amount == 100000.0 and txn.tp_rate_id == rate

    res = p03.action(model="fix.transfer.price.rate", ids=[rate.id], method="action_retire")
    assert res["success"] and rate.state == "retired"


def test_item3_rule_form_offers_every_posting_account_the_mirror_needs(ic, p03, screens):
    """A rule the form cannot finish is a dead end: 'Rule X cannot post yet'."""
    offered = {f["name"] for f in _fields(screens, "M19-form-icrule")}
    missing = ic.rule.sudo().copy({"code": "OPICX%d" % next(_SEQ), "source_journal_id": False})
    needed = {
        "source_journal_id",
        "source_receivable_account_id",
        "source_income_account_id",
        "target_journal_id",
        "target_expense_account_id",
        "target_payable_account_id",
    }
    assert needed <= offered
    assert any("Supplying Side Journal" in e for e in missing._posting_config_errors())
    tabs = {t["id"] for t in screens["screens"]["M19-form-icrule"]["tabs"]}
    assert {s["tab"] for s in screens["screens"]["M19-form-icrule"]["sections"]} <= tabs


# ============================================== 4. acceptance by the counterparty
def test_item4_match_needs_a_user_of_the_target_entity(ic, p03):
    txn = _txn(ic, ic.poster)
    _as(txn, ic.poster, ic).action_generate_mirror()
    # a colleague who holds only the originating company: not the counterparty
    with pytest.raises(UserError, match="counterparty entity"):
        txn.with_user(ic.source_only).action_match()
    assert txn.state == "pending_matching" and not txn.matched_by_id
    # through the surface the same refusal reaches the screen
    p03.as_user(ic.source_only)
    res = p03.action(model="fix.intercompany.transaction", ids=[txn.id], method="action_match")
    assert not res["success"] and "counterparty entity" in res["error"]
    # the poster holds both companies but is excluded: I02 still holds
    with pytest.raises(UserError, match="Segregation of duties"):
        _as(txn, ic.poster, ic).action_match()
    # a target user with no finance role
    with pytest.raises(UserError, match="Accountant role"):
        txn.with_user(ic.target_plain).action_match()
    assert txn.state == "pending_matching"


def test_item4_an_accountant_of_the_target_entity_alone_can_accept(ic, p03):
    """He cannot read the originating company's record by rule; the acceptance works."""
    txn = _txn(ic, ic.poster)
    _as(txn, ic.poster, ic).action_generate_mirror()
    p03.as_user(ic.target_only)
    res = p03.action(model="fix.intercompany.transaction", ids=[txn.id], method="action_match")
    assert res["success"], res
    assert txn.state == "matched" and txn.matched_by_id == ic.target_only


def test_item4_group_accountant_of_both_entities_can_accept(ic):
    txn = _txn(ic, ic.poster)
    _as(txn, ic.poster, ic).action_generate_mirror()
    _as(txn, ic.group_acct, ic).action_match()
    assert txn.state == "matched" and txn.matched_by_id == ic.group_acct
