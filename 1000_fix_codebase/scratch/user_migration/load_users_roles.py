# ruff: noqa: F821, UP031, S608, E501, S101, SIM105  (odoo-bin shell script: env/cr are injected at runtime; table/column identifiers come from the staging CSVs and information_schema, not user input)
# Loader 3 — 344 users + employee links + org defaults + role grants
# through the estate's own access-request chain (odoo shell, superuser).
import csv
import re

STG = r"C:\software_project\software_project_14\1000fix-2\_migration\staged"


def read_csv(name):
    with open(STG + "\\" + name, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


env.cr.execute("SAVEPOINT users_l3")
try:
    Users = env["res.users"].sudo()
    Emp = env["hr.employee"].sudo()
    Branch = env["fix.branch"].sudo()
    WH = env["fix.warehouse"].sudo()
    Role = env["fix.role"].sudo()
    Req = env["fix.access.request"].sudo()
    admin = Users.browse(2)

    internal_group = env.ref("base.group_user")
    portal_group = env.ref("base.group_portal")

    br = {b.name: b for b in Branch.search([("active", "=", True)])}
    wh = {w.name: w for w in WH.search([])}
    roles = {r.code: r for r in Role.search([])}
    rows = read_csv("staged_users.csv")

    # ---- create users
    created = portal_n = 0
    failures = []
    for r in rows:
        if Users.search_count([("login", "=", r["login"])]):
            continue
        groups = portal_group if r["track"] == "portal" else internal_group
        clean_name = re.sub(r"^\(\s*\d+\s*\)\s*", "", r["name"] or "").strip()
        vals = {
            "name": clean_name or r["login"],
            "login": r["login"],
            "email": r["login"],
            "tz": "Asia/Dhaka",
            "lang": "en_US",
            "group_ids": [(6, 0, [groups.id])],
        }
        try:
            Users.create(vals)
            created += 1
            if r["track"] == "portal":
                portal_n += 1
        except Exception as exc:
            failures.append((r["login"], str(exc)[:120]))
    print("users created:", created, "(portal", portal_n, ") failures:", len(failures))
    for f in failures[:10]:
        print("  FAIL:", f)

    # ---- link employees + org defaults
    linked = defaults = 0
    for r in rows:
        user = Users.search([("login", "=", r["login"])], limit=1)
        if not user:
            continue
        emp = False
        if r["employee_email"]:
            emp = Emp.search([("work_email", "=", r["employee_email"])], limit=1)
        if emp and not emp.user_id:
            emp.write({"user_id": user.id})
            linked += 1
        ev = {}
        if r["legacy_ou"]:
            ev["legacy_operating_unit"] = r["legacy_ou"]
        if r["cost_center"]:
            ev["fix_cost_centre"] = r["cost_center"]
        if r["legacy_branch"]:
            ev["legacy_branch_name"] = r["legacy_branch"]
        if r["default_warehouse"] and r["default_warehouse"] in wh:
            ev["default_warehouse_id"] = wh[r["default_warehouse"]].id
        elif emp and emp.default_warehouse_id:
            pass  # keep whatever the employee already carries
        if r["legacy_branch"] and not r["default_warehouse"]:
            # gap policy: default to the branch's warranty warehouse if one exists
            b = br.get(r["new_branch"])
            if b:
                cand = WH.search(
                    [("branch_id", "=", b.id), ("name", "ilike", "Warranty%")], limit=1
                )
                if cand:
                    ev["default_warehouse_id"] = cand.id
        if emp and ev:
            emp.write(ev)
        if emp and emp.branch_id and emp.branch_id.operating_unit_id:
            user.write({"default_operating_unit_id": emp.branch_id.operating_unit_id.id})
            defaults += 1
        elif r["new_branch"] in br:
            user.write({"default_operating_unit_id": br[r["new_branch"]].operating_unit_id.id})
            defaults += 1
    print("employee links:", linked, "| users with OU default:", defaults)

    # ---- role grants through the access-request chain
    granted = blocked = norole = 0
    for r in rows:
        if r["track"] != "internal" or not r["role_code"]:
            norole += 1
            continue
        user = Users.search([("login", "=", r["login"])], limit=1)
        role = roles.get(r["role_code"])
        if not user or not role:
            norole += 1
            continue
        reason = (
            "Initial take-on from legacy job title '%s' (user migration crosswalk v1, 2026-11-09)"
            % (r["employee_code"] or r["name"])
        )
        try:
            req = Req.create(
                {
                    "request_type": "grant",
                    "user_id": user.id,
                    "role_id": role.id,
                    "reason": reason,
                    "requested_by_id": admin.id,
                    "state": "submitted",
                }
            )
            req.action_approve()
            req.action_grant()
            granted += 1
        except Exception as exc:
            blocked += 1
            if blocked <= 10:
                print("  GRANT BLOCKED %s/%s: %s" % (r["login"], r["role_code"], str(exc)[:140]))
    print("role grants:", granted, "| blocked:", blocked, "| no role (portal/unmapped):", norole)
    env.cr.execute("COMMIT")
    print("USERS+ROLES COMMIT OK")
except Exception as exc:
    env.cr.execute("ROLLBACK TO SAVEPOINT users_l3")
    print("USERS FAILED:", exc)
    raise
