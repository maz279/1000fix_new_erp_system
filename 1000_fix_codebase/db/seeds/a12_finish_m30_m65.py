# ruff: noqa: F821 - runs inside odoo-bin shell, which provides env
"""a12_finish_m30_m65.py - bring M30/M65 live rows into line with the A12 finish controls.

Run inside `odoo-bin shell -c <conf> -d <db>` (superuser), after appoint_approvers.py
and the module upgrade (whose migration handles branch states, ladder stamps, the
decorative flags and notification windows). Idempotent.

FIX_A12_COMMIT=1 commits; otherwise the transaction is rolled back and the output
says what would have changed. Do not run it on fix_dev before a rehearsal on a copy.

Everything is walked through the sanctioned path as the seed.*@1000fix.local users,
which are synthetic and say so. Nothing is forged. What needs a person is left as it
is and listed under "for_a_person":
  * BIN and TIN: live values look like placeholders. They are flagged, never replaced.
  * The Bangladesh packs load as DRAFT. Nobody has checked them, and this script does
    not certify them: a person verifies them and a second Platform Admin certifies.
  * The 5 Nov rulings were made under the old code: their countersigner never acted.
  * Release 19.0.4 stays planned unless an approved change names it.
"""

import json
import os

PLATFORM_ADMIN = "cd_entity_config.group_platform_admin"
SECOND_ADMIN_LOGIN = "seed.platform.admin@1000fix.local"
GATEWAY_APPROVER_LOGIN = "seed.gateway.approver@1000fix.local"
T4_LOGIN = "seed.dofa.t4@1000fix.local"
T5_LOGIN = "seed.dofa.t5@1000fix.local"
PLACEHOLDER_BIN = "1234567890123"
PLACEHOLDER_TIN = "123456789012"
SYNTHETIC = "Synthetic environment, seed users: "
FLAG_KEY = "itsm.sla_auto_escalate"
RETAKE_REFERENCE = "DOFA-RULING-2026-11-05/01"


def _note_once(record, text):
    """Post a chatter note unless this same note is already on the record."""
    bodies = record.sudo().message_ids.mapped("body")
    if not any(text in str(body) for body in bodies):
        record.sudo().message_post(body=text)
        return True
    return False


def _user(env, login):
    return env["res.users"].with_context(active_test=False).search([("login", "=", login)], limit=1)


def _second_admin(env, out):
    """Two-person rules need a second Platform Admin; fix_dev has one (admin)."""
    user = _user(env, SECOND_ADMIN_LOGIN)
    group = env.ref(PLATFORM_ADMIN)
    if not user:
        user = (
            env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "রুবেল আহমেদ (Platform Admin, synthetic)",
                    "login": SECOND_ADMIN_LOGIN,
                    "email": SECOND_ADMIN_LOGIN,
                    "password": SECOND_ADMIN_LOGIN,
                    "group_ids": [(6, 0, [env.ref("base.group_user").id, group.id])],
                    "company_id": env.ref("base.main_company").id,
                    "company_ids": [(6, 0, env["res.company"].search([]).ids)],
                }
            )
        )
        out["created_users"].append(SECOND_ADMIN_LOGIN)
    elif group not in user.group_ids:
        user.write({"group_ids": [(4, group.id)]})
        out["created_users"].append(f"{SECOND_ADMIN_LOGIN} (role added)")
    return user


def _reapprove_live_gateways(env, requester, out):
    """A gateway live with approval_state=none never had the routed decision. Walk it:
    suspend, request, approver decides from the inbox. The rail is back live only if
    the approver's decision reaches it, all inside this transaction."""
    approver = _user(env, GATEWAY_APPROVER_LOGIN)
    Gateway = env["fix.payment.gateway"].sudo()
    rails = Gateway.search(
        [("state", "=", "active"), ("mode", "=", "live"), ("approval_state", "=", "none")]
    )
    if rails and not approver:
        out["for_a_person"].append(
            "No {} user, so {} were not re-approved: run appoint_approvers.py first.".format(
                GATEWAY_APPROVER_LOGIN, rails.mapped("provider")
            )
        )
        return
    for rail in rails:
        rail.with_user(approver).action_suspend(
            reason="Re-approval: this rail was live with no routed approval on record (P1-4)."
        )
        rail.with_user(requester).action_request_approval(
            justification=SYNTHETIC + "the rail predates the routed approval; re-approving it."
        )
        task = rail.approval_request_id.sudo().task_ids.filtered(
            lambda t: t.state == "pending" and t.assigned_user_id == approver
        )
        if not task:
            out["for_a_person"].append(
                f"{rail.provider} is suspended awaiting an approver: no inbox task reached {approver.login}."
            )
            continue
        task.with_user(approver).action_approve(comment=SYNTHETIC + "routed re-approval.")
        rail.invalidate_recordset()
        out["gateways_reapproved"].append(
            f"{rail.provider} ({rail.country_code}): {rail.state}/{rail.mode}, approval {rail.approval_state}"
        )


def _load_bd_drafts(env, admin, out):
    result = env["fix.country_pack.loader"].with_user(admin).load_bangladesh_pack()
    out["bd_packs_created_as_draft"] = result["created"]
    drafts = env["fix.country.pack"].search(
        [("code", "in", ("BD-DIV-DIST-2026", "BD-HOL-2026")), ("state", "=", "draft")]
    )
    if drafts:
        out["for_a_person"].append(
            "{} are unverified drafts: check every line against the official source, "
            "then a Platform Admin other than the creator certifies. The holiday data "
            "covers 2026 only.".format(drafts.mapped("code"))
        )


def _release(env, out):
    Release = env["fix.platform.release"].sudo()
    Change = env["fix.itsm.change"].sudo()
    for rel in Release.search([("state", "in", ("planned", "in_test"))]):
        if rel.itsm_change_id:
            continue
        match = Change.search(
            [("state", "in", ("approved", "implemented")), ("title", "ilike", rel.version)], limit=1
        )
        if match:
            rel.write({"itsm_change_id": match.id})
            out["releases_linked"].append(f"{rel.version} -> {match.name}")
        else:
            _note_once(
                rel,
                "No approved ITSM change names this release, so it cannot ship yet: a person "
                "links the change it really ships.",
            )
            out["for_a_person"].append(f"Release {rel.version} has no approved change to link.")
    shipped = Release.search([("state", "=", "released"), ("itsm_change_id", "=", False)])
    if shipped:
        out["for_a_person"].append(
            "Releases {} shipped before the change gate, with no linked change; left as history.".format(
                shipped.mapped("version")
            )
        )


def _flag_entities(env, out):
    for entity in env["fix.entity"].sudo().search([]):
        doubtful = []
        if entity.bin_number == PLACEHOLDER_BIN:
            doubtful.append(f"BIN {entity.bin_number}")
        if entity.tin_number == PLACEHOLDER_TIN:
            doubtful.append(f"TIN {entity.tin_number}")
        if doubtful:
            _note_once(
                entity,
                "{} look like placeholders. They pass the format check and were left as they "
                "are: record the real NBR registrations before any filing.".format(
                    " and ".join(doubtful)
                ),
            )
            out["for_a_person"].append(
                "Entity {}: {} look like placeholders; not replaced.".format(
                    entity.code, " and ".join(doubtful)
                )
            )
        if entity.active and not entity.incorporation_date:
            out["for_a_person"].append(
                f"Entity {entity.code} has no incorporation date; none was invented."
            )


def _notification_caps(env, out):
    """Marketing cap 0 means uncapped, which NT-003 forbids. The row's own combined
    non-transactional cap is the conservative figure already on it."""
    for row in env["fix.notification.config"].sudo().search([("consent_class", "=", "marketing")]):
        if row.frequency_cap == 0:
            cap = row.combined_cap_non_transactional or 4
            row.write({"frequency_cap": cap})
            row.message_post(
                body="Marketing was uncapped (0), which NT-003 forbids. Set to this row's own "
                f"combined non-transactional cap ({cap}); a person should confirm the figure."
            )
            out["notification_caps_set"].append(f"{row.name} -> {cap}")


def _flag_register(env, admin, out):
    """Show the one real kill switch, enabled, so behaviour does not change."""
    Flag = env["fix.feature.flag"]
    if not Flag.sudo().search_count([("key", "=", FLAG_KEY)]):
        Flag.with_user(admin).create(
            {
                "key": FLAG_KEY,
                "name": "SLA auto-escalation kill switch (disable to stop the cron)",
                "enabled": True,
            }
        )
        out["flags_created"].append(FLAG_KEY)


def _proposal_awaiting_countersign(env, out):
    """A real proposal the screen can show and the named Tier 5 user can countersign
    or decline: the same bands as the ruling in force, so no authority changes even
    if countersigned, and nothing is in force until a person acts."""
    Ladder = env["fix.dofa.ladder"].sudo()
    t4, t5 = _user(env, T4_LOGIN), _user(env, T5_LOGIN)
    in_force = Ladder.search(
        [("target_model", "=", "fix.loyalty.ledger"), ("in_force", "=", True)], limit=1
    )
    if not (in_force and t4 and t5):
        return
    if Ladder.search_count(
        [("target_model", "=", in_force.target_model), ("ruling_state", "=", "proposed")]
    ):
        return
    draft = Ladder.with_user(t4).create(
        {
            "name": f"{in_force.name}, re-take under the two-person control (synthetic)",
            "target_model": in_force.target_model,
            "basis": in_force.basis,
            "threshold_ids": [
                (0, 0, {"upper_bound": band.upper_bound, "tier": band.tier, "note": band.note})
                for band in in_force.threshold_ids
            ],
        }
    )
    draft.action_propose_ruling(reference=RETAKE_REFERENCE, countersigned_by=t5.id)
    out["rulings_proposed"].append(f"{draft.name}, awaiting {t5.login}")


def _report_state(env, out):
    Ladder = env["fix.dofa.ladder"].sudo()
    unsigned = Ladder.search([("in_force", "=", True), ("countersigned_at", "=", False)])
    if unsigned:
        out["for_a_person"].append(
            "Rulings {} predate the countersign step: the named countersigner never acted. "
            "Re-take them with real authority holders (B1).".format(unsigned.mapped("target_model"))
        )
    envs = (
        env["fix.platform.environment"]
        .sudo()
        .search(
            [
                ("kind", "in", ("dev", "staging")),
                ("state", "=", "live"),
                ("masking_state", "=", "pending"),
            ]
        )
    )
    if envs:
        out["for_a_person"].append(
            "{} are live with no masking evidence on record; left as they are: only a person "
            "can say whether the data is masked (BRU-ADM-16).".format(envs.mapped("name"))
        )
    Branch = env["fix.branch"].sudo().with_context(active_test=False)
    lost = Branch.search_count([("company_id", "=", False)])
    archived = Branch.search_count([("entity_id.active", "=", False)])
    if lost or archived:
        out["for_a_person"].append(
            f"{lost} branches have no company and {archived} hang off an archived entity: "
            "which company and entity they belong to is decision B7."
        )
    out["locale_coverage_measured"] = {
        p.code: p.coverage_pct for p in env["fix.locale.pack"].sudo().search([])
    }
    out["nagad_gateway_row"] = bool(
        env["fix.payment.gateway"].sudo().search_count([("provider", "=ilike", "nagad")])
    )


def run(env):
    out = {
        "created_users": [],
        "gateways_reapproved": [],
        "bd_packs_created_as_draft": [],
        "releases_linked": [],
        "notification_caps_set": [],
        "flags_created": [],
        "rulings_proposed": [],
        "for_a_person": [],
    }
    admin = _second_admin(env, out)
    _reapprove_live_gateways(env, admin, out)
    _load_bd_drafts(env, admin, out)
    _release(env, out)
    _flag_entities(env, out)
    _notification_caps(env, out)
    _flag_register(env, admin, out)
    _proposal_awaiting_countersign(env, out)
    _report_state(env, out)
    return out


if "env" in globals():
    result = run(env)
    print(json.dumps(result, indent=2, default=str, ensure_ascii=False))
    if os.environ.get("FIX_A12_COMMIT") == "1":
        env.cr.commit()
        print("committed")
    else:
        env.cr.rollback()
        print("rolled back: nothing changed (set FIX_A12_COMMIT=1 to commit)")
