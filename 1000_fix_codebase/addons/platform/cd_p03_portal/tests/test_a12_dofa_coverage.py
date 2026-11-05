"""A12 P1-5 / M30-3 — the DOFA coverage report is computed, never typed.

The audit's headline: the ladder governs 18 of 76 approval-bearing models
and three other DoA tables disagree with it. The report lists every
approval-bearing model with the authority that governs it — the migration
backlog P1-5 exists to empty and the single-DoA conflicts to consolidate —
computed live from the registry and the two authority sources.
"""

from ..controllers.a12 import m30


def test_dofa_coverage_lists_every_approval_bearing_model(odoo_env):
    env = odoo_env
    report = m30.dofa_coverage(env)
    assert set(report["cols"]) == {"model", "ladder", "m63", "authority"}

    approvable_cls = type(env["fix.approvable.mixin"])
    dofa_cls = type(env["fix.dofa.mixin"])
    expected = {}
    for name, cls in env.registry.models.items():
        if getattr(cls, "_abstract", False) or getattr(cls, "_transient", False):
            continue
        if issubclass(cls, approvable_cls):
            expected[name] = issubclass(cls, dofa_cls)

    listed = {row["model"] for row in report["rows"]}
    assert listed == set(expected), "every approval-bearing model appears, nothing else"


def test_the_ladder_column_matches_the_registry(odoo_env):
    env = odoo_env
    report = m30.dofa_coverage(env)
    approvable_cls = type(env["fix.approvable.mixin"])
    dofa_cls = type(env["fix.dofa.mixin"])
    for row in report["rows"]:
        cls = env.registry.models[row["model"]]
        assert issubclass(cls, approvable_cls)
        assert (row["ladder"] == "yes") == issubclass(cls, dofa_cls)


def test_the_m63_column_matches_the_rule_book(odoo_env):
    env = odoo_env
    report = m30.dofa_coverage(env)
    targets = {row.res_model for row in env["fix.approval.matrix"].search([]) if row.res_model}
    for row in report["rows"]:
        assert (row["m63"] == "yes") == (row["model"] in targets)
        if row["authority"] == "none":
            assert row["ladder"] == "-" and row["m63"] == "-"
        if row["authority"] == "ladder+m63":
            assert row["ladder"] == "yes" and row["m63"] == "yes"


def test_the_estate_has_real_coverage_and_a_real_backlog(odoo_env):
    """The numbers are allowed to be uncomfortable; they may not be zero-eyed.

    No fabricated zeros (the A12 KPI rule): the estate genuinely has
    ladder-governed models AND ungoverned ones today — the report must say
    so rather than show a tidy 100%."""
    report = m30.dofa_coverage(odoo_env)
    authorities = {row["authority"] for row in report["rows"]}
    assert any(a in ("ladder", "m63", "ladder+m63") for a in authorities)
    assert "none" in authorities, "the P1-5 backlog must be visible, not hidden"
    assert report["rows"], "an empty estate would itself be a finding"
