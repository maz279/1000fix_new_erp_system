# Live-ORM tests (`odoo_env`, rolled back) for the Bengali back-office language
# (TR-07 / DoD-08): cd_multi_entity ships the bn_BD res.lang (Odoo 19 has only
# bn_IN) and every module's i18n/bn_BD.po must render through it - including
# modules installed before cd_multi_entity (build-test-db.py runs
# `odoo-bin i18n loadlang -l bn_BD` after the install).
import pytest

BN = "bn_BD"


@pytest.fixture
def bn_lang(odoo_env):
    return odoo_env["res.lang"].with_context(active_test=False).search([("code", "=", BN)])


def test_bn_bd_language_is_installed_and_active(odoo_env, bn_lang):
    assert bn_lang, "res.lang bn_BD missing - cd_multi_entity data/res_lang_bn_bd.xml not loaded"
    assert bn_lang == odoo_env.ref("cd_multi_entity.lang_bn_BD")
    assert bn_lang.active
    assert (bn_lang.iso_code, bn_lang.url_code, bn_lang.direction) == (BN, BN, "ltr")
    assert BN in dict(odoo_env["res.lang"].get_installed())


def test_bn_bd_formats_follow_bangladesh_conventions(bn_lang):
    assert bn_lang.date_format == "%d/%m/%Y"
    assert bn_lang.week_start == "7"  # Friday+Saturday weekend: the week starts on Sunday
    # BN-007 lakh/crore grouping, as the portal money formatters render it
    assert bn_lang.format("%.2f", 12345678.0, grouping=True) == "1,23,45,678.00"


@pytest.mark.parametrize(
    ("model", "field", "bengali"),
    [
        ("fix.consolidation.book", "fiscal_year", "অর্থবছর"),  # cd_multi_entity itself
        ("fix.service.order", "technician_id", "নিয়োজিত টেকনিশিয়ান"),  # cd_service_order
        # cd_entity_config is installed BEFORE cd_multi_entity (needs i18n loadlang)
        ("fix.notification.config", "channel", "চ্যানেল"),
    ],
)
def test_field_label_renders_in_bengali(odoo_env, model, field, bengali):
    ir_field = odoo_env["ir.model.fields"]._get(model, field)
    assert ir_field.with_context(lang=BN).field_description == bengali
    # the label the web client receives (fields_get -> Field.get_description)
    described = odoo_env[model].with_context(lang=BN).fields_get([field])[field]["string"]
    assert described == bengali
    # English stays English
    english = odoo_env[model].with_context(lang="en_US").fields_get([field])[field]["string"]
    assert english != bengali
