# ruff: noqa: I001
# cd_msp_contract models. fix_msp_ext extends fix.msp.alert and
# fix.remote.session — its name sorts after the base file, so the
# alphabetical import below is also the correct load order. fix_msp_lifecycle
# (A02 audit P1/P2) extends all of them, so it comes last.
# fix_msp_rules (M05 capture audit) extends the alert, asset and contract
# after all of them.
# fix_msp_rules_bru (the business rules found unbuilt by the audit) extends them all;
# fix_msp_services (the spec features found unbuilt) follows; fix_msp_services_onboarding
# (sub-module 10, capture audit pass 2) narrows the SLA measure, so it comes last.
from . import (
    fix_msp,
    fix_msp_engines,
    fix_msp_ext,
    fix_msp_lifecycle,
    fix_msp_rules,
    fix_msp_rules_bru,
    fix_msp_services,
    fix_msp_services_onboarding,
    # A02 ERP audit (2026-11-19, stream B1): the guarded contract terms and the
    # credit's report check extend everything above, so they load last.
    fix_msp_a02_controls,
)
