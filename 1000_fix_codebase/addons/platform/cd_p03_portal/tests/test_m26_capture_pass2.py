# M26 AI/ML Services, capture audit second pass (2026-11-19).
#
# The user again saw M26 pages without a relevant capture. The 14 Nov pass
# (test_m26_capture_buttons.py / test_m26_capture_live.py) gave every page a
# "+ New"; read against the spec's lifecycle (§8.1), rules (§9) and owned
# entities (§10.1), these were still missing on HEAD a6ca660a:
#
#   page 2  Training Pipelines: no training run (FR-AIM-002/003, T-10). The
#           page's only capture was a model version, which named no run.
#   page 3  Evaluation Gates: no data-sufficiency gate (FR-AIM-006 P0,
#           BRU-AIM-12 H) - promotion never asked whether the data sufficed;
#           no bias test (FR-AIM-042 P0) - the version's bias status was a
#           choice the person who registered it typed on the version.
#   page 4  Deployment & Monitoring: no production performance (FR-AIM-008 P0,
#           BRU-AIM-19) - nothing recorded a floor, so nothing was ever demoted.
#   page 5  Explainability: an override without a reason saved (BRU-AIM-05 H).
#   page 7  Bengali NLP & OCR: no way to record the confirmed fault.
#   and     Retire asked nobody whether the consumers' fallback stood (FR-AIM-010).
#
# The page rule is JavaScript (p03_workspace.js fregCreate / fregPanels), so it
# is EXECUTED in node over the real registry; the saves run through the
# workspace endpoints with the values the forms post, as non-admin M26 role
# holders (the superuser is trusted by the guards and would hide a gap).
from __future__ import annotations

import datetime
import importlib.util
import itertools
import json
import re
import shutil
import subprocess
import types
from pathlib import Path

import pytest
from odoo.exceptions import UserError, ValidationError

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "static" / "src"
_SEQ = itertools.count(1)

SCIENTIST = "cd_ml_services.group_ml_data_scientist"
REVIEWER = "cd_ml_services.group_ml_reviewer"
OWNER = "cd_ml_services.group_ml_model_owner"

_spec = importlib.util.spec_from_file_location(
    "_estate_pages", HERE / "test_estate_module_pages.py"
)
_estate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_estate)

PROBE = """
import * as M from './meta.mjs';
const { P03_MODULES, P03_FORM_CHIPS, P03_DATA_SCREENS } = M;
function %(create)s
function %(panels)s
const mod = P03_MODULES.M26;
const subs = mod.freg.sub.map((s) => ({ no: s[0], map: s[3],
  create: fregCreate('M26', s[3]), forms: fregPanels('M26', mod, s[3]).forms }));
console.log(JSON.stringify({ subs,
  chips: Object.fromEntries(Object.entries(P03_FORM_CHIPS).filter(([k]) => k.startsWith('M26:'))),
  nav: mod.groups.flatMap((g) => g.screens.map((s) => s.id)),
  screens: Object.fromEntries(Object.entries(P03_DATA_SCREENS).filter(([k]) => k.startsWith('M26-'))) }));
"""


@pytest.fixture(scope="module")
def m26(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m26_pass2")
    for area in sorted(d for d in SRC.iterdir() if re.fullmatch(r"a\d\d", d.name)):
        (tmp / area.name).mkdir()
        for js in area.glob("*.js"):
            (tmp / area.name / (js.stem + ".mjs")).write_text(
                js.read_text(encoding="utf-8"), "utf-8"
            )
    meta = (SRC / "p03_modules_meta.js").read_text(encoding="utf-8")
    (tmp / "meta.mjs").write_text(_estate.IMPORT.sub(r'from "\1.mjs"', meta), "utf-8")
    engine = (SRC / "p03_workspace.js").read_text(encoding="utf-8").replace("\r\n", "\n")
    probe = tmp / "probe.mjs"
    probe.write_text(
        PROBE
        % {
            "create": _estate._method(engine, "fregCreate(mid, map)"),
            "panels": _estate._method(engine, "fregPanels(mid, mod, map)"),
        },
        "utf-8",
    )
    out = subprocess.run(  # noqa: S603 - fixed argv: the node binary and our own probe file
        [node, str(probe)], capture_output=True, encoding="utf-8", check=True, timeout=120
    )
    return json.loads(out.stdout)


# page -> (chip, list screen, form screen, model)
NEW_CAPTURES = {
    "2": ("Training Run", "M26-training", "M26-form-training", "fix.ml.training.run"),
    "3a": (
        "Data-Sufficiency Gate",
        "M26-sufficiency",
        "M26-form-sufficiency",
        "fix.ml.data.sufficiency",
    ),
    "3b": ("Bias Test", "M26-bias-tests", "M26-form-bias", "fix.ml.bias.test"),
    "4": (
        "Performance Observation",
        "M26-performance",
        "M26-form-performance",
        "fix.ml.performance.observation",
    ),
}


def _sub(m26, no):
    return next(s for s in m26["subs"] if s["no"] == no[0])


@pytest.mark.parametrize("key", sorted(NEW_CAPTURES))
def test_the_page_offers_its_new_capture(m26, key):
    """The page lists the record, names its form, and the chip, the list's own
    + New and the model all open the same form."""
    chip, list_id, form_id, model = NEW_CAPTURES[key]
    sub = _sub(m26, key)
    assert chip in sub["forms"], (key, sub["forms"])
    assert list_id in sub["map"]["screens"]
    assert m26["chips"]["M26:" + chip] == form_id
    assert m26["chips"]["M26:__by_screen__"][list_id] == form_id
    assert m26["chips"]["M26:__by_model__"][model] == form_id
    form, lst = m26["screens"][form_id], m26["screens"][list_id]
    assert form["kind"] == "model_form" and form["model"] == model
    assert lst["kind"] == "model_list" and lst["model"] == model and lst.get("create") is True
    assert list_id in m26["nav"]


def test_training_pipelines_opens_on_a_training_run(m26):
    sub = _sub(m26, "2")
    assert sub["create"]["screen"] == "M26-form-training"
    assert sub["map"]["model"] == "fix.ml.training.run"
    assert "Model Version" in sub["forms"]


def test_the_nlp_page_records_the_confirmed_fault(m26):
    assert "Record Human Decision" in _sub(m26, "7")["forms"]


def test_every_retire_button_asks_for_the_consumers_confirmation(m26):
    for screen in ("M26-registry", "M26-deploy"):
        retire = next(a for a in m26["screens"][screen]["actions"] if a["m"] == "action_retire")
        assert [a["kwarg"] for a in retire["asks"]] == ["confirmation"], screen


def test_the_version_form_no_longer_types_the_bias_status(m26):
    fields = {
        f["name"]: f for s in m26["screens"]["M26-form-version"]["sections"] for f in s["fields"]
    }
    assert fields["bias_status"].get("readonly") is True
    assert "training_run_id" in fields


# --------------------------------------------------------------- forms vs models
@pytest.fixture
def env(odoo_env):
    if "fix.ml.performance.observation" not in odoo_env:
        pytest.skip("cd_ml_services is not at the capture-pass-2 version on this database")
    return odoo_env


FORMS = ("M26-form-training", "M26-form-sufficiency", "M26-form-bias", "M26-form-performance")


@pytest.mark.parametrize("form_id", FORMS)
def test_every_form_field_exists_and_saves(m26, env, form_id):
    """Every field the form shows exists on the model; every editable one is in
    the surface whitelist (or the save drops it silently); every required
    model field without a default is on the form (else + New never saves)."""
    from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api

    form = m26["screens"][form_id]
    model = env[form["model"]]
    shown = {f["name"]: f for s in form["sections"] for f in s["fields"]}
    assert set(shown) <= set(model._fields), set(shown) - set(model._fields)
    writable = api.SURFACES[form["model"]]["writable"]
    editable = {n for n, f in shown.items() if not f.get("readonly")}
    assert editable <= writable, editable - writable
    for name, field in model._fields.items():
        if field.required and field.default is None and not field.compute and not field.related:
            if name in ("company_id",):
                continue
            assert name in editable, "%s: required %s is not on the form" % (form_id, name)


# --------------------------------------------------------------- live captures
@pytest.fixture
def p03(env):
    import odoo.addons.cd_p03_portal.controllers.p03_generic_api as g
    import odoo.addons.cd_p03_portal.controllers.p03_service_order_api as s

    ctl = g.P03GenericApiController()
    old = (getattr(g, "request", None), getattr(s, "request", None))

    def raw(fn):
        return getattr(fn, "original_endpoint", fn)

    def as_user(user):
        req = types.SimpleNamespace(env=env(user=user.id))

        def call(route, **kw):
            g.request = s.request = req
            return raw(getattr(g.P03GenericApiController, route))(ctl, **kw)

        return call

    yield as_user
    g.request, s.request = old


def _user(env, *xmlids):
    n = next(_SEQ)
    groups = [env.ref("base.group_user").id] + [env.ref(x).id for x in xmlids]
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "M26 Pass2 %d" % n,
                "login": "m26.pass2.%d@a11.test" % n,
                "group_ids": [(6, 0, groups)],
            }
        )
    )


def _model(env, **extra):
    n = next(_SEQ)
    vals = {
        "name": "Pass-2 probe %d" % n,
        "code": "P2PROBE%d" % n,
        "kind": "tradein_valuation",
        "implementation": "rule_based",
        "status": "production",
        # BRU-AIM-11 (A2-F10): a NEW promotion needs a named consumer, an
        # accuracy target and a defined fallback. A trade-in model is
        # financial (not advisory), so the target is required too.
        "consumer_modules": "M14 Trade-In (probe)",
        "accuracy_target": "Within 10% of assessed value (probe)",
        "fallback_definition": "Depreciation table (probe)",
    }
    vals.update(extra)
    return env["fix.ml.model"].create(vals)


def _deployed(env, model, version, when):
    """A served version in the seeded-baseline shape (superuser load)."""
    return env["fix.ml.model.version"].create(
        {
            "model_id": model.id,
            "version": version,
            "state": "deployed",
            "deployed_at": when,
            "deployment_mode": "online",
        }
    )


def _ok(res):
    assert "id" in res, res
    return res["id"]


def _training_values(model, **extra):
    vals = {
        "model_id": {"id": model.id, "label": model.display_name},
        "code_version": "a1b2c3d",
        "data_snapshot_ref": "m62://snapshots/2026-11-01",
        "feature_versions": "brand@2, age_months@1, condition_grade@3",
        "hyperparameters": '{"depth": 4}',
        "environment_ref": "uv.lock@a1b2c3d",
        "m06_data_excluded": True,
        "started_at": "2026-11-18 08:00:00",
        "ended_at": "2026-11-18 09:30:00",
        "outcome": "succeeded",
        "metrics_json": '{"within_10pct": 0.77}',
        # stamps the form shows read-only, posted back: dropped
        "trained_by": False,
    }
    vals.update(extra)
    return vals


# ---- page 2: training run
def test_a_scientist_records_a_reproducible_training_run(env, p03):
    model = _model(env)
    sci_user = _user(env, SCIENTIST)
    run = env["fix.ml.training.run"].browse(
        _ok(
            p03(sci_user)(
                "model_write", model="fix.ml.training.run", values=_training_values(model)
            )
        )
    )
    assert run.trained_by == sci_user and run.outcome == "succeeded"
    # the version registered from it names it (lineage, FR-AIM-004)
    version = env["fix.ml.model.version"].browse(
        _ok(
            p03(sci_user)(
                "model_write",
                model="fix.ml.model.version",
                values={
                    "model_id": {"id": model.id, "label": model.display_name},
                    "version": "1.0.0",
                    "training_run_id": {"id": run.id, "label": run.display_name},
                    "deployment_mode": "none",
                },
            )
        )
    )
    assert version.training_run_id == run and run.version_ids == version
    # evidence: never edited
    with pytest.raises(UserError, match="(?i)evidence"):
        run.with_user(sci_user).write({"code_version": "other"})


def test_a_training_run_must_confirm_no_m06_data(env, p03):
    res = p03(_user(env, SCIENTIST))(
        "model_write",
        model="fix.ml.training.run",
        values=_training_values(_model(env), m06_data_excluded=False),
    )
    assert "error" in res and "BRU-AIM-03" in res["error"], res


@pytest.mark.parametrize(
    "extra, why",
    [
        ({"outcome": "failed", "metrics_json": ""}, "(?i)why the run failed"),
        ({"metrics_json": ""}, "(?i)evaluation metrics"),
        ({"metrics_json": "{}"}, "(?i)evaluation metrics"),
        ({"metrics_json": "[0.8]"}, "(?i)evaluation metrics"),
        ({"hyperparameters": "depth=4"}, "(?i)JSON object"),
        ({"ended_at": "2026-11-18 07:00:00"}, "(?i)end before"),
    ],
)
def test_a_training_run_that_cannot_be_reproduced_is_refused(env, extra, why):
    model = _model(env)
    vals = {k: v for k, v in _training_values(model).items() if k != "trained_by"}
    vals["model_id"] = model.id
    vals.update(extra)
    with pytest.raises((UserError, ValidationError), match=why):
        env["fix.ml.training.run"].with_user(_user(env, SCIENTIST)).create(vals)


def test_a_version_cannot_name_another_models_run(env):
    sci = _user(env, SCIENTIST)
    run_model, other = _model(env), _model(env)
    vals = {k: v for k, v in _training_values(run_model).items() if k != "trained_by"}
    vals["model_id"] = run_model.id
    run = env["fix.ml.training.run"].with_user(sci).create(vals)
    with pytest.raises(ValidationError, match="(?i)trained model"):
        env["fix.ml.model.version"].with_user(sci).create(
            {"model_id": other.id, "version": "1.0.0", "training_run_id": run.id}
        )


# ---- page 3: data-sufficiency gate
def _gated_version(env, model):
    """An evaluated version with every gate passed by a reviewer, bias passed by
    a bias test: only the data-sufficiency gate is left to decide."""
    sci, rev = _user(env, SCIENTIST), _user(env, REVIEWER)
    version = (
        env["fix.ml.model.version"]
        .with_user(sci)
        .create(
            {
                "model_id": model.id,
                "version": "2.%d.0" % next(_SEQ),
                "model_card": "Purpose: probe. Limits: none claimed.",
                "metrics_json": '{"auc": 0.8}',
            }
        )
    )
    version.with_user(sci).action_evaluate()
    for gate in ("accuracy", "latency", "bias", "explainability", "safety"):
        env["fix.ml.evaluation.gate"].with_user(rev).create(
            {"version_id": version.id, "gate": gate, "result": "passed"}
        )
    _bias(env, rev, version, "passed")
    return sci, version


def _bias(env, user, version, assessment):
    return (
        env["fix.ml.bias.test"]
        .with_user(user)
        .create(
            {
                "version_id": version.id,
                "segments_tested": "branch; device brand",
                "metric_by_segment": "within-10%: 0.78 / 0.76",
                "assessment": assessment,
                "next_due": "2099-01-01",
            }
        )
    )


def test_a_model_without_a_declared_bar_cannot_be_gated(env, p03):
    model = _model(env)
    res = p03(_user(env, SCIENTIST))(
        "model_write",
        model="fix.ml.data.sufficiency",
        values={
            "model_id": {"id": model.id, "label": model.display_name},
            "observed_history_months": 24,
            "observed_volume": 9000,
            "source_modules": "M14 trade-ins",
        },
    )
    assert "error" in res and "declares no minimum" in res["error"], res


def test_the_gate_measures_against_the_models_own_bar(env, p03):
    model = _model(env, min_history_months=12, min_volume=1000)
    sci = p03(_user(env, SCIENTIST))
    base = {
        "model_id": {"id": model.id, "label": model.display_name},
        "source_modules": "M14 trade-ins",
        # the bar is read-only on the form: a posted lower bar is dropped
        "required_history_months": 1,
        "required_volume": 1,
    }
    # unmet without a revisit date: refused (deferred, never silently rejected)
    res = sci(
        "model_write",
        model="fix.ml.data.sufficiency",
        values=dict(base, observed_history_months=6, observed_volume=5000),
    )
    assert "error" in res and "revisit" in res["error"], res
    deferred = env["fix.ml.data.sufficiency"].browse(
        _ok(
            sci(
                "model_write",
                model="fix.ml.data.sufficiency",
                values=dict(
                    base,
                    observed_history_months=6,
                    observed_volume=5000,
                    deferred_until="2027-05-01",
                ),
            )
        )
    )
    assert deferred.required_history_months == 12 and deferred.required_volume == 1000
    assert deferred.result == "deferred"


def test_the_bar_cannot_be_lowered_through_the_orm_either(env):
    model = _model(env, min_history_months=12, min_volume=1000)
    gate = (
        env["fix.ml.data.sufficiency"]
        .with_user(_user(env, REVIEWER))
        .create(
            {
                "model_id": model.id,
                "required_history_months": 1,
                "required_volume": 1,
                "observed_history_months": 3,
                "observed_volume": 50,
                "source_modules": "M14",
                "deferred_until": "2027-05-01",
            }
        )
    )
    assert (gate.required_history_months, gate.required_volume) == (12, 1000)
    assert gate.result == "deferred"


def test_promotion_needs_the_newest_sufficiency_gate_met(env):
    model = _model(env, min_history_months=12, min_volume=1000)
    sci, version = _gated_version(env, model)
    with pytest.raises(UserError, match="no data-sufficiency gate"):
        version.with_user(sci).action_request_promotion()
    gates = env["fix.ml.data.sufficiency"].with_user(sci)
    gates.create(
        {
            "model_id": model.id,
            "observed_history_months": 3,
            "observed_volume": 200,
            "source_modules": "M14",
            "deferred_until": "2027-05-01",
        }
    )
    with pytest.raises(UserError, match="is deferred"):
        version.with_user(sci).action_request_promotion()
    gates.create(
        {
            "model_id": model.id,
            "observed_history_months": 14,
            "observed_volume": 1500,
            "source_modules": "M14",
            "evaluated_at": fields_now() + datetime.timedelta(minutes=1),
        }
    )
    version.with_user(sci).action_request_promotion(justification="data now sufficient")
    assert version.approval_request_id, "the met gate lets the request reach M63"


def fields_now():
    from odoo import fields

    return fields.Datetime.now()


# ---- page 3: bias test
def test_the_bias_status_follows_the_reviewers_test(env, p03):
    model = _model(env)
    sci_user, rev_user = _user(env, SCIENTIST), _user(env, REVIEWER)
    version = (
        env["fix.ml.model.version"]
        .with_user(sci_user)
        .create({"model_id": model.id, "version": "3.0.0"})
    )
    # the registrant can no longer type it - neither through the form...
    res = p03(sci_user)(
        "model_write",
        model="fix.ml.model.version",
        record_id=version.id,
        values={"bias_status": "passed"},
    )
    assert version.bias_status == "untested", res
    # ...nor through the ORM
    with pytest.raises(UserError, match="follows the recorded bias test"):
        version.with_user(sci_user).write({"bias_status": "passed"})
    with pytest.raises(UserError, match="follows the recorded bias test"):
        env["fix.ml.model.version"].with_user(sci_user).create(
            {"model_id": model.id, "version": "3.0.1", "bias_status": "passed"}
        )
    test_id = _ok(
        p03(rev_user)(
            "model_write",
            model="fix.ml.bias.test",
            values={
                "version_id": {"id": version.id, "label": version.display_name},
                "segments_tested": "branch; device brand",
                "metric_by_segment": "0.78 / 0.71",
                "max_disparity": 0.07,
                "assessment": "failed",
                "next_due": "2027-11-19",
                "documented_by": False,
            },
        )
    )
    test = env["fix.ml.bias.test"].browse(test_id)
    assert test.documented_by == rev_user
    assert version.bias_status == "failed"
    with pytest.raises(UserError, match="(?i)evidence"):
        test.with_user(rev_user).write({"assessment": "passed"})


def test_the_registrant_and_the_model_owner_cannot_review_fairness(env):
    sci = _user(env, SCIENTIST, REVIEWER)
    owner = _user(env, REVIEWER, OWNER)
    model = _model(env, owner_id=owner.id)
    version = (
        env["fix.ml.model.version"]
        .with_user(sci)
        .create({"model_id": model.id, "version": "4.0.0"})
    )
    with pytest.raises(UserError, match="You registered"):
        _bias(env, sci, version, "passed")
    with pytest.raises(UserError, match="You own model"):
        _bias(env, owner, version, "passed")
    assert version.bias_status == "untested"


# ---- page 4: production performance
def _perf(env, user, version, value, floor=0.70, target=0.80, higher=True):
    return (
        env["fix.ml.performance.observation"]
        .with_user(user)
        .create(
            {
                "version_id": version.id,
                "period_start": "2026-11-01",
                "period_end": "2026-11-15",
                "metric_name": "within 10% of assessed",
                "value": value,
                "target": target,
                "floor": floor,
                "higher_is_better": higher,
                "labelled_sample_size": 240,
            }
        )
    )


def test_a_breach_demotes_and_restores_the_prior_champion(env, p03):
    model = _model(env)
    prior = _deployed(env, model, "1.0.0", "2026-10-01 00:00:00")
    newest = _deployed(env, model, "1.1.0", "2026-11-01 00:00:00")
    assert model.serving_version_id == newest
    sci_user = _user(env, SCIENTIST)
    obs = env["fix.ml.performance.observation"].browse(
        _ok(
            p03(sci_user)(
                "model_write",
                model="fix.ml.performance.observation",
                values={
                    "version_id": {"id": newest.id, "label": newest.display_name},
                    "period_start": "2026-11-01",
                    "period_end": "2026-11-15",
                    "metric_name": "within 10% of assessed",
                    "value": 0.61,
                    "target": 0.75,
                    "floor": 0.70,
                    "higher_is_better": True,
                    "labelled_sample_size": 240,
                    # the result is the engine's: posted values are dropped
                    "action_taken": "none",
                    "breached": False,
                },
            )
        )
    )
    assert obs.breached and obs.action_taken == "demoted"
    assert newest.state == "demoted" and newest.demotion_reason
    model.invalidate_recordset()
    assert model.serving_version_id == prior, "the prior champion serves again"
    # a demoted version takes no further observation, and evidence is not edited
    with pytest.raises(UserError, match="serving version"):
        _perf(env, sci_user, newest, 0.9)
    with pytest.raises(UserError, match="(?i)evidence"):
        obs.with_user(sci_user).write({"value": 0.9})


def test_a_breach_with_no_prior_champion_keeps_serving_and_escalates(env):
    model = _model(env)
    only = _deployed(env, model, "1.0.0", "2026-10-01 00:00:00")
    obs = _perf(env, _user(env, OWNER), only, 0.5)
    assert obs.breached and obs.action_taken == "escalated"
    assert only.state == "deployed" and model.serving_version_id == only
    assert any("Escalated" in (m.body or "") for m in only.message_ids)


def test_an_error_metric_breaches_upwards_and_a_good_period_does_nothing(env):
    model = _model(env)
    _deployed(env, model, "1.0.0", "2026-10-01 00:00:00")
    newest = _deployed(env, model, "1.1.0", "2026-11-01 00:00:00")
    sci = _user(env, SCIENTIST)
    fine = _perf(env, sci, newest, 0.15, floor=0.25, target=0.18, higher=False)
    assert not fine.breached and fine.action_taken == "none" and newest.state == "deployed"
    with pytest.raises(ValidationError, match="wrong side"):
        _perf(env, sci, newest, 0.15, floor=0.10, target=0.18, higher=False)
    bad = _perf(env, sci, newest, 0.31, floor=0.25, target=0.18, higher=False)
    assert bad.breached and newest.state == "demoted"


# ---- page 5 / 7: the human decision carries its reason
def test_an_override_without_a_reason_is_refused_from_the_form(env, p03):
    fault = env.ref("cd_ml_services.ml_model_fault_classifier")
    clerk = _user(env)
    run = (
        env["fix.ml.inference.run"]
        .with_user(clerk)
        .create({"model_id": fault.id, "input_text": "ডিসপ্লে কাজ করছে না, screen is dark"})
    )
    run.sudo().write({"state": "computed", "suggested_value": "DSP-01"})
    values = {
        "model_id": {"id": fault.id, "label": fault.display_name},
        "input_text": run.input_text,
        "suggested_value": "DSP-01",
        "final_value": "PWR-02",
        "override_reason": "",
    }
    res = p03(clerk)("model_write", model="fix.ml.inference.run", record_id=run.id, values=values)
    assert "error" in res and "BRU-AIM-05" in res["error"], res
    assert not run.final_value, "nothing of the refused decision is left behind"
    values["override_reason"] = "Power board burnt; the display is fine"
    _ok(p03(clerk)("model_write", model="fix.ml.inference.run", record_id=run.id, values=values))
    assert run.overridden and run.override_reason.startswith("Power board")


# ---- retirement records the consumers' confirmation
def test_retire_needs_the_consumers_confirmation(env, p03):
    model = _model(env, fallback_definition="Depreciation table")
    version = _deployed(env, model, "1.0.0", "2026-10-01 00:00:00")
    owner = p03(_user(env, OWNER))
    res = owner(
        "model_action", model="fix.ml.model.version", ids=[version.id], method="action_retire"
    )
    assert not res["success"] and "Depreciation table" in res["error"], res
    assert version.state == "deployed"
    res = owner(
        "model_action",
        model="fix.ml.model.version",
        ids=[version.id],
        method="action_retire",
        kwargs={"confirmation": "M14 lead confirmed the depreciation table, 19 Nov"},
    )
    assert res["success"], res
    assert version.state == "retired"
    assert any("M14 lead confirmed" in (m.body or "") for m in version.message_ids)
