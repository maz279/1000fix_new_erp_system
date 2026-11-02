# Behavioural tests for the M37 catalogue kernel on the live ORM (`odoo_env`,
# rolled back after every test): computes, constraints and AS-08 events.
import contextlib
import json

import pytest
from odoo.exceptions import ValidationError


@contextlib.contextmanager
def _rejects(env, exc, match):
    """pytest.raises inside a savepoint: an expected failure never leaves a
    half-applied write in the shared test transaction."""
    with pytest.raises(exc, match=match) as info, env.cr.savepoint():
        yield info


def _events(env, event_type, res_id):
    return env["fix.event.outbox"].search(
        [
            ("event_type", "=", event_type),
            ("aggregate", "=", "fix.catalogue.item"),
            ("aggregate_id", "=", res_id),
        ]
    )


def _brand(env, name="Probe Brand", code="PRB"):
    return env["fix.brand"].create({"name": name, "code": code})


def _item(env, **vals):
    tmpl = env["product.template"].create({"name": vals.pop("tmpl_name", "Probe Service")})
    return env["fix.catalogue.item"].create({"product_tmpl_id": tmpl.id, **vals})


# --- fix.brand ---------------------------------------------------------------


def test_brand_model_count_follows_device_models(odoo_env):
    brand = _brand(odoo_env)
    assert brand.model_count == 0
    Model = odoo_env["fix.device.model"]
    Model.create({"brand_id": brand.id, "name": "Probe One"})
    Model.create({"brand_id": brand.id, "name": "Probe Two"})
    assert brand.model_count == 2


# --- fix.device.model --------------------------------------------------------


@pytest.mark.parametrize("year", [1989, 2101])
def test_device_model_rejects_release_year_out_of_range(odoo_env, year):
    brand = _brand(odoo_env)
    with _rejects(odoo_env, ValidationError, match=f"Release year {year} is out of range"):
        odoo_env["fix.device.model"].create(
            {"brand_id": brand.id, "name": "Bad Year", "release_year": year}
        )


@pytest.mark.parametrize("year", [0, 1990, 2024, 2100])
def test_device_model_accepts_unset_and_boundary_years(odoo_env, year):
    brand = _brand(odoo_env)
    model = odoo_env["fix.device.model"].create(
        {"brand_id": brand.id, "name": f"Year {year}", "release_year": year}
    )
    assert model.release_year == year


# --- fix.refurb.grade --------------------------------------------------------


def test_refurb_grade_name_is_derived_from_its_code(odoo_env):
    grades = odoo_env["fix.refurb.grade"].with_context(active_test=False)
    grades.search([("code", "=", "E")]).unlink()
    grade = grades.create({"code": "E", "price_multiplier": 0.1})
    assert grade.name == "Grade E — For Parts"
    assert grade.currency_id == odoo_env.ref("base.BDT")


def test_refurb_grade_name_follows_a_code_change(odoo_env):
    """Regression: the stored name had no @api.depends, so a recoded grade
    kept the old label (Grade D shown for an E-coded row)."""
    grades = odoo_env["fix.refurb.grade"].with_context(active_test=False)
    grades.search([("code", "=", "E")]).unlink()
    grade_d = grades.search([("code", "=", "D")])
    grade_d.code = "E"
    assert grade_d.name == "Grade E — For Parts"


# --- fix.catalogue.item ------------------------------------------------------


def test_catalogue_item_create_emits_item_created_with_brand(odoo_env):
    brand = _brand(odoo_env)
    item = _item(odoo_env, brand_id=brand.id, item_type="part")
    events = _events(odoo_env, "catalogue.item_created", item.id)
    assert len(events) == 1
    payload = json.loads(events.payload)
    assert payload == {
        "product_tmpl_id": item.product_tmpl_id.id,
        "item_type": "part",
        "brand_id": brand.id,
    }
    # the related Bengali-first name mirrors the template's BENGALI name and
    # never touches its English name (R01 re-audit: it mirrored `name`)
    item.product_tmpl_id.name_bn = "প্রোব সার্ভিস"
    assert item.name_bn == "প্রোব সার্ভিস"
    item.name_bn = "প্রোব সেবা"
    assert item.product_tmpl_id.name_bn == "প্রোব সেবা"
    assert item.product_tmpl_id.name == "Probe Service"


def test_catalogue_item_without_brand_emits_null_brand(odoo_env):
    item = _item(odoo_env)
    payload = json.loads(_events(odoo_env, "catalogue.item_created", item.id).payload)
    assert payload["brand_id"] is None
    assert payload["item_type"] == "service"


@pytest.mark.parametrize("field", ["is_out_of_scope", "is_warranty_eligible"])
def test_catalogue_item_scope_or_warranty_change_emits_item_changed(odoo_env, field):
    item = _item(odoo_env)
    item.write({field: not item[field]})
    assert len(_events(odoo_env, "catalogue.item_changed", item.id)) == 1


def test_catalogue_item_other_writes_emit_nothing(odoo_env):
    item = _item(odoo_env)
    item.write({"description_bn": "বিবরণ", "standard_labour_time": 1.5})
    assert not _events(odoo_env, "catalogue.item_changed", item.id)


# --- fix.service.kit ---------------------------------------------------------


def test_service_kit_estimates_sum_component_cost_and_time(odoo_env):
    item = _item(odoo_env, item_type="bundle")
    kit = odoo_env["fix.service.kit"].create(
        {
            "name": "Screen Replacement",
            "catalogue_item_id": item.id,
            "component_ids": [
                (
                    0,
                    0,
                    {"notes": "Test component", "component_type": "part", "standard_cost": 4500.0},
                ),
                (
                    0,
                    0,
                    {
                        "notes": "Bench labour",
                        "component_type": "labour",
                        "standard_cost": 800.0,
                        "time_allocation": 1.5,
                    },
                ),
            ],
        }
    )
    assert kit.estimated_cost == 5300.0
    assert kit.estimated_time == 1.5
    assert kit.currency_id == odoo_env.ref("base.BDT")

    kit.component_ids.filtered(lambda c: c.component_type == "labour").time_allocation = 2.0
    assert kit.estimated_time == 2.0


def test_service_kit_requires_at_least_one_component(odoo_env):
    """Regression: a kit created WITHOUT a component_ids key skipped the
    @api.constrains check entirely and was saved empty."""
    item = _item(odoo_env, item_type="bundle")
    with _rejects(
        odoo_env, ValidationError, match="Service kit 'Empty Kit' must have at least one"
    ):
        odoo_env["fix.service.kit"].create({"name": "Empty Kit", "catalogue_item_id": item.id})


def test_service_kit_cannot_be_emptied_by_write(odoo_env):
    item = _item(odoo_env, item_type="bundle")
    kit = odoo_env["fix.service.kit"].create(
        {
            "name": "One Part Kit",
            "catalogue_item_id": item.id,
            "component_ids": [
                (0, 0, {"notes": "Test component", "component_type": "part", "standard_cost": 10.0})
            ],
        }
    )
    with _rejects(odoo_env, ValidationError, match="must have at least one component"):
        kit.write({"component_ids": [(5, 0, 0)]})


def test_rental_sku_name_mirrors_the_catalogue_product(odoo_env):
    item = _item(odoo_env, tmpl_name="Projector Rental", item_type="accessory")
    sku = odoo_env["fix.rental.sku"].create({"catalogue_item_id": item.id, "daily_rate": 500.0})
    assert sku.name == "Projector Rental"
    assert sku.currency_id == odoo_env.ref("base.BDT")
    assert item.product_tmpl_id.catalogue_item_id == item
