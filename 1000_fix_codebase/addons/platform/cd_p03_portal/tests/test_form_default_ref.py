# A form's own default for a reference (`defaultRef`, 13 Nov 2026): the import
# purchase order starts in USD although the purchase order model defaults to
# BDT (the local order's currency).
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api


def _defaults(env, model, specs):
    ctl = api.P03GenericApiController()
    out_fields = ctl._form_field_meta(env, model, specs)
    return api.P03GenericApiController._form_defaults(env, model, out_fields)


def test_a_form_names_its_own_default_reference(odoo_env):
    usd = odoo_env.ref("base.USD")
    out = _defaults(
        odoo_env,
        "fix.purchase.order",
        [{"name": "currency_id", "defaultRef": "base.USD"}],
    )
    assert out["currency_id"] == {"id": usd.id, "label": usd.display_name}


def test_without_it_the_model_default_stands(odoo_env):
    # the model default is the company's currency (BDT on the estate; a test
    # database may run another)
    company_ccy = odoo_env.company.currency_id
    out = _defaults(odoo_env, "fix.purchase.order", [{"name": "currency_id"}])
    assert out["currency_id"]["id"] == company_ccy.id


def test_a_wrong_or_missing_reference_is_ignored(odoo_env):
    bdt = odoo_env.company.currency_id  # the model default
    for ref in ("base.no_such_record", "base.main_company"):
        out = _defaults(
            odoo_env, "fix.purchase.order", [{"name": "currency_id", "defaultRef": ref}]
        )
        assert out["currency_id"]["id"] == bdt.id, ref
