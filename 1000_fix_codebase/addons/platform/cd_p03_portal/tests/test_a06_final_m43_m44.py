# A06 final pass: the M43 and M44 screens a user reaches, read from the fragments
# the workspace renders. A control is not done until it can be reached: every
# screen's columns exist, every button is served by its surface and carries the
# argument it needs, a long form is tabbed with every section on a declared tab,
# status labels cover every state, and the form endpoint serves a picker's domain.
from __future__ import annotations

import inspect
import re
from pathlib import Path
from unittest import mock

import pytest
from odoo.addons.cd_p03_portal.controllers import a06
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api

FRAGMENTS = Path(api.__file__).resolve().parents[1] / "static" / "src" / "a06"
STATE_FIELDS = {"state"}


def _block(text, start):
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    raise AssertionError("unbalanced fragment")


def _screens(code):
    text = (FRAGMENTS / ("%s.js" % code)).read_text(encoding="utf-8")
    start = text.index("export const SCREENS = {")
    body = text[start : text.index("export const REPORT_ROUTES")]
    out = {}
    for match in re.finditer(r"^  '(M\d+-[a-z0-9-]+)': \{", body, re.M):
        out[match.group(1)] = _block(body, match.end() - 1)
    return out, text


CODES = ("m43", "m44")
ALL = {sid: blk for code in CODES for sid, blk in _screens(code)[0].items()}
FORMS = {sid: blk for sid, blk in ALL.items() if "kind: 'model_form'" in blk}
LISTS = {sid: blk for sid, blk in ALL.items() if "kind: 'model_list'" in blk}


def _model(blk):
    return re.search(r"model: '([a-z0-9_.]+)'", blk).group(1)


def _header_fields(blk):
    head = blk
    grid = re.search(r"\blines: \{", blk)
    if grid:
        head = blk[: grid.start()]
    return re.findall(r"\{ name: '([a-z0-9_]+)'", head)


def _sections(blk):
    return re.findall(r"\{ (?:tab: '([a-z]+)', )?title: '", blk)


@pytest.mark.parametrize("sid", sorted(FORMS))
def test_a_long_form_is_tabbed_and_every_section_is_on_a_declared_tab(sid):
    blk = FORMS[sid]
    declared = re.findall(r"\{ id: '([a-z]+)', label: '", blk)
    sections = _sections(blk)
    if len(_header_fields(blk)) > 15:
        assert declared, "%s has more than 15 fields and no tabs" % sid
    if declared:
        assert all(sections), "%s has a section with no tab: it renders on every tab" % sid
        assert set(sections) <= set(declared), "%s names an undeclared tab" % sid
        assert re.findall(r"\bbn: '", blk), "%s tabs have no Bengali label" % sid


@pytest.mark.parametrize("sid", sorted(FORMS))
def test_every_form_field_exists_and_the_status_covers_every_state(odoo_env, sid):
    blk = FORMS[sid]
    model = odoo_env[_model(blk)]
    for name in re.findall(r"\{ name: '([a-z0-9_]+)'", blk.split("lines: {")[0]):
        assert name in model._fields, "%s: %s.%s" % (sid, model._name, name)
    status = re.search(r"status: \{ field: '([a-z_]+)', labels: \{(.*?)\} \}", blk, re.S)
    if status:
        labels = set(re.findall(r"([a-z_]+):", status.group(2)))
        values = {v for v, _l in model._fields[status.group(1)]._description_selection(odoo_env)}
        assert values <= labels, "%s status misses %s" % (sid, values - labels)


@pytest.mark.parametrize("sid", sorted(FORMS))
def test_no_form_offers_a_guarded_field_as_an_input(odoo_env, sid):
    blk = FORMS[sid]
    model = odoo_env[_model(blk)]
    if not hasattr(model, "_fix_guarded_fields"):
        return
    guarded = model.browse()._fix_guarded_fields()
    for match in re.finditer(r"\{ name: '([a-z0-9_]+)'([^{}]*)\}", blk):
        if "readonly: true" not in match.group(2):
            assert match.group(1) not in guarded, "%s offers %s" % (sid, match.group(1))


@pytest.mark.parametrize("sid", sorted(LISTS))
def test_every_list_column_and_button_is_real(odoo_env, sid):
    blk = LISTS[sid]
    name = _model(blk)
    model = odoo_env[name]
    cols = re.search(r"cols: \[([^\]]*)\]", blk).group(1)
    for col in re.findall(r"'([a-z0-9_]+)'", cols):
        assert col in model._fields, "%s: %s has no %s" % (sid, name, col)
    allowed = a06.SURFACES[name]["actions"]
    for button in re.finditer(r"\{ m: '([a-z_]+)', l: '[^']*'([^{}]*)\}", blk):
        method, extra = button.group(1), button.group(2)
        assert method in allowed, "%s: %s refuses %s" % (sid, name, method)
        fn = getattr(model, method, None)
        assert callable(fn), "%s: %s.%s" % (sid, name, method)
        kwarg = re.search(r"kwarg: '([a-z_]+)'", extra)
        if kwarg:
            assert kwarg.group(1) in inspect.signature(fn).parameters, (sid, method)


# a method that refuses without this value must collect it on its button
NEEDS_ARGUMENT = {
    "M43-planned": {"action_reopen": "reason"},
    "M44-proforma": {"action_reject": "reason"},
    "M44-lca": {"action_reject": "reason"},
    "M44-irc": {"action_suspend": "reason"},
    "M44-agent": {"action_block": "reason"},
    "M44-boe": {
        "action_accept_variance": "reason",
        "action_cancel_assessed": "reason",
        "action_reverse": "reason",
    },
    "M44-lc-pay": {"action_link_boe": "boe_no"},
    "M44-arrival": {"action_arrive": "arrival_date"},
    "M44-advance": {"action_approve": "reason", "action_reject": "reason"},
}


@pytest.mark.parametrize("sid", sorted(NEEDS_ARGUMENT))
def test_a_button_collects_what_its_action_needs(sid):
    blk = ALL[sid]
    for method, kwarg in NEEDS_ARGUMENT[sid].items():
        button = re.search(r"\{ m: '%s', l: '[^']*'([^{}]*)\}" % method, blk)
        assert button, "%s has no %s button" % (sid, method)
        assert "ask: " in button.group(1) and "kwarg: '%s'" % kwarg in button.group(1), (
            sid,
            method,
        )


@pytest.mark.parametrize("code", CODES)
def test_every_screen_is_on_the_nav_and_every_row_opens_a_form(code):
    screens, text = _screens(code)
    prefix = code.upper()
    nav = set(re.findall(r"\{ id: '(%s-[a-z0-9-]+)', en: '[^']+', bn: '[^']+'" % prefix, text))
    chips = text[text.index("__by_screen__") :]
    for sid, blk in screens.items():
        if "kind: 'model_list'" in blk or ("kind: 'table_report'" in blk and "-rpt-" not in sid):
            assert sid in nav, "%s is not on the nav" % sid
        if "kind: 'model_list'" in blk:
            assert "'%s':" % sid in chips, "%s has no form chip" % sid
    by_model = text[text.index("__by_model__") : text.index("__by_screen__")]
    for sid, blk in screens.items():
        if "kind: 'model_form'" in blk:
            assert "'%s':" % _model(blk) in by_model, "%s has no model chip" % sid


def _form(env, user, model, fields, lines=None):
    with mock.patch.object(api, "request", mock.Mock(env=env(user=user.id))):
        method = api.P03GenericApiController.model_form
        method = getattr(method, "original_endpoint", method)
        return method(api.P03GenericApiController(), model=model, fields=fields, lines=lines)


def test_the_form_serves_a_named_filtered_line_picker(odoo_env):
    """A3: the Bill of Entry line picker lists 'Order / Part x Qty' and leaves
    out the lines of an order already received."""
    env = odoo_env
    ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    part = env["fix.spare.part"].create({"name": "A06F Picker", "part_number": "A06F-PICK"})
    orders = env["fix.import.order"]
    for suffix in ("OPEN", "DONE"):
        orders |= orders.create(
            {
                "name": "A06F-%s" % suffix,
                "operating_unit_id": ou.id,
                "line_ids": [(0, 0, {"part_id": part.id, "quantity": 4, "unit_price": 1})],
            }
        )
    orders[1].sudo()._guarded().write({"state": "received"})
    user = env["res.users"].create(
        {
            "name": "A06F Picker User",
            "login": "a06f.picker@a06.test",
            "group_ids": [(6, 0, [env.ref("base.group_user").id])],
        }
    )
    blk = FORMS["M44-form-boe"]
    domain = [["order_id.state", "not in", ["received", "landed", "closed"]]]
    assert "domain: [['order_id.state', 'not in', ['received', 'landed', 'closed']]]" in blk
    out = _form(
        env,
        user,
        "fix.import.boe",
        [{"name": "boe_no"}],
        lines={
            "field": "line_ids",
            "fields": [{"name": "order_line_id", "domain": domain}, {"name": "quantity"}],
        },
    )
    assert "error" not in out, out
    meta = next(f for f in out["lines"]["fields"] if f["name"] == "order_line_id")
    labels = [c["label"] for c in meta["choices"]]
    assert "A06F-OPEN / A06F Picker x 4" in labels
    assert not [lb for lb in labels if lb.startswith("A06F-DONE")]
    assert not [lb for lb in labels if lb.startswith("fix.import.order.line,")]
