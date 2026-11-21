"""A04 ERP audit (20 Nov 2026) M12-F4: a job is awarded only once Finance has
configured the seller commission scheme in force. Every marketplace test runs
with one configured (as the superuser, rolled back with the test); a test of
the rule itself deactivates it."""

import pytest

from .b4_helpers import seller_scheme


@pytest.fixture(autouse=True)
def _b4_seller_scheme(request):
    if "odoo_env" not in request.fixturenames:
        yield
        return
    env = request.getfixturevalue("odoo_env")
    seller_scheme(env)
    yield
