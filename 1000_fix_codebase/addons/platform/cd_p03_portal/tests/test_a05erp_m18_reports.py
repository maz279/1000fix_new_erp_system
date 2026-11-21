"""A05 ERP audit (20 Nov 2026): the M18 e-waste report packs and KPIs.

XC-06 / M18-10 every pack honours date_from / date_to (Dhaka days);
XC-15 / M18-09 diversion is GRI 306-4: recycling under a certificate counts as
diverted, untriaged / in-process weight is outside the rate;
M18-23 material recovery reports what the recyclers recovered;
XC-18 the zero-target controls.
"""

import datetime
from types import SimpleNamespace

import pytest
from odoo.addons.cd_p03_portal.controllers.a05 import m18
from odoo.addons.cd_p03_portal.tests.a05erp_helpers import SEQ, row_of, set_cols

# a month nothing else in the test database lives in
JAN_2001 = (datetime.date(2001, 1, 1), datetime.date(2001, 1, 31))


@pytest.fixture
def e(odoo_env):
    env = odoo_env
    if "fix.ewaste.collection" not in env:
        pytest.skip("cd_ewaste not installed")
    x = SimpleNamespace(env=env)
    x.customer = env["res.partner"].create({"name": "A05ERP E-waste Donor %d" % next(SEQ)})

    def collection(day, weight, material="other", **cols):
        rec = env["fix.ewaste.collection"].create(
            {
                "customer_id": x.customer.id,
                "material_type": material,
                "weight_kg": weight,
                "collected_on": day,
            }
        )
        set_cols(rec, collected_on=day, **cols)
        return rec

    x.collection = collection
    return x


def test_collection_volume_honours_the_period(e):
    inside = e.collection(datetime.date(2001, 1, 15), 3.0)
    e.collection(datetime.date(2000, 10, 15), 7.0)
    pack = m18.collection_volume(e.env, str(JAN_2001[0]), str(JAN_2001[1]))
    assert pack["totals"]["weight_kg"] == 3.0
    assert [r["period"] for r in pack["rows"]] == ["2001-01"]
    assert inside.weight_kg == 3.0


def _triage(e, col, decision, day, **cols):
    """The triage decision as the assessor leaves it (dated ``day``)."""
    env = e.env
    env.cr.execute(
        """INSERT INTO fix_ewaste_triage (name, company_id, collection_id, decision,
               decided_on, data_bearing, wipe_required)
           VALUES ('A05ERP-TRI', %s, %s, %s, %s, false, false) RETURNING id""",
        [env.company.id, col.id, decision, day],
    )
    set_cols(col, triage_id=env.cr.fetchone()[0], triage_grade=decision, **cols)
    return col


def test_diversion_is_gri_306_4(e):
    day = datetime.date(2001, 1, 10)
    _triage(e, e.collection(day, 10.0), "reuse", day, state="routed")
    _triage(e, e.collection(day, 20.0), "recycle", day, state="certified")
    _triage(e, e.collection(day, 5.0, material="battery"), "hazardous", day, state="disposed")
    _triage(e, e.collection(day, 15.0), "recycle", day, state="recycled")  # in process
    e.collection(day, 100.0, state="collected")  # untriaged: outside the rate
    # received in December, triaged in January: January's cohort
    december = datetime.date(2000, 12, 20)
    _triage(e, e.collection(december, 10.0), "reuse", datetime.date(2001, 1, 5), state="routed")
    gri = m18.gri_306(e.env, *JAN_2001)
    assert gri["triaged_kg"] == 60.0 and gri["diverted_kg"] == 40.0
    assert gri["diversion_rate_pct"] == 66.67  # recycling counts; untriaged does not
    assert gri["directed_to_disposal_kg"] == 5.0 and gri["hazardous_disposal_kg"] == 5.0
    # the report's own definition is the engine's, figure for figure
    own = m18._gri_fallback(m18._triaged_in(e.env, *JAN_2001))
    for key in ("triaged_kg", "diverted_kg", "directed_to_disposal_kg", "diversion_rate_pct"):
        assert own[key] == gri[key], key
    pack = m18.impact_diversion(e.env, str(JAN_2001[0]), str(JAN_2001[1]))
    assert pack["totals"]["weight_kg"] == 60.0 and pack["totals"]["diverted_kg"] == 40.0
    assert "= 66.7%" in pack["notes"][0]
    assert row_of(pack, "disposition", "Reusable")["weight_kg"] == 20.0
    assert any(
        r["disposition"].startswith("Untriaged") and r["weight_kg"] == 100.0 for r in pack["rows"]
    )


def test_material_recovery_reports_the_recovered_material(e):
    env = e.env
    if "fix.ewaste.material.recovery" not in env:
        pytest.skip("material recovery not installed")
    batch = env["fix.ewaste.batch"].create({"material_type": "phone"})
    set_cols(
        batch,
        state="processed",
        processed_on=datetime.date(2001, 1, 20),
        processed_weight_kg=50.0,
    )
    line = env["fix.ewaste.material.recovery"].create(
        {"batch_id": batch.id, "material_class": "pcb", "weight_kg": 12.5, "agreed_rate": 100}
    )
    set_cols(line, recorded_on=datetime.date(2001, 1, 21))
    pack = m18.material_recovery(env, str(JAN_2001[0]), str(JAN_2001[1]))
    row = row_of(pack, "material", "Circuit Boards")
    assert row["recovered_kg"] == 12.5
    assert row["share_pct"] == 25.0
    outside = m18.material_recovery(env, "2001-03-01", "2001-03-31")
    assert not row_of(outside, "material", "Circuit Boards")


def test_zero_target_controls_flag_an_unweighed_receipt(e):
    env = e.env
    batch = env["fix.ewaste.batch"].create({"material_type": "phone"})
    set_cols(batch, state="received", received_on=datetime.date(2001, 1, 5), received_weight_kg=0)
    pack = m18.zero_target_controls(env, str(JAN_2001[0]), str(JAN_2001[1]))
    row = next(r for r in pack["rows"] if r["control"].startswith("Chain-of-custody"))
    assert row["status"] == "BREACH" and batch.name in row["examples"]
