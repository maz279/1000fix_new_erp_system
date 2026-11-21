# cd_rental_asset tests: the deployment parameters the rental money path
# fails closed without (A05 remediation, owner decisions D1/D2). The test
# chart is not fix_real's: the roles point at accounts that exist in it, and
# damage compensation at an exempt M51 treatment made here. Rolled back with
# the odoo_env transaction.
import pytest

TEST_ACCOUNTS = {
    "deposit_liability": "212000",
    "recovery_income": "450000",
    "rental_income": "400000",
}
DAMAGE_VAT_CODE = "A05S1-RNT-DAMAGE"


def configure_rental_money(env):
    params = env["ir.config_parameter"].sudo()
    for role, code in TEST_ACCOUNTS.items():
        params.set_param("cd_rental_asset.account_code.%s" % role, code)
    Treatment = env["fix.vat.treatment"].sudo()
    if not Treatment._fix_treatment_for(DAMAGE_VAT_CODE, env.company):
        row = Treatment.create(
            {
                "code": DAMAGE_VAT_CODE,
                "name": "Rental damage compensation (outside VAT)",
                "treatment_type": "exempt",
                "rate": 0.0,
                "company_id": env.company.id,
                # signed off (D12): an adviser-flagged row refuses invoicing
                "verify_with_adviser": False,
            }
        )
        if row.state != "active":
            row._guarded().write({"state": "active"})
    params.set_param("cd_rental_asset.vat_treatment_code.damage", DAMAGE_VAT_CODE)


@pytest.fixture(autouse=True)
def _rental_money_configured(request):
    if "odoo_env" not in request.fixturenames or request.node.get_closest_marker(
        "rental_unconfigured"
    ):
        return
    configure_rental_money(request.getfixturevalue("odoo_env"))


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "rental_unconfigured: the test is about the missing rental parameters (fail closed)",
    )
