"""A11 control suite — the cross-area exposure sweep, pinned to area a11.

The audit probe, kept as a regression test: for every model served on the
A11 P03 surfaces, as a plain internal user (base.group_user only) — can the
user write/create/unlink it, is it guarded, does its surface declare a
`writable` whitelist, and which workflow-looking fields are open. The suite
prints the sweep AND asserts the invariants the remediation established.
Rolled back by odoo_env.
"""

import importlib
import re

AREA = "a11"
area_mod = importlib.import_module("odoo.addons.cd_p03_portal.controllers.%s" % AREA)

WORKFLOW = re.compile(
    r"^(state|stage|status|.*_state|approved|.*_approved|approved_by.*|.*_approved_by|.*approver.*|"
    r"verified.*|.*_verified|.*_verified_by|certificate.*|.*_certified|signed.*|.*_signed|.*signature.*|"
    r"pod_.*|otp_.*|.*_otp|closed_.*|completed_.*|decided_.*|.*_override|is_warranty|warranty.*|"
    r"variance.*|.*_variance|counted.*|expected.*|refund.*|paid|is_paid|.*_paid|"
    r"released.*|.*_released|accepted.*|.*_accepted|awarded.*|.*_awarded|blacklist.*|.*_blacklisted|"
    r"qualified.*|.*_qualified|cleared.*|.*_cleared|posted.*|.*_posted|validated.*|.*_validated|"
    r"confirmed.*|.*_confirmed|locked.*|.*_locked|active)$"
)


def _module_of(model):
    for code, mod in area_mod.MODULES.items():
        if model in mod.SURFACES:
            return code
    return "?"


def test_area_exposure_sweep(odoo_env):
    env = odoo_env
    clerk = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "Sweep Clerk",
                "login": "sweep.%s@audit.test" % AREA,
                "group_ids": [(6, 0, [env.ref("base.group_user").id])],
            }
        )
    )
    cenv = env(user=clerk.id)
    rows, missing = [], []
    for model in sorted(area_mod.SURFACES):
        if model not in env:
            missing.append(model)
            continue
        M = cenv[model]
        guarded = hasattr(M, "_fix_guarded_fields")
        gfields = M.browse()._fix_guarded_fields() if guarded else set()
        wf = [
            n
            for n, f in M._fields.items()
            if WORKFLOW.match(n)
            and f.store
            and not f.compute
            and not f.related
            and f.type not in ("one2many", "many2many")
        ]
        open_fields = [n for n in wf if not M._fields[n].readonly and n not in gfields]
        ro_unguarded = [n for n in wf if M._fields[n].readonly and n not in gfields]
        surf = area_mod.SURFACES[model]
        rows.append(
            (
                _module_of(model),
                model,
                M.has_access("read"),
                M.has_access("write"),
                M.has_access("create"),
                M.has_access("unlink"),
                guarded,
                "writable" in surf,
                len(surf.get("actions", ())),
                sorted(open_fields),
                sorted(ro_unguarded),
            )
        )
    for r in rows:
        print(
            "ROW|%s|%s|read=%s|write=%s|create=%s|unlink=%s|guarded=%s|whitelist=%s|actions=%d|open=%s|ro_unguarded=%s"
            % r
        )
    for m in missing:
        print("MISSING_MODEL|%s" % m)
    exposed = [r for r in rows if r[3] and (r[9] or r[10])]
    print(
        "SUMMARY area=%s models=%d missing=%d clerk_can_write=%d clerk_can_unlink=%d guarded=%d "
        "with_writable_whitelist=%d exposed=%d"
        % (
            AREA,
            len(rows),
            len(missing),
            sum(1 for r in rows if r[3]),
            sum(1 for r in rows if r[5]),
            sum(1 for r in rows if r[6]),
            sum(1 for r in rows if r[7]),
            len(exposed),
        )
    )
    # ---- the pinned invariants (audit 2026-11-03: 18 writable, 13 exposed) --
    # Every surfaced model exists, and a plain internal user can NEVER unlink.
    assert not missing, "surfaced models missing from the registry: %s" % missing
    writable = {r[1] for r in rows if r[3]}
    assert all(not r[5] for r in rows), "a plain user can unlink: %s" % [r[1] for r in rows if r[5]]
    # The M63 rule book is closed (DoA administrator only); the two remaining
    # writable M63 models are the self-service ones the guards police
    # (substitution by the absent approver, task decisions by the assignee).
    # Data-ops and ML runtime rows stay writable for the operational flows;
    # their lifecycle rules are asserted by the M62/M26 control suites.
    assert writable == {
        "fix.approval.substitution",
        "fix.workflow.task",
        "fix.data.incident",
        "fix.data.pipeline",
        "fix.data.run",
        "fix.ml.inference.run",
        "fix.predictive.maintenance",
    }, "the plain-user writable set on A11 surfaces changed: %s" % sorted(writable)
    for model in ("fix.approval.substitution", "fix.workflow.task"):
        row = next(r for r in rows if r[1] == model)
        assert row[6], "%s keeps base write access, so it must stay guarded" % model
