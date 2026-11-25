# ruff: noqa: F821, UP031, S608, E501, S101, SIM105  (odoo-bin shell script: env/cr are injected at runtime; table/column identifiers come from the staging CSVs and information_schema, not user input)
# Loader 4 — synthetic decommission on fix_real (odoo shell, superuser).
# Deactivates (never deletes) every synthetic user/employee/master that is
# not part of the real take-on; keeps Odoo core identities (admin, system,
# public template). Password login for real users stays untouched.
import csv

STG = r"C:\software_project\software_project_14\1000fix-2\_migration\staged"


def read_csv(name):
    with open(STG + "\\" + name, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


env.cr.execute("SAVEPOINT purge_l4")
try:
    Users = env["res.users"].sudo()
    Emp = env["hr.employee"].sudo()
    WH = env["fix.warehouse"].sudo()

    real_logins = {r["login"] for r in read_csv("staged_users.csv")}
    real_emails = {r["work_email"] for r in read_csv("staged_employees.csv") if r["work_email"]}
    core = {"__system__", "admin", "public", "portaltemplate"}

    # 1. synthetic users: not real, not core -> strip groups + deactivate + archive partner
    synth = Users.search([("active", "=", True), ("login", "not in", list(real_logins | core))])
    stripped = 0
    for u in synth:
        if u.group_ids:
            u.write({"group_ids": [(5, 0, 0)]})
            stripped += 1
    synth.write({"active": False})
    partners = synth.mapped("partner_id").filtered(lambda p: p.active)
    partners.write({"active": False}) if partners else None
    print("synthetic users deactivated:", len(synth), "| groups stripped:", stripped)

    # demo/portal template logins go off too (documented in the plan)
    for login in ("demo", "portal"):
        u = Users.search([("login", "=", login)], limit=1)
        if u and u.active:
            u.write({"active": False})
            print("  core-demo deactivated:", login)

    # 2. synthetic employees (52 seed names) -> archive
    syn_emp = Emp.search([("active", "=", True), ("work_email", "not in", list(real_emails))])
    # keep any real employee that has no email but a legacy branch label (take-on rows)
    syn_emp = syn_emp.filtered(lambda e: not e.legacy_branch_name)
    syn_emp.write({"active": False})
    print("synthetic employees archived:", len(syn_emp))

    # 3. seed warehouse off
    for w in WH.search([("code", "in", ["SEED-WH-", "SEED-WH"])]):
        w.write({"active": False})
        print("  seed warehouse deactivated:", w.name)

    # 4. final census
    active_internal = Users.search_count([("active", "=", True), ("share", "=", False)])
    active_portal = Users.search_count([("active", "=", True), ("share", "=", True)])
    print(
        "ACTIVE CENSUS: internal %d, portal %d, employees %d"
        % (active_internal, active_portal, Emp.search_count([("active", "=", True)]))
    )
    env.cr.execute("COMMIT")
    print("PURGE COMMIT OK")
except Exception as exc:
    env.cr.execute("ROLLBACK TO SAVEPOINT purge_l4")
    print("PURGE FAILED:", exc)
    raise
