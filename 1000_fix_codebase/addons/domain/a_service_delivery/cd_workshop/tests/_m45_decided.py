"""M45 now holds every new calibration for a Quality Manager's usage decision
(an instrument is certified only once a QM other than the recorder accepts
it). The M31 tests that use it are about the QC gate, not that decision: each
calibration they record is accepted, as M45's own tests do
(cd_equipment_register/tests/test_a07_m45_operability.py)."""

import pytest


@pytest.fixture(autouse=True)
def calibrations_decided(odoo_env, monkeypatch):
    if "fix.calibration" not in odoo_env:
        return
    cls = type(odoo_env["fix.calibration"])
    if "decision_state" not in cls._fields:
        return
    original = cls.create

    def create(self, vals_list):
        records = original(self, vals_list)
        records.sudo()._guarded().write({"decision_state": "accepted"})
        return records

    monkeypatch.setattr(cls, "create", create)
