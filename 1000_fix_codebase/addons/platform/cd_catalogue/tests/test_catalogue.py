# Tests for cd_catalogue (P03-M06) — AS-10 monetary, model constraints.
#
# A04 C13 (2026-11-04): these were hasattr / dir() checks that a constraint
# or a field exists. They now run each rule as a non-admin Catalogue Officer.
import uuid

import pytest
from odoo.exceptions import ValidationError

TAG = "A4C13-CAT-%s" % uuid.uuid4().hex[:6]


@pytest.fixture
def officer(odoo_env):
    return (
        odoo_env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "A04 C13 catalogue officer",
                "login": "a04c13.cat.%s@a04.test" % uuid.uuid4().hex[:6],
                "group_ids": [
                    (
                        6,
                        0,
                        [
                            odoo_env.ref("base.group_user").id,
                            odoo_env.ref("cd_catalogue.group_catalogue_officer").id,
                        ],
                    )
                ],
            }
        )
    )


def _tmpl(env, name):
    return env["product.template"].create({"name": "%s %s" % (TAG, name)})


class TestFixCatalogueItem:
    def test_one_catalogue_item_per_template(self, odoo_env, officer):
        Item = odoo_env["fix.catalogue.item"].with_user(officer)
        tmpl = _tmpl(odoo_env, "one")
        Item.create({"product_tmpl_id": tmpl.id})
        with pytest.raises(Exception, match="product_tmpl_unique"), odoo_env.cr.savepoint():
            Item.create({"product_tmpl_id": tmpl.id})


class TestFixServiceKit:
    def test_kit_needs_components_and_rolls_up_cost(self, odoo_env, officer):
        item = (
            odoo_env["fix.catalogue.item"]
            .with_user(officer)
            .create({"product_tmpl_id": _tmpl(odoo_env, "kit").id, "item_type": "bundle"})
        )
        Kit = odoo_env["fix.service.kit"].with_user(officer)
        with pytest.raises(ValidationError, match="at least one"), odoo_env.cr.savepoint():
            Kit.create({"name": "empty", "catalogue_item_id": item.id})
        kit = Kit.create(
            {
                "name": "kit",
                "catalogue_item_id": item.id,
                "component_ids": [(0, 0, {"notes": "part", "quantity": 2, "standard_cost": 250.0})],
            }
        )
        assert kit.estimated_cost == 500.0
        assert kit.currency_id == odoo_env.ref("base.BDT")


class TestFixRentalSku:
    def test_rates_are_monetary_in_bdt(self, odoo_env, officer):
        item = (
            odoo_env["fix.catalogue.item"]
            .with_user(officer)
            .create({"product_tmpl_id": _tmpl(odoo_env, "rental").id, "item_type": "rental"})
        )
        sku = (
            odoo_env["fix.rental.sku"]
            .with_user(officer)
            .create({"catalogue_item_id": item.id, "daily_rate": 100.0, "security_deposit": 1000.0})
        )
        for field in ("daily_rate", "weekly_rate", "monthly_rate", "security_deposit"):
            assert sku._fields[field].type == "monetary"
        assert sku.currency_id == odoo_env.ref("base.BDT")


class TestFixBrand:
    def test_brand_name_unique(self, odoo_env, officer):
        Brand = odoo_env["fix.brand"].with_user(officer)
        Brand.create({"name": "%s brand" % TAG, "code": "A4U"})
        with pytest.raises(Exception, match="name_unique"), odoo_env.cr.savepoint():
            Brand.create({"name": "%s brand" % TAG, "code": "A4V"})


class TestFixDeviceModel:
    def test_model_unique_within_a_brand(self, odoo_env, officer):
        brand = (
            odoo_env["fix.brand"]
            .with_user(officer)
            .create({"name": "%s mbrand" % TAG, "code": "A4M"})
        )
        Model = odoo_env["fix.device.model"].with_user(officer)
        Model.create({"brand_id": brand.id, "name": "X1"})
        with pytest.raises(Exception, match="brand_name_unique"), odoo_env.cr.savepoint():
            Model.create({"brand_id": brand.id, "name": "X1"})
