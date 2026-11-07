# ruff: noqa: F821, UP031 - runs inside odoo-bin shell, which provides env
"""a12_finish_m64.py - make the M64 screens tell the truth (A12 finish).

Run inside `odoo-bin shell -c <conf> -d <db>` (superuser), after -u cd_mdm_core.
Idempotent. FIX_A12_M64_COMMIT=1 commits; otherwise it rolls back and reports.
The lead runs it on fix_dev after a rehearsal on a copy.

1. Rows that contradict the controls are moved to an honest state with a note.
   Nothing is back-dated and no approval is invented: a request that never had a
   payload is closed as having none, a pair whose references resolve to nothing
   is closed through the sanctioned action by a synthetic steward, labelled so.
2. Every workflow is walked once by synthetic role-holders, through the same
   methods the screens call, on SYNTHETIC parties and a SYNTHETIC code list, so a
   screen shows an applied change, a merged pair and a superseded version.
   Appointments here are synthetic (seed.*@1000fix.local): real stewards, domain
   owners and party stewards are a business decision (findings B1, B10).
"""

import json
import os

from odoo.exceptions import UserError, ValidationError

STEWARD = "cd_entity_config.group_mdm_domain_steward"
PARTY_STEWARD = "cd_party_master.group_party_data_steward"
NOTE = "A12 finish (M64) data repair: "
SYNTHETIC = "[SYNTHETIC M64 walk] "
report = {"repaired": [], "walked": [], "for_a_person": []}


def seed_user(login, name, *groups):
    Users = env["res.users"].with_context(no_reset_password=True, active_test=False)
    user = Users.search([("login", "=", login)], limit=1)
    wanted = [env.ref("base.group_user").id] + [env.ref(g).id for g in groups]
    if user:
        user.write({"active": True, "group_ids": [(4, g) for g in wanted]})
        return user
    return Users.create({"name": name, "login": login, "group_ids": [(6, 0, wanted)]})


steward_a = seed_user("seed.mdm.steward@1000fix.local", "Synthetic MDM Steward", STEWARD)
steward_b = seed_user("seed.mdm.steward2@1000fix.local", "Synthetic MDM Steward 2", STEWARD)
proposer = seed_user("seed.mdm.proposer@1000fix.local", "Synthetic MDM Proposer")
party_steward = seed_user(
    "seed.party.steward@1000fix.local", "Synthetic Party Data Steward", PARTY_STEWARD, STEWARD
)


def inbox(rec, user):
    return rec.sudo().approval_request_id.task_ids.filtered(
        lambda t: t.state == "pending" and t.assigned_user_id == user
    )


# ---- 1. rows that contradict the controls ---------------------------------

# Change requests: an open request that can never apply is closed as what it is.
Requests = env["fix.mdm.change.request"]
for cr in Requests.search([("state", "in", ("draft", "submitted", "under_review", "approved"))]):
    if cr.title.startswith(SYNTHETIC):
        continue
    why = None
    try:
        target = cr._target_record()
        changes = cr._proposed_values()
        cr._mdm_assert_governed(cr.model_name, changes, cr.reference)
        cr._mdm_assert_route(target, cr.reference)
    except (UserError, ValidationError) as exc:
        why = str(exc)
    if why or (cr.reference or "NEW") == "NEW":
        vals = {}
        if (cr.reference or "NEW") == "NEW":
            vals["reference"] = env["ir.sequence"].next_by_code("fix.mdm.change.request")
        if why:
            request = cr.approval_request_id
            if request and request.state == "pending":
                request._finish(
                    "voided", "voided", env.user, comment=NOTE + "no payload", record_state="none"
                )
            vals["state"] = "cancelled"
        cr._guarded().write(vals)
        cr.message_post(
            body=NOTE
            + (
                "closed: this request cannot apply and no value was ever changed by it (%s)." % why
                if why
                else "given a real reference; it carried the pre-sequence placeholder NEW."
            )
        )
        report["repaired"].append(
            "change request %s: %s" % (cr.id, "cancelled" if why else "numbered")
        )

# Steward requests: same rule, with the state this model has for a closed request.
Steward = env["fix.mdm.steward"]
for st in Steward.search([("state", "in", ("submitted", "in_review", "approved"))]):
    if st.reason.startswith(SYNTHETIC):
        continue
    why = None
    if st.request_type == "create":
        why = "a steward request cannot create a master record"
    else:
        try:
            st._mdm_assert_governed(st.res_model, (), st.name)
            st._target_record()
            if st.request_type == "update":
                st._proposed_values()
            if st.request_type == "merge":
                st._merge_survivor()
        except (UserError, ValidationError) as exc:
            why = str(exc)
    if why:
        request = st.approval_request_id
        if request and request.state == "pending":
            request._finish(
                "voided", "voided", env.user, comment=NOTE + why[:200], record_state="none"
            )
        was = st.state
        st._guarded().write({"state": "rejected", "decision_note": ("Data repair: " + why)[:250]})
        st.message_post(
            body=NOTE + "was %s; closed because it can never apply, and nothing was written "
            "to any master: %s" % (was, why)
        )
        report["repaired"].append("steward request %s: %s -> rejected" % (st.name, was))


# Duplicates: a decision nobody took, and pairs that resolve to nothing.
def pair_resolves(dup):
    model = env.get(dup.res_model)
    if model is None:
        return False
    for ref in (dup.record_a_ref, dup.record_b_ref):
        value = (ref or "").strip()
        if value.isdigit():
            found = model.browse(int(value)).exists()
        elif "ref" in model._fields:
            found = model.search([("ref", "=", value)], limit=1)
        elif "serial_number" in model._fields:
            found = model.search([("serial_number", "=", value)], limit=1)
        else:
            found = False
        if not found:
            return False
    return True


Duplicates = env["fix.mdm.duplicate"]
for dup in Duplicates.search([("decision", "!=", "pending"), ("decided_by_id", "=", False)]):
    was = dup.decision
    dup._guarded().write({"decision": "pending", "decided_on": False})
    dup.message_post(
        body=NOTE + "was %s with no recorded decider or date, so it is pending again: "
        "the decision cannot be attributed to anyone." % was
    )
    report["repaired"].append("duplicate %s: %s, no decider -> pending" % (dup.name, was))

for dup in Duplicates.search([("decision", "=", "pending"), ("party_merge_id", "in", (0, False))]):
    if not pair_resolves(dup):
        dup.with_user(steward_a).action_false_positive(
            note="Data repair by a synthetic steward: %s / %s resolve to no %s on this database."
            % (dup.record_a_ref, dup.record_b_ref, dup.res_model)
        )
        report["repaired"].append(
            "duplicate %s: refs resolve to nothing -> false positive" % dup.name
        )

# Code lists published with no publication date: the date was never recorded.
for lst in env["fix.mdm.code.list"].search(
    [("state", "=", "published"), ("published_on", "=", False)]
):
    day = lst.create_date.date()
    lst._guarded().write({"published_on": day, "effective_from": lst.effective_from or day})
    lst.message_post(
        body=NOTE + "its publication date was not recorded; the list's creation date %s stands "
        "in for it. Nothing about its values changed." % day
    )
    report["repaired"].append("code list %s: dated %s" % (lst.code, day))

# Domain register: the lead must hold the steward role. Live it was access.demo.
for card in env["fix.mdm.stewardship"].search([]):
    if not card.lead_steward_id.has_group(STEWARD):
        was = card.lead_steward_id.login
        card.write({"lead_steward_id": steward_a.id})
        card.message_post(
            body=NOTE + "lead was %s, who holds no steward role; a synthetic steward stands in "
            "until the business appoints one." % was
        )
        report["repaired"].append(
            "stewardship %s: lead %s -> %s" % (card.domain, was, steward_a.login)
        )
    if not card.owner_id:
        report["for_a_person"].append("stewardship %s has no business owner (B10)" % card.domain)

# A merge left in draft: it is routed for a decision, never executed here.
Merges = env.get("fix.party.merge")
for merge in Merges.search([("state", "=", "draft"), ("approval_state", "=", "none")]):
    try:
        with env.cr.savepoint():
            merge.with_user(steward_a).action_request_approval(
                justification="A12 finish data repair: this draft merge was never routed. "
                "A party data steward decides it from the inbox."
            )
        merge.message_post(body=NOTE + "routed for a decision; it has not been executed.")
        report["repaired"].append("party merge %s: routed, awaiting a decision" % merge.id)
    except (UserError, ValidationError) as exc:
        report["for_a_person"].append("party merge %s stays draft: %s" % (merge.id, exc))

# ---- 2. one honest walk of each workflow -----------------------------------

Partner = env["res.partner"]


def demo_partner(name, phone):
    partner = Partner.with_context(active_test=False).search([("name", "=", name)], limit=1)
    return partner or Partner.create({"name": name, "phone": phone})


# Change request: proposer -> submit -> route -> steward approves -> steward applies.
title = SYNTHETIC + "correct the phone of a synthetic party"
if not Requests.search_count([("title", "=", title)]):
    party = demo_partner(SYNTHETIC + "Party", "01700064001")
    cr = Requests.with_user(proposer).create(
        {
            "title": title,
            "description": "Synthetic walk of the sanctioned path, on a synthetic party.",
            "model_name": "res.partner",
            "record_id": party.id,
            "proposed_changes": "phone=01800064001",
        }
    )
    cr.with_user(proposer).action_submit()
    cr.with_user(proposer).action_request_approval(justification="Synthetic walk")
    inbox(cr, steward_a).with_user(steward_a).action_approve(comment="Synthetic walk")
    cr.with_user(steward_b).action_apply()
    report["walked"].append("change request %s: %s, %s" % (cr.reference, cr.state, party.phone))

# A second one left routed, so the inbox and the Impact field have something to show.
title = SYNTHETIC + "a request awaiting the steward's decision"
if not Requests.search_count([("title", "=", title)]):
    party = demo_partner(SYNTHETIC + "Party 2", "01700064002")
    cr = Requests.with_user(proposer).create(
        {
            "title": title,
            "description": "Synthetic: left pending in the steward's inbox.",
            "model_name": "res.partner",
            "record_id": party.id,
            "proposed_changes": json.dumps({"email": "synthetic.m64@1000fix.local"}),
        }
    )
    cr.with_user(proposer).action_submit()
    cr.with_user(proposer).action_request_approval(justification="Synthetic walk")
    report["walked"].append("change request %s: awaiting a decision" % cr.reference)

# Steward request: A raises, B reviews, A routes, B decides, B applies.
reason = SYNTHETIC + "deactivate a synthetic party"
if not Steward.search_count([("reason", "=", reason)]):
    party = demo_partner(SYNTHETIC + "Party to deactivate", "01700064003")
    st = Steward.with_user(steward_a).create(
        {
            "request_type": "deactivate",
            "res_model": "res.partner",
            "record_ref": str(party.id),
            "reason": reason,
        }
    )
    st.with_user(steward_b).action_review()
    st.with_user(steward_a).action_request_approval(justification="Synthetic walk")
    inbox(st, steward_b).with_user(steward_b).action_approve(comment="Synthetic walk")
    st.with_user(steward_b).action_apply()
    report["walked"].append(
        "steward request %s: %s, party active=%s" % (st.name, st.state, party.active)
    )

# Duplicate: a steward routes the merge; a party steward executes it from the inbox.
factors = SYNTHETIC.strip()
if not Duplicates.search_count([("match_factors", "=", factors)]):
    a = demo_partner(SYNTHETIC + "Duplicate A", "01700064004")
    b = demo_partner(SYNTHETIC + "Duplicate B", "01700064005")
    dup = Duplicates.with_user(steward_a).create(
        {
            "res_model": "res.partner",
            "record_a_ref": str(a.id),
            "record_b_ref": str(b.id),
            "match_factors": factors,
        }
    )
    dup.with_user(steward_a).action_merge(justification="Synthetic walk", survivor=str(a.id))
    merge = Merges.browse(dup.party_merge_id)
    inbox(merge, party_steward).with_user(party_steward).action_approve(comment="Synthetic walk")
    report["walked"].append(
        "duplicate %s: %s through M33 merge %s" % (dup.name, dup.decision, merge.id)
    )

# Code list: A builds, B publishes; A cuts version 2, B publishes it and v1 retires.
Lists = env["fix.mdm.code.list"]
code = "SEED-M64-DEMO"
if not Lists.search_count([("code", "=", code)]):
    v1 = Lists.with_user(steward_a).create(
        {"code": code, "name": SYNTHETIC + "demo list", "domain_area": "synthetic"}
    )
    env["fix.mdm.code.entry"].with_user(steward_a).create(
        {"list_id": v1.id, "value": "A", "label": "Alpha", "label_bn": "ক"}
    )
    v1.with_user(steward_b).action_publish()
    v2 = v1.with_user(steward_a).action_new_version()
    env["fix.mdm.code.entry"].with_user(steward_a).create(
        {"list_id": v2.id, "value": "B", "label": "Beta", "label_bn": "খ"}
    )
    v2.with_user(steward_b).action_publish()
    report["walked"].append(
        "code list %s: v%s %s, v%s %s" % (code, v1.version, v1.state, v2.version, v2.state)
    )

# Measured results: the same cron bodies the schedule runs.
env["fix.mdm.dq.rule"].cron_evaluate_dq_rules()
raised = env["fix.mdm.match.rule"].cron_detect_duplicates()
env["fix.mdm.stewardship"].cron_audit_data_quality()
report["walked"].append(
    "detection raised %s candidate pair(s); DQ rules and scorecards measured" % raised
)

for line in (
    "steward and party-steward appointments here are synthetic (B1)",
    "the governed register's contents are the lead's default, for the business to confirm (B4)",
):
    report["for_a_person"].append(line)

print(json.dumps(report, indent=2, default=str))
if os.environ.get("FIX_A12_M64_COMMIT") == "1":
    env.cr.commit()
    print("committed")
else:
    env.cr.rollback()
    print("rolled back: nothing changed (set FIX_A12_M64_COMMIT=1 to commit)")
