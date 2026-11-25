# A03 - a form bound to a model that OWNS child records must display them.
#
# Raised by a user looking at M33 sub-module 6, "Kits & Bundles", and asking
# what it uniquely does: the screens showed a kit's name, its computed cost and
# its computed time, and never the components those two numbers are computed
# FROM. A kit is its components. The sub-module looked empty because the only
# thing in it was hidden.
#
# It was not only kits. The workspace engine has supported child-line grids all
# along (`lines: {field, title, fields[]}`, served by /p03/model/form and
# written back by /p03/model/write) and A06/A07/A08 forms use them, but **0 of
# 71 A03 forms did** while 10 A03 models own child collections.
#
# Why six audit passes missed it: the "no flat forms" test asserted that every
# form declares TABS. A nine-tab form that never shows its own children passes
# that. Tabs were the wrong proxy for the requirement, which was comprehensive
# data entry.
from __future__ import annotations

import re
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "static" / "src" / "a03"
SCREEN = re.compile(r"^[ \t]{2,6}'([A-Za-z0-9:_-]+)':\s*\{", re.M)
MODEL = re.compile(r"model:\s*'([a-z0-9_.]+)'")

# Parents whose child collection is incidental rather than constitutive: a
# reverse link that belongs on its own list screen, not inside this form.
# Keep this list short and justified - it is the obvious escape hatch.
INCIDENTAL = {
    # A party's users, bank accounts, payment tokens and discuss-channel
    # memberships are Odoo substrate hanging off res.partner, not the party
    # record's own content - that is its contacts (child_ids), which the
    # form does show.
    ("res.partner", "user_ids"),
    ("res.partner", "bank_ids"),
    ("res.partner", "channel_member_ids"),
    ("res.partner", "rtc_session_ids"),
    ("res.partner", "payment_token_ids"),
    ("res.partner", "invoice_ids"),
    ("res.partner", "contract_ids"),
    ("res.partner", "employee_ids"),
    ("res.partner", "company_ids"),
    ("res.partner", "opportunity_ids"),
    ("res.partner", "meeting_ids"),
    ("res.partner", "calendar_last_notif_ack"),
    # a loyalty programme's accounts have their own register (M10-enrol);
    # what constitutes the programme is its tiers, which the form shows.
    ("fix.loyalty.program", "account_ids"),
    # a loyalty account's vouchers have their own screen (M10-vouchers);
    # the account's own content is its points ledger.
    ("fix.loyalty.account", "voucher_ids"),
    # an import batch's staged rows have their own register (M33-import-
    # lines) and run to tens of thousands per batch (the vendor list staged
    # 26,680): a form grid would load them all. The batch form shows the
    # counts; the rows are audited on their list.
    ("fix.party.import.batch", "line_ids"),
    # a programme's campaigns are mastered on their own form and listed on
    # their own register (M35-campaigns, M35-calendar, programme column); the
    # programme form shows their count and budget roll-up. A read-only grid
    # here was tried: its save posts campaign_ids, which the programme form
    # may not write, and a new programme could not be saved (M35 pass 2 walk).
    ("fix.campaign.programme", "campaign_ids"),
}


def _forms():
    """[(js, screen_id, model, body)] for every A03 model_form."""
    out = []
    for js in sorted(SRC.glob("m*.js")):
        text = js.read_text(encoding="utf-8")
        starts = [(m.start(), m.group(1)) for m in SCREEN.finditer(text)]
        for i, (pos, sid) in enumerate(starts):
            end = starts[i + 1][0] if i + 1 < len(starts) else len(text)
            body = text[pos:end]
            if "kind: 'model_form'" not in body:
                continue
            m = MODEL.search(body)
            if m:
                out.append((js.name, sid, m.group(1), body))
    return out


# Odoo's mail/activity mixins add one2many fields to almost every model.
# They are chatter, not business content, and the workspace renders them
# through its own activity panel. Counting them made this test fire on 29
# forms, 25 of which were only "hiding" message_ids - noise that would have
# got the real finding ignored.
MIXIN = {
    "activity_ids",
    "message_ids",
    "message_follower_ids",
    "website_message_ids",
    "message_attachment_count",
    "rating_ids",
}


def _one2many(env, model):
    return {
        name: f
        for name, f in env[model]._fields.items()
        if f.type == "one2many"
        and name not in MIXIN
        # A COMPUTED, non-stored one2many has no inverse, and the grid writes
        # back through /p03/model/write - so it cannot carry one at all.
        # fix.complaint.evidence_ids is a computed one2many of fix.document;
        # having no grid there is correct (A03 audit, 2026-11-01).
        and not (f.compute and not f.store)
    }


def test_the_scan_finds_forms():
    """A guard on the guard: an empty list would pass everything below."""
    forms = _forms()
    assert len(forms) >= 50, "only %d A03 forms found - the scan broke" % len(forms)


def test_every_form_that_owns_children_displays_them(odoo_env):
    """The defect this file exists for."""
    hiding = []
    for js, sid, model, body in _forms():
        if model not in odoo_env:
            continue
        children = _one2many(odoo_env, model)
        constitutive = [n for n in children if (model, n) not in INCIDENTAL]
        if not constitutive:
            continue
        if "lines:" in body:
            continue
        # `grids: [{field, tab, ...}]` (several tabbed grids on one form, the
        # engine's 18 Nov 2026 form) displays the children it names.
        if "grids:" in body and all("field: '%s'" % n in body for n in constitutive):
            continue
        # A collection already displayed by another form on the same model in
        # the same module does not have to be repeated here - repeating it is
        # the duplication this estate forbids. M39-form-dunning is a
        # collections workflow; the subscription's IFRS 15 obligations belong
        # on M39-form-subscription, which shows them.
        shown_elsewhere = any(
            o_js == js and o_model == model and "lines:" in o_body
            for o_js, _o_sid, o_model, o_body in _forms()
        )
        if shown_elsewhere:
            continue
        hiding.append(
            "%s/%s (%s) owns %s and shows none of it"
            % (js, sid, model, ", ".join(sorted(constitutive)))
        )
    assert not hiding, (
        "%d A03 form(s) hide the records that constitute them:" % len(hiding)
        + "\n  "
        + "\n  ".join(hiding)
    )


def test_each_grid_names_a_real_one2many(odoo_env):
    """A grid pointed at a field that does not exist renders nothing, which
    looks exactly like the defect it was meant to fix."""
    bad = []
    for js, sid, model, body in _forms():
        m = re.search(r"lines:\s*\{[^}]*?field:\s*'([a-z0-9_]+)'", body, re.S)
        if not m:
            continue
        field = m.group(1)
        if model not in odoo_env:
            continue
        f = odoo_env[model]._fields.get(field)
        if f is None or f.type != "one2many":
            bad.append("%s/%s: lines.field='%s' is not a one2many on %s" % (js, sid, field, model))
    assert not bad, "\n  ".join(bad)


def test_each_grid_column_is_a_real_field_on_the_child(odoo_env):
    """A column naming a field the child model does not have is dropped
    silently by /p03/model/form, so the grid quietly loses a column."""
    bad = []
    for js, sid, model, body in _forms():
        m = re.search(r"lines:\s*\{(.*?)\n\s{2,8}\},", body, re.S)
        if not m or model not in odoo_env:
            continue
        chunk = m.group(1)
        fm = re.search(r"field:\s*'([a-z0-9_]+)'", chunk)
        if not fm:
            continue
        rel = odoo_env[model]._fields.get(fm.group(1))
        if rel is None or rel.type != "one2many":
            continue
        child = odoo_env[rel.comodel_name]
        for col in re.findall(r"\{\s*name:\s*'([a-z0-9_]+)'", chunk):
            if col not in child._fields:
                bad.append("%s/%s: column '%s' not on %s" % (js, sid, col, rel.comodel_name))
    assert not bad, "\n  ".join(bad)


def test_no_model_is_mastered_by_two_a03_modules():
    """Duplication between modules is out of scope for this estate.

    `fix.promotion` was bound by M11 and M38 with byte-identical columns. A
    module may offer a scoped VIEW of another's master (narrowed by a domain
    and not creatable); it may not carry a second master.
    """
    masters = {}
    offenders = []
    for js in sorted(SRC.glob("m*.js")):
        text = js.read_text(encoding="utf-8")
        starts = [(m.start(), m.group(1)) for m in SCREEN.finditer(text)]
        for i, (pos, sid) in enumerate(starts):
            end = starts[i + 1][0] if i + 1 < len(starts) else len(text)
            body = text[pos:end]
            if "kind: 'model_list'" not in body:
                continue
            m = MODEL.search(body)
            if not m:
                continue
            scoped = "domain:" in body or "create: false" in body
            if scoped:
                continue
            prev = masters.get(m.group(1))
            if prev and prev[0] != js.name:
                offenders.append(
                    "%s mastered by %s/%s and %s/%s" % (m.group(1), prev[0], prev[1], js.name, sid)
                )
            else:
                masters.setdefault(m.group(1), (js.name, sid))
    assert not offenders, "\n  ".join(offenders)


@pytest.mark.parametrize(
    "sid,field",
    [
        ("M27-form-call", "turn_ids"),
        ("M10-form-account", "ledger_ids"),
        ("M10-form-programme", "tier_ids"),
        ("M07-form-qbr", "action_ids"),
        ("M33-form-segment", "membership_ids"),
        ("M35-form-campaign", "response_ids"),
    ],
)
def test_named_forms_show_the_collection_that_defines_them(sid, field):
    """The ones where hiding the children made the screen meaningless.

    A conversation IS its turns; a loyalty account IS its points ledger; a
    QBR IS its agreed actions; a segment IS its members."""
    body = next((b for _js, s, _m, b in _forms() if s == sid), None)
    assert body, "%s not found" % sid
    assert "lines:" in body and field in body, "%s still does not display %s" % (sid, field)
