# Document screens whose buttons "did nothing" (fix_real, 12 Nov 2026).
#
# The user's Purchase Orders PDF: every button looked dead. A live walk of the
# document screens (PO, estimates, quotations, proforma, import orders,
# vendor bills, counter sales, online orders, customer invoices) on a copy of
# fix_real found these causes, each pinned here:
#
#   1. every row action was enabled on a list with no row selected (all of
#      them were empty on fix_real) and only toasted "Select a row first";
#   2. the record tab compared a row's state - served as {key, label} - with
#      the plain keys of an action's `states`, so every state-gated action
#      vanished from it (a draft quotation showed none);
#   3. the reason prompt and the one-time-secret dialog were rendered only in
#      the grid view: from a record tab, Submit for Approval, Cancel, Reject
#      and the invoice Cancel / Write-off silently did nothing;
#   4. a save that left a required column blank answered "This record breaks
#      a data rule ... (NotNullViolation)" without naming the field;
#   5. the PO's Vendor picker was empty (no supplier is active yet) with no
#      word of why, and a picker with nothing to offer showed a blank box;
#   6. a counter sale could not be saved from its form: the model requires an
#      operating unit the form never asks for;
#   7. "+ New Online Order" opened a form no back-office role may save;
#   8. the pre-sales estimate form offered a service order as its owner but
#      not the CRM opportunity the server equally accepts.
from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import pytest
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api

SRC = Path(__file__).resolve().parents[1] / "static" / "src"
IMPORT = re.compile(r'from\s+"(\./a\d\d/\w+)"')


def _method(engine, signature):
    """The source of one engine method, from its 4-space-indented signature
    to the closing brace at the same indent."""
    pattern = re.compile(r"^    (%s \{\n.*?\n    \})\n" % re.escape(signature), re.S | re.M)
    found = pattern.search(engine)
    assert found, "p03_workspace.js no longer defines %s" % signature
    return found.group(1)


PROBE = """
import * as M from './meta.mjs';
const { P03_DATA_SCREENS, P03_MODULE_CREATE } = M;
function %(key)s
function %(actions)s
function %(block)s
const host = (cfg, selected, rows) => ({
  state: { gl: { modelCfg: cfg, mlSelected: selected, data: { rows: rows || [] } } },
  t: (x) => x,
  _mlStateKey, recActionsFor, mlActionBlock,
});
const out = { gated: [], blocks: {} };
for (const [id, cfg] of Object.entries(P03_DATA_SCREENS)) {
  if (cfg.kind !== 'model_list') continue;
  for (const act of cfg.actions || []) {
    if (!act.states || !act.states.length) continue;
    const field = cfg.stateField || 'state';
    const row = { id: 1, [field]: { key: act.states[0], label: 'X' } };
    const h = host(cfg, row, [row]);
    out.gated.push({ id, m: act.m,
      shown: recActionsFor.call(h, row).some((a) => a.m === act.m),
      enabled: mlActionBlock.call(h, act) === '' });
  }
}
const quotes = P03_DATA_SCREENS['M36-quotes'];
const submit = quotes.actions.find((a) => a.m === 'action_submit');
const issue = quotes.actions.find((a) => a.m === 'action_send');
const draft = { id: 3, state: { key: 'draft', label: 'Draft' } };
const pos = P03_DATA_SCREENS['M16-pos'];
const send = pos.actions.find((a) => a.m === 'action_send');
out.blocks = {
  empty_list: mlActionBlock.call(host(pos, null, []), send),
  rows_no_selection: mlActionBlock.call(host(pos, null, [draft]), send),
  no_create_list: mlActionBlock.call(host({ ...pos, create: false }, null, []), send),
  draft_submit: mlActionBlock.call(host(quotes, draft, [draft]), submit),
  draft_issue: mlActionBlock.call(host(quotes, draft, [draft]), issue),
  pane: recActionsFor.call(host(quotes, draft, [draft]), draft).map((a) => a.m),
  plain_state: recActionsFor.call(host(quotes, null, []), { id: 4, state: 'draft' }).map((a) => a.m),
};
const field = (screen, name) => ((P03_DATA_SCREENS[screen] || {}).sections || [])
  .flatMap((s) => s.fields || []).find((f) => f.name === name) || null;
out.registry = {
  po_vendor: field('M16-form-po', 'vendor_id'),
  order_form: { create: P03_DATA_SCREENS['M38-form-order'].create, pick: P03_DATA_SCREENS['M38-form-order'].pick || null },
  module_create: Object.values(P03_MODULE_CREATE).map((c) => c.screen),
  estimate_lead: field('M36-form-estimate', 'lead_id'),
  estimate_order: field('M36-form-estimate', 'order_id'),
};
console.log(JSON.stringify(out));
"""


@pytest.fixture(scope="module")
def probe(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_document_buttons")
    for area in sorted(d for d in SRC.iterdir() if re.fullmatch(r"a\d\d", d.name)):
        (tmp / area.name).mkdir()
        for js in area.glob("*.js"):
            (tmp / area.name / (js.stem + ".mjs")).write_text(
                js.read_text(encoding="utf-8"), "utf-8"
            )
    meta = (SRC / "p03_modules_meta.js").read_text(encoding="utf-8")
    (tmp / "meta.mjs").write_text(IMPORT.sub(r'from "\1.mjs"', meta), "utf-8")
    engine = (SRC / "p03_workspace.js").read_text(encoding="utf-8").replace("\r\n", "\n")
    script = PROBE % {
        "key": _method(engine, "_mlStateKey(row)"),
        "actions": _method(engine, "recActionsFor(row)"),
        "block": _method(engine, "mlActionBlock(act)"),
    }
    (tmp / "probe.mjs").write_text(script, "utf-8")
    run = subprocess.run(  # noqa: S603 - fixed argv: the node binary and our own probe file
        [node, str(tmp / "probe.mjs")],
        capture_output=True,
        encoding="utf-8",  # Bengali labels: never the Windows ANSI codepage
        timeout=120,
        check=False,
    )
    assert run.returncode == 0, run.stderr
    return json.loads(run.stdout)


# --- 2. a state-gated action appears for a record in its state -------------
def test_every_state_gated_action_shows_in_the_record_tab(probe):
    hidden = [(g["id"], g["m"]) for g in probe["gated"] if not g["shown"]]
    assert probe["gated"], "no state-gated list action found in the registry"
    assert not hidden, "state-gated actions hidden from the record tab: %s" % hidden[:10]


def test_a_draft_quotation_offers_its_draft_actions(probe):
    pane = probe["blocks"]["pane"]
    assert "action_submit" in pane and "action_cancel" in pane
    assert "action_send" not in pane  # Issue needs an approved quotation
    # a row served with a plain key still works
    assert "action_submit" in probe["blocks"]["plain_state"]


# --- 1. a row action says why it cannot run, instead of looking dead -------
def test_row_actions_are_disabled_with_a_reason_until_a_fitting_row_is_selected(probe):
    b = probe["blocks"]
    assert b["empty_list"] == "No record to act on yet: create one with + New first"
    assert b["no_create_list"] == "No record to act on yet"
    assert b["rows_no_selection"] == "Select a record in the list first"
    assert b["draft_submit"] == ""
    assert b["draft_issue"] == "Not available for a record in this state"
    assert all(g["enabled"] for g in probe["gated"])


def test_the_list_command_bar_disables_row_actions_by_that_reason():
    xml = (SRC / "p03_workspace.xml").read_text(encoding="utf-8")
    loop = re.search(
        r'<t t-foreach="state\.gl\.modelCfg\.actions \|\| \[\]" t-as="act" t-key="act\.m">(.*?)</t>',
        xml,
        re.S,
    )
    assert loop, "the model_list command bar no longer renders modelCfg.actions"
    assert 't-att-disabled="!!this.mlActionBlock(act)"' in loop.group(1)
    assert "this.mlActionBlock(act)" in loop.group(1).split("t-att-title=")[1]


# --- 3. the record tab renders the dialogs its actions open ----------------
def _record_view_block():
    xml = (SRC / "p03_workspace.xml").read_text(encoding="utf-8")
    start = xml.index("<t t-if=\"state.viewMode === 'record_view' &amp;&amp; state.recView\">")
    end = xml.index("<t t-if=\"state.viewMode === 'home'\">", start)
    return xml[start:end]


def test_the_record_tab_renders_the_reason_prompt_and_secret_dialog():
    block = _record_view_block()
    assert 't-if="state.gl &amp;&amp; state.gl.prompt"' in block
    assert "this.glPromptOk()" in block and "this.glPromptCancel()" in block
    assert 't-if="state.gl &amp;&amp; state.gl.secretDialog"' in block


# --- 5. an empty picker explains itself -------------------------------------
def test_an_empty_many2one_picker_shows_its_note():
    xml = (SRC / "p03_workspace.xml").read_text(encoding="utf-8")
    assert "field.emptyNote || 'Nothing to choose yet: no record qualifies for this field.'" in xml
    # only where it matters: a required picker, or one that carries its own note
    assert "(fm.required || field.emptyNote)" in xml


def test_the_po_vendor_picker_says_why_it_is_empty(probe):
    vendor = probe["registry"]["po_vendor"]
    assert vendor["required"] is True
    assert vendor["domain"] == [["fix_supplier_status", "=", "active"]]
    assert "Supplier Approver" in vendor["emptyNote"]


# --- 7. no "+ New" for a document the back office may not create -----------
def test_online_orders_are_not_created_in_the_workspace(probe, odoo_env):
    order_form = probe["registry"]["order_form"]
    assert order_form["create"] is False and order_form["pick"]
    assert "M38-form-order" not in probe["registry"]["module_create"]
    # the reason, read from the ACL: no internal group may create an order
    access = odoo_env["ir.model.access"].search(
        [("model_id.model", "=", "fix.storefront.order"), ("perm_create", "=", True)]
    )
    assert not access.filtered(lambda a: not a.group_id or not a.group_id.share)


# --- 8. a pre-sales estimate can name its opportunity ----------------------
def test_the_estimate_form_offers_both_owners_the_server_accepts(probe):
    reg = probe["registry"]
    assert reg["estimate_order"] and reg["estimate_lead"]
    assert not reg["estimate_lead"].get("readonly")
    from odoo.addons.cd_p03_portal.controllers.a02.writable import WRITABLE

    assert {"order_id", "lead_id"} <= WRITABLE["fix.estimate"]


# --- 4. a blank required column is named ------------------------------------
class FakeRequest:
    def __init__(self, env):
        self.env = env


def test_a_po_saved_without_a_vendor_names_the_vendor(odoo_env):
    ou = odoo_env["operating.unit"].search([], limit=1)
    if not ou:
        pytest.skip("no operating unit on this database")
    with mock.patch.object(api, "request", FakeRequest(odoo_env)):
        res = api.P03GenericApiController().model_write(
            model="fix.purchase.order",
            record_id=False,
            values={"operating_unit_id": ou.id, "date_order": "2026-11-12 10:00:00"},
            lines=None,
        )
    assert res.get("error") == "Vendor is required: fill it in and save again.", res


def test_a_blank_line_column_is_named_as_a_line_field(odoo_env):
    exc = SimpleNamespace(
        diag=SimpleNamespace(column_name="product_id", table_name="fix_purchase_order_line")
    )
    label = api._not_null_label(odoo_env, "fix.purchase.order", exc)
    assert label and label.endswith("(on a line)"), label
    unknown = SimpleNamespace(diag=SimpleNamespace(column_name="nope", table_name="nope"))
    assert api._not_null_label(odoo_env, "fix.purchase.order", unknown) is False


# --- 6. a counter sale takes its unit from where it was rung ---------------
def test_a_counter_sale_without_a_unit_takes_its_branch_unit(odoo_env):
    branch = odoo_env["fix.branch"].search([("operating_unit_id", "!=", False)], limit=1)
    product = odoo_env["product.product"].search([], limit=1)
    if not branch or not product:
        pytest.skip("needs a branch with an operating unit and a product")
    sale = odoo_env["fix.counter.sale"].create(
        {"branch_id": branch.id, "product_id": product.id, "quantity": 1, "unit_price": 100.0}
    )
    assert sale.operating_unit_id == branch.operating_unit_id


def test_a_counter_sale_without_branch_or_shift_takes_the_sellers_unit(odoo_env):
    ou = odoo_env["operating.unit"].search([], limit=1)
    product = odoo_env["product.product"].search([], limit=1)
    if not ou or not product:
        pytest.skip("needs an operating unit and a product")
    seller = odoo_env.user
    seller.write({"operating_unit_ids": [(4, ou.id)], "default_operating_unit_id": ou.id})
    sale = odoo_env["fix.counter.sale"].create(
        {"product_id": product.id, "quantity": 1, "unit_price": 100.0}
    )
    assert sale.operating_unit_id == ou
