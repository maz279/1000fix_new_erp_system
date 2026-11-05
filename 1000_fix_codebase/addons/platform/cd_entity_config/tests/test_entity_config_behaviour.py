# Behavioural tests for cd_entity_config (M30 platform administration) on the
# live ORM (`odoo_env`, rolled back after every test).
import contextlib
import json

import pytest
from odoo.addons.cd_entity_config.models.fix_feature_flag import (
    FixFeatureFlag,
    flag_enabled,
)
from odoo.exceptions import ValidationError


@contextlib.contextmanager
def _rejects(env, exc, match):
    """pytest.raises inside a savepoint: the failed write is rolled back so
    the test transaction stays usable (the row never lingers)."""
    with pytest.raises(exc, match=match) as info, env.cr.savepoint():
        yield info


def _entity(env, code="ECTEST"):
    company = env.company
    existing = env["fix.entity"].search([("company_id", "=", company.id)], limit=1)
    return existing or env["fix.entity"].create(
        {"code": code, "legal_name": "Entity Test Ltd", "company_id": company.id}
    )


def _ou(env):
    return env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)


def _branch(env, code="B1", name="Gulshan Branch"):
    return env["fix.branch"].create(
        {"code": code, "name": name, "entity_id": _entity(env).id, "operating_unit_id": _ou(env).id}
    )


def _zone(env, code="ZT1"):
    zone = env["fix.zone"].search([("code", "=", code)], limit=1)
    return zone or env["fix.zone"].create({"name": "Test Zone", "code": code})


# --- fix.bd.address -------------------------------------------------------------


@pytest.mark.parametrize("postcode", ["12a8", "120", "abcd"])
def test_bd_address_rejects_malformed_postcodes(odoo_env, postcode):
    with _rejects(odoo_env, ValidationError, match="exactly 4 digits"):
        odoo_env["fix.bd.address"].create(
            {"division": "Dhaka", "district": "Dhaka", "postcode": postcode}
        )


def test_bd_address_formats_in_bangladeshi_order_with_bengali_parts(odoo_env):
    address = odoo_env["fix.bd.address"].create(
        {
            "division": "Dhaka",
            "district": "Dhaka",
            "district_bn": "ঢাকা",
            "upazila": "Tejgaon",
            "upazila_bn": "তেজগাঁও",
            "street": "5",
            "house": "12",
            "postcode": "1208",
        }
    )
    expected = "বাড়ি 12, রোড 5, তেজগাঁও, ঢাকা 1208"
    assert address.format_bn() == expected
    # the BN-007 rendering IS the record's display name (regression: it lived
    # in name_get, which Odoo 19 never calls - the UI showed "fix.bd.address,N")
    assert address.display_name == expected
    address.write({"house": "7", "postcode": False})
    assert address.display_name == "বাড়ি 7, রোড 5, তেজগাঁও, ঢাকা"
    branch = _branch(odoo_env)
    branch.address_id = address
    assert branch.address_id.display_name == "বাড়ি 7, রোড 5, তেজগাঁও, ঢাকা"


def test_bd_address_minimal_parts_fall_back_to_latin_names(odoo_env):
    Address = odoo_env["fix.bd.address"]
    no_upazila = Address.create({"division": "Sylhet", "district": "Sylhet"})
    assert no_upazila.format_bn() == "Sylhet"
    latin_upazila = Address.create(
        {"division": "Khulna", "district": "Khulna", "upazila": "Sonadanga"}
    )
    assert latin_upazila.format_bn() == "Sonadanga, Khulna"
    assert (no_upazila.display_name, latin_upazila.display_name) == ("Sylhet", "Sonadanga, Khulna")


# --- fix.entity / fix.branch -----------------------------------------------------


def test_entity_code_must_be_uppercase(odoo_env):
    company = odoo_env["res.company"].create({"name": "Lowercase Co"})
    with _rejects(odoo_env, ValidationError, match="uppercase"):
        odoo_env["fix.entity"].create(
            {"code": "bad-code", "legal_name": "Bad", "company_id": company.id}
        )


def test_entity_defaults_and_branch_count(odoo_env):
    entity = _entity(odoo_env)
    assert entity.country_id == odoo_env.ref("base.bd")
    assert entity.currency_id == odoo_env.ref("base.BDT")
    before = entity.branch_count
    _branch(odoo_env, "B1")
    _branch(odoo_env, "B2", "Uttara Branch")
    assert entity.branch_count == before + 2


def test_branch_company_derives_from_entity_and_onchange_scopes_ous(odoo_env):
    branch = _branch(odoo_env)
    assert branch.company_id == odoo_env.company
    assert branch._onchange_entity() == {
        "domain": {"operating_unit_id": [("company_id", "=", odoo_env.company.id)]}
    }
    assert odoo_env["fix.branch"].new({})._onchange_entity() is None


def test_country_pack_action_load_stamps_loaded_at(odoo_env):
    """A12 P1-4: loading now requires the certification lifecycle, so the
    fixture walks it: a pack with one line, validated, certified (with a
    basis) and activated; loading stamps loaded_at only then."""
    pack = odoo_env["fix.country.pack"].create(
        {"name": "Test Pack", "code": "TST-PACK", "kind": "divisions"}
    )
    odoo_env["fix.country.pack.line"].create(
        {"pack_id": pack.id, "code": "DHA", "name": "Dhaka", "name_bn": "ঢাকা"}
    )
    assert not pack.loaded_at
    pack.action_validate()
    pack.sudo().action_certify(note="test gazette basis")
    pack.action_activate()
    assert pack.action_load() is True
    assert pack.loaded_at


# --- fix.feature.flag -------------------------------------------------------------


def _flag(env, key="probe.flag", **vals):
    return env["fix.feature.flag"].create({"key": key, "name": key, **vals})


def test_unknown_flag_fails_closed(odoo_env):
    """Regression: is_enabled filtered on a non-existent `active` field and
    raised ValueError instead of answering."""
    assert odoo_env["fix.feature.flag"].is_enabled("no.such.flag") is False


def test_disabled_flag_is_off(odoo_env):
    _flag(odoo_env, enabled=False)
    assert odoo_env["fix.feature.flag"].is_enabled("probe.flag") is False


def test_enabled_global_flag_is_on(odoo_env):
    _flag(odoo_env, enabled=True)
    assert odoo_env["fix.feature.flag"].is_enabled("probe.flag") is True


def test_branch_scoped_flag_is_on_only_for_listed_branches(odoo_env):
    listed, other = _branch(odoo_env, "B1"), _branch(odoo_env, "B2", "Mirpur Branch")
    _flag(odoo_env, enabled=True, scope="branch", branch_ids=[(6, 0, listed.ids)])
    Flag = odoo_env["fix.feature.flag"]
    assert Flag.is_enabled("probe.flag", branch=listed) is True
    assert Flag.is_enabled("probe.flag", branch=other) is False
    # scope set but no branch context -> fail closed
    assert Flag.is_enabled("probe.flag") is False


def test_base_check_fails_closed_without_the_role_extension(odoo_env):
    """cd_entity_config's own is_enabled - what answers where cd_rbac_ext is
    not installed (in this registry the extension sits in front of it)."""
    Flag = odoo_env["fix.feature.flag"]
    assert FixFeatureFlag.is_enabled(Flag, "no.such.flag") is False
    _flag(odoo_env, enabled=False)
    assert FixFeatureFlag.is_enabled(Flag, "probe.flag") is False
    Flag.search([("key", "=", "probe.flag")]).enabled = True
    assert FixFeatureFlag.is_enabled(Flag, "probe.flag") is True


def test_role_scoped_flag_without_role_context_fails_closed(odoo_env):
    _flag(odoo_env, enabled=True, scope="role")
    assert odoo_env["fix.feature.flag"].is_enabled("probe.flag") is False


class _Gated:
    def __init__(self, env):
        self.env = env

    @flag_enabled("probe.gate")
    def double(self, value):
        """Gated work."""
        return value * 2

    @flag_enabled("probe.gate", default=True)
    def increment(self, value):
        return value + 1


def test_flag_enabled_decorator_runs_when_flag_on(odoo_env):
    _flag(odoo_env, key="probe.gate", enabled=True)
    gated = _Gated(odoo_env)
    assert gated.double(4) == 8
    assert gated.increment(4) == 5
    assert _Gated.double.__doc__ == "Gated work."  # functools.wraps keeps metadata


def test_flag_enabled_decorator_silently_skips_when_flag_off(odoo_env):
    gated = _Gated(odoo_env)
    assert gated.double(4) is None
    # default=True: a missing/disabled flag still runs the capability
    assert gated.increment(4) == 5


# --- fix.geofence -------------------------------------------------------------------


def _fence(env, geometry, geofence_type="circle"):
    return env["fix.geofence"].create(
        {
            "name": "Fence",
            "zone_id": _zone(env).id,
            "geofence_type": geofence_type,
            "geometry_json": geometry if isinstance(geometry, str) else json.dumps(geometry),
        }
    )


@pytest.mark.parametrize(
    ("geofence_type", "geometry", "message"),
    [
        ("circle", "{not json", "valid JSON"),
        ("circle", {"lat": 23.7, "lng": 90.4}, "Circle geofence needs radius_m"),
        ("circle", {"lng": 90.4, "radius_m": 10}, "Circle geofence needs lat"),
        ("circle", {"lat": 23.7, "lng": 90.4, "radius_m": 0}, r"radius_m must be within"),
        ("circle", {"lat": 23.7, "lng": 90.4, "radius_m": 100001}, r"radius_m must be within"),
        ("polygon", {"points": [[23.7, 90.4], [23.8, 90.5]]}, "at least 3 points"),
        ("polygon", {}, "at least 3 points"),
        ("polygon", {"points": [[23.7, 90.4], [91, 90.5], [23.9, 90.6]]}, "out of lat/lng"),
        ("polygon", {"points": [[23.7, 90.4], [23.8, 181], [23.9, 90.6]]}, "out of lat/lng"),
    ],
)
def test_geofence_rejects_invalid_geometry(odoo_env, geofence_type, geometry, message):
    with _rejects(odoo_env, ValidationError, match=message):
        _fence(odoo_env, geometry, geofence_type)


def test_geofence_accepts_valid_circle_and_polygon(odoo_env):
    circle = _fence(odoo_env, {"lat": 23.79, "lng": 90.41, "radius_m": 100000})
    polygon = _fence(
        odoo_env, {"points": [[23.7, 90.4], [23.8, 90.5], [-90, 180]]}, geofence_type="polygon"
    )
    assert circle.geofence_type == "circle"
    assert polygon.zone_id.geofence_ids == circle | polygon


# --- fix.notification.config ----------------------------------------------------------


def _config(env, **vals):
    vals = {"consent_class": "service", "channel": "sms", **vals}
    return env["fix.notification.config"].create(vals)


def test_notification_config_name_tracks_class_and_channel(odoo_env):
    config = _config(odoo_env, consent_class="transactional", channel="email")
    assert config.name == "transactional / email"
    config.channel = "whatsapp"  # regression: the stored name had no @api.depends
    assert config.name == "transactional / whatsapp"


@pytest.mark.parametrize("vals", [{"frequency_cap": -1}, {"combined_cap_non_transactional": -2}])
def test_notification_config_rejects_negative_caps(odoo_env, vals):
    with _rejects(odoo_env, ValidationError, match="cannot be negative"):
        _config(odoo_env, **vals)


def test_marketing_never_uses_the_masking_route(odoo_env):
    with _rejects(odoo_env, ValidationError, match="BD-02"):
        _config(odoo_env, consent_class="marketing", sms_route="masking")
    ok = _config(odoo_env, consent_class="marketing", sms_route="non-masking", frequency_cap=2)
    assert ok.send_window == "24/7"


# --- fix.working.calendar ----------------------------------------------------------------


def test_working_window_must_be_ordered_within_the_day(odoo_env):
    calendar = odoo_env["fix.working.calendar"].create({"name": "National"})
    Line = odoo_env["fix.working.calendar.line"]
    for hour_from, hour_to in ((10.0, 9.0), (-1.0, 8.0), (9.0, 24.5), (9.0, 9.0)):
        with _rejects(odoo_env, ValidationError, match="0 <= from < to <= 24"):
            Line.create(
                {
                    "calendar_id": calendar.id,
                    "weekday": "sun",
                    "hour_from": hour_from,
                    "hour_to": hour_to,
                }
            )
    line = Line.create(
        {"calendar_id": calendar.id, "weekday": "sun", "hour_from": 0.0, "hour_to": 24.0}
    )
    assert calendar.line_ids == line


def test_holiday_end_cannot_precede_start(odoo_env):
    calendar = odoo_env["fix.working.calendar"].create({"name": "National"})
    Holiday = odoo_env["fix.working.calendar.holiday"]
    with _rejects(odoo_env, ValidationError, match="precedes its start"):
        Holiday.create(
            {
                "calendar_id": calendar.id,
                "name": "Eid",
                "date_from": "2026-03-21",
                "date_to": "2026-03-20",
            }
        )
    eid = Holiday.create(
        {
            "calendar_id": calendar.id,
            "name": "Eid",
            "date_from": "2026-03-20",
            "date_to": "2026-03-22",
        }
    )
    assert calendar.holiday_ids == eid


# --- fix.zone ----------------------------------------------------------------------------


def test_zone_display_name_prefers_bengali_then_latin(odoo_env):
    """Regression: the Bengali-first label lived in name_get, which Odoo 19
    never calls, so the UI showed the Latin name only."""
    bengali = odoo_env["fix.zone"].create({"name": "North", "name_bn": "উত্তর", "code": "ZN"})
    latin = odoo_env["fix.zone"].create({"name": "South", "code": "ZS"})
    assert bengali.display_name == "উত্তর"
    assert latin.display_name == "South"
    latin.name_bn = "দক্ষিণ"
    assert latin.display_name == "দক্ষিণ"
    bengali.name_bn = False
    assert bengali.display_name == "North"
