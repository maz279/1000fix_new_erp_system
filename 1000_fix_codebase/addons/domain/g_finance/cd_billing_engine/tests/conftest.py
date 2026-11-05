"""Shared fixtures for the cd_billing_engine tests.

The A04 C7 claim-consumer suite needs the warranty-claim world (brands,
devices, clerks); cd_warranty_claims' own conftest builds it, and this
module now depends on that module, so its fixture is re-registered here
under the short name ``w`` instead of being rebuilt. (The C10 walker suite
cannot do the same for cd_contract_core's world: its ``c`` fixture lives in
the test module, so the walker suite builds its own.)"""

from odoo.addons.cd_warranty_claims.tests.conftest import wc as w  # noqa: F401
