"""A02 ERP pass 2, X5-11 (owner decision D26) - evidence, not a fix.

The finding: the BER write-off (M31), the consignment damage-claim payout (M03)
and the manual MSP SLA credit (M05) take their approval ladder from code
constants instead of the DoA register. The register IS consulted: a ladder
ruled in force in fix.dofa.ladder (two-person ruling, A12 M30-1/-2) is read
by fix.dofa.mixin._dofa_tier_for_amount (cd_entity_config
fix_dofa_threshold.py), the one chokepoint every DOFA tier derivation goes
through. The coded ladders are only the fallback while nothing is ruled -
which is exactly D26. These tests pin that for the three models named.
``odoo_env`` rolls back after each test.
"""

import pytest

CASES = [
    # model, coded tier of BDT 4,000 (no ruling), ruled tier
    ("fix.damage.claim", "tier_2", "tier_1"),  # _DOFA_CLAIM_THRESHOLDS
    ("fix.msp.sla.credit", "tier_4", "tier_1"),  # _DOFA_MANUAL_CREDIT_THRESHOLDS
    ("fix.workshop.job", "tier_2", "tier_1"),  # BER_DOFA_THRESHOLDS
]


def _rule(env, model, bands):
    ladder = env["fix.dofa.ladder"].create(
        {
            "name": "A02R2 register %s" % model,
            "target_model": model,
            "basis": "ruling",
            "threshold_ids": [
                (0, 0, {"upper_bound": bound, "tier": tier, "note": "x511"})
                for bound, tier in bands
            ],
        }
    )
    # superuser service code: the two-person ruling is exercised in
    # cd_entity_config's own A12 suite; here only its EFFECT matters
    ladder.action_put_in_force(reference="X5-11 evidence")
    assert ladder.in_force
    return ladder


@pytest.mark.parametrize("model,coded,ruled", CASES)
def test_a_ruled_register_ladder_governs_the_coded_one(odoo_env, model, coded, ruled):
    """Every tier derivation of these models passes _dofa_tier_for_amount
    (the damage claim's uninsured bump is applied on top of it)."""
    env = odoo_env
    if model not in env:
        pytest.skip("%s not installed" % model)
    Model = env[model]
    assert Model._dofa_tier_for_amount(4000.0) == coded  # nothing ruled: the code fallback
    _rule(env, model, [(5000.0, "tier_1"), (1e9, "tier_3")])
    assert Model._dofa_tier_for_amount(4000.0) == ruled  # the register decides
    assert Model._dofa_tier_for_amount(60000.0) == "tier_3"
