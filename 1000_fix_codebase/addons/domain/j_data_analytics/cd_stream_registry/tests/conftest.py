"""A07 ERP audit (2026-11-20) M48-02: an M48 prediction drives work only when the
M26 model version that scored it is deployed with a passed accuracy evaluation
gate. The seeded predictive-maintenance version was grandfathered without one, so
the suites that exercise the work an engine score raises give it its gate here,
inside the test's rolled-back transaction. A module about the gate itself sets
GOVERN_PDM = False and governs explicitly."""

from __future__ import annotations

import pytest

PDM_MODEL = "m26.predictive.maintenance"


@pytest.fixture(autouse=True)
def _governed_pdm_model(request):
    if not getattr(request.module, "GOVERN_PDM", True):
        return
    if "odoo_env" not in request.fixturenames:
        return
    env = request.getfixturevalue("odoo_env")
    if "fix.ml.model" not in env:
        return
    model = env["fix.ml.model"].search([("code", "=", PDM_MODEL)], limit=1)
    version = model._serving_version() if model else None
    if version and not version.gate_ids.filtered(
        lambda g: g.gate == "accuracy" and g.result == "passed"
    ):
        env["fix.ml.evaluation.gate"].create(
            {"version_id": version.id, "gate": "accuracy", "result": "passed"}
        )
