# A06 final pass - the form engine: the status pill, pickers beyond the choice
# limit, and what a picker's filter may test. A non-admin user throughout: the
# filter runs under sudo, so the plain user is the one who could abuse it.
import itertools
from unittest import mock

import pytest
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api

_SEQ = itertools.count(1)
PO = "fix.purchase.order"
UNSERVED = "ir.attachment"


class FakeRequest:
    def __init__(self, env):
        self.env = env


@pytest.fixture
def call():
    patchers = []

    def _call(env, route, **kw):
        p = mock.patch.object(api, "request", FakeRequest(env))
        p.start()
        patchers.append(p)
        return getattr(api.P03GenericApiController(), route)(**kw)

    yield _call
    for p in patchers:
        p.stop()


@pytest.fixture
def clerk_env(odoo_env):
    """A buyer: reads the purchase order surface, and no partner's private fields."""
    n = next(_SEQ)
    ou = odoo_env["operating.unit"].search([("company_id", "=", odoo_env.company.id)], limit=1)
    user = (
        odoo_env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "Engine Clerk %d" % n,
                "login": "engine.clerk.%d@a06.test" % n,
                "group_ids": [
                    (
                        6,
                        0,
                        [
                            odoo_env.ref("base.group_user").id,
                            odoo_env.ref("cd_requisition.group_fix_procurement_buyer").id,
                        ],
                    )
                ],
                "assigned_operating_unit_ids": [(6, 0, ou.ids)],
                "default_operating_unit_id": ou.id,
            }
        )
    )
    return odoo_env(user=user.id)


@pytest.fixture
def order(odoo_env):
    ou = odoo_env["operating.unit"].search([("company_id", "=", odoo_env.company.id)], limit=1)
    vendor = odoo_env["res.partner"].create({"name": "Engine Vendor %d" % next(_SEQ)})
    return odoo_env[PO].create({"vendor_id": vendor.id, "operating_unit_id": ou.id})


def _vendor_spec(**extra):
    return [{"name": "vendor_id", **extra}]


# --- the status pill ---------------------------------------------------------


def test_status_value_is_served_though_the_form_has_no_state_input(call, clerk_env, order):
    res = call(
        clerk_env,
        "model_form",
        model=PO,
        fields=_vendor_spec(),
        record_id=order.id,
        status_field="state",
    )
    assert "error" not in res
    assert "state" not in [f["name"] for f in res["fields"]]
    assert res["status_value"] == order.state


def test_status_value_serves_only_a_workflow_kind_of_field(call, clerk_env, order):
    """The pill must not become a way to read any field by naming it."""
    res = call(
        clerk_env,
        "model_form",
        model=PO,
        fields=_vendor_spec(),
        record_id=order.id,
        status_field="vendor_id",
    )
    assert res["status_value"] is None
    res = call(
        clerk_env,
        "model_form",
        model=PO,
        fields=_vendor_spec(),
        record_id=order.id,
        status_field="nope",
    )
    assert res["status_value"] is None


# --- pickers beyond the limit ------------------------------------------------


def test_a_list_beyond_the_limit_says_so_and_keeps_the_records_value(
    call, clerk_env, order, odoo_env
):
    with mock.patch.object(api, "PICKER_LIMIT", 2):
        odoo_env["res.partner"].create([{"name": "Filler %d" % i} for i in range(3)])
        res = call(clerk_env, "model_form", model=PO, fields=_vendor_spec(), record_id=order.id)
    meta = res["fields"][0]
    # a header many2one becomes a search box, and still shows the record's value
    assert meta["truncated"] is True and meta["remote"] is True
    assert order.vendor_id.id in [c["id"] for c in meta["choices"]]


def test_a_short_list_is_not_marked_truncated(call, clerk_env, order):
    with mock.patch.object(api, "PICKER_LIMIT", 10**7):
        res = call(clerk_env, "model_form", model=PO, fields=_vendor_spec(), record_id=order.id)
    meta = res["fields"][0]
    assert meta["truncated"] is False and meta["remote"] is False and meta["choices"]


def test_server_search_finds_a_record_beyond_the_limit(call, clerk_env, odoo_env):
    target = odoo_env["res.partner"].create({"name": "Findable Zebra Vendor %d" % next(_SEQ)})
    res = call(clerk_env, "model_choices", model=PO, field="vendor_id", q=target.name)
    assert target.id in [c["id"] for c in res["choices"]]


def test_server_search_refuses_a_model_no_screen_serves(call, clerk_env):
    assert UNSERVED not in api.SURFACES
    res = call(clerk_env, "model_choices", model=UNSERVED, field="company_id", q="a")
    assert res == {"error": "Model not served by the workspace screens"}


def test_server_search_refuses_a_child_grid_the_parent_does_not_declare(call, clerk_env):
    """Naming a served parent does not open an unrelated model."""
    res = call(
        clerk_env,
        "model_choices",
        model=UNSERVED,
        field="company_id",
        q="a",
        parent_model=PO,
        parent_field="vendor_id",
    )
    assert res == {"error": "Model not served by the workspace screens"}


def test_server_search_refuses_a_field_with_no_choices(call, clerk_env):
    res = call(clerk_env, "model_choices", model=PO, field="state", q="a")
    assert res == {"error": "This field has no choices"}


# --- a picker's filter runs under sudo: it must not read values ---------------


@pytest.mark.parametrize(
    "domain",
    [
        [["name", "like", "a%"]],  # a character at a time
        [["name", "=", "Exact Guess"]],  # a free text value
        [["credit_limit", ">", 1000]],  # an amount, above zero is the only test
        [["user_ids.login", "in", ["admin"]]],  # through a link to free text
        [["nope", "=", 1]],  # no such field
        [["name.foo", "=", 1]],  # a path through a value
        "[('name','like','a')]",  # not a domain at all
        [["active", "=", True, "extra"]],  # not a leaf
    ],
)
def test_a_filter_that_could_read_a_value_is_refused(call, clerk_env, order, domain):
    res = call(clerk_env, "model_choices", model=PO, field="vendor_id", q="", domain=domain)
    assert res == {"error": "This list's filter is not valid"}
    res = call(clerk_env, "model_lookup", model=PO, field="vendor_id", term="", domain=domain)
    assert res == {"error": "This list's filter is not valid"}
    res = call(
        clerk_env, "model_form", model=PO, fields=_vendor_spec(domain=domain), record_id=order.id
    )
    assert res.get("error") == "This list's filter is not valid"


def test_a_workflow_filter_narrows_the_list(call, clerk_env, odoo_env):
    keep = odoo_env["res.partner"].create({"name": "Filter Keep %d" % next(_SEQ), "active": True})
    domain = [["active", "=", True], ["parent_id", "=", False]]
    res = call(clerk_env, "model_choices", model=PO, field="vendor_id", q=keep.name, domain=domain)
    assert keep.id in [c["id"] for c in res["choices"]]
    excluded = call(
        clerk_env,
        "model_choices",
        model=PO,
        field="vendor_id",
        q=keep.name,
        domain=[["active", "=", False]],
    )
    assert keep.id not in [c["id"] for c in excluded["choices"]]


def test_above_zero_is_the_one_numeric_test_allowed(call, clerk_env, odoo_env):
    assert api._choice_domain(odoo_env, "res.partner", [["color", ">", 0]]) == [["color", ">", 0]]
    with pytest.raises(api.UserError):
        api._choice_domain(odoo_env, "res.partner", [["color", ">", 5]])


def test_a_dangling_operator_cannot_or_past_the_company_fence(odoo_env):
    """The declared filter is ANDed with the surface's company fence; a lone
    "|" would otherwise OR the fence away."""
    for domain in (["|", ["active", "=", True]], ["|"], ["!"]):
        with pytest.raises(api.UserError):
            api._choice_domain(odoo_env, "res.partner", domain)


def test_search_reads_a_rule_fenced_comodel_as_the_caller(odoo_env):
    """A comodel whose own screens apply record rules is searched as the
    caller, never sudo, so a picker cannot list the rows those screens hide."""
    fenced = next((m for m, conf in api.SURFACES.items() if conf.get("rules")), None)
    if not fenced:
        pytest.skip("no surface declares rules")
    assert not api._picker_source(odoo_env, fenced).env.su
    assert api._picker_source(odoo_env, "res.partner").env.su
