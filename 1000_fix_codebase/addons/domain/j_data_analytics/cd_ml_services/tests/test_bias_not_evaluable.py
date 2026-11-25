"""A11 audit D10 - a bias test that could not be measured has an honest state.

Before this, `fix.ml.bias.test.assessment` offered only "passed" and "failed",
while a people-affecting model with no scored production decisions cannot be
measured at all. The recorder's choices were therefore to assert a result nobody
measured, or to record nothing (which the Fairness Summary showed as "untested"
for ever, with no evidence anyone had tried).

These tests pin the third state and its accounting:
  * "not evaluable" is an accepted assessment and lands on the version's
    bias_status, so the Fairness Summary can show it;
  * the summary counts it in its own bucket, never inside "passed" or "untested";
  * "passed" and "failed" still require a measured metric (the field is required),
    so the new value cannot be used to dodge evidence.
"""

import datetime

import pytest
from odoo.exceptions import UserError, ValidationError


def _people_model(env, code="m26.dispatch.scoring"):
    return env["fix.ml.model"].search([("code", "=", code)], limit=1)


def _deployed_version(env, model):
    return env["fix.ml.model.version"].search(
        [("model_id", "=", model.id), ("state", "=", "deployed")], limit=1
    )


def test_not_evaluable_is_an_offered_assessment(odoo_env):
    """The selection carries all three verdicts (D10)."""
    values = dict(odoo_env["fix.ml.bias.test"]._fields["assessment"].selection)
    assert "not_evaluable" in values, "the honest 'cannot be measured' state is missing"
    assert {"passed", "failed"} <= set(values), "the measured verdicts must stay"
    # and the version status mirrors it, because the test writes it there
    statuses = dict(odoo_env["fix.ml.model.version"]._fields["bias_status"].selection)
    assert "not_evaluable" in statuses, "the version status cannot carry the test's verdict"


def test_a_not_evaluable_test_lands_on_the_version_and_is_counted_separately(odoo_env):
    """Record a test with no ground truth; the summary shows it as its own bucket."""
    from odoo.addons.cd_p03_portal.controllers.a11 import m26

    model = _people_model(odoo_env)
    if not model:
        pytest.skip("no m26.dispatch.scoring on this database")
    version = _deployed_version(odoo_env, model)
    if not version:
        pytest.skip("no deployed version to attach a bias test to")

    before = version.bias_status
    test = odoo_env["fix.ml.bias.test"].create(
        {
            "version_id": version.id,
            "segments_tested": "branch; tenure band",
            "metric_by_segment": "not measurable: 0 scored inference runs on this estate",
            "assessment": "not_evaluable",
            "notes": "Attempted under owner decision D10; no ground truth yet.",
            "next_due": datetime.date.today() + datetime.timedelta(days=90),
        }
    )
    assert test.assessment == "not_evaluable"
    assert version.bias_status == "not_evaluable", (
        "the verdict did not reach the version (was %s)" % before
    )

    pack = m26.fairness_summary(odoo_env)
    assert any(
        str(r.get("bias", "")).lower().startswith("not evaluable") for r in pack["rows"]
    ), "the fairness summary does not show the not-evaluable verdict"
    total = str(pack["totals"].get("bias", ""))
    assert "not evaluable" in total, "the totals line does not count the new bucket"


def test_measured_verdicts_still_need_evidence(odoo_env):
    """The new value must not become a way to record a verdict without a measurement.

    A missing `metric_by_segment` is refused by the database (NOT NULL), which is
    what makes "passed"/"failed" carry evidence; the assertion accepts either the
    ORM's validation error or the constraint, and runs in a savepoint so the
    aborted statement cannot poison the test transaction.
    """
    import psycopg2

    model = _people_model(odoo_env)
    version = _deployed_version(odoo_env, model) if model else None
    if not version:
        pytest.skip("no deployed version to attach a bias test to")
    # The exception must travel THROUGH the savepoint (a swallowed one leaves the
    # transaction aborted and the next statement fails for the wrong reason).
    refused = False
    try:
        with odoo_env.cr.savepoint():
            odoo_env["fix.ml.bias.test"].create(
                {
                    "version_id": version.id,
                    "segments_tested": "branch",
                    # metric_by_segment is required and deliberately left out
                    "assessment": "passed",
                    "next_due": datetime.date.today() + datetime.timedelta(days=90),
                }
            )
    except (ValidationError, UserError, psycopg2.errors.NotNullViolation):
        refused = True
    assert refused, "a 'passed' verdict was accepted without a measured metric"
