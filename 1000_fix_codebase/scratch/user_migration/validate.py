# ruff: noqa: F821, UP031, S608, E501, S101, SIM105, E741  (odoo-bin shell script: env/cr are injected at runtime; table/column identifiers come from the staging CSVs and information_schema, not user input)
# Validation suite — asserts the migration end-state on fix_real (odoo shell).
import csv

STG = r"C:\software_project\software_project_14\1000fix-2\_migration\staged"


def read_csv(name):
    with open(STG + "\\" + name, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


Users = env["res.users"].sudo()
Emp = env["hr.employee"].sudo()
Branch = env["fix.branch"].sudo()
WH = env["fix.warehouse"].sudo()
Dept = env["hr.department"].sudo()
Pos = env["fix.org.position"].sudo()
Element = env["fix.cost.element"].sudo()
Req = env["fix.access.request"].sudo()
Asg = env["fix.role.assignment"].sudo()
Prov = env["auth.oauth.provider"].sudo()

staged = read_csv("staged_users.csv")
staged_emp = read_csv("staged_employees.csv")
real_logins = [r["login"] for r in staged]
ok = fail = 0


def check(name, cond, detail=""):
    global ok, fail
    if cond:
        ok += 1
        print("PASS", name, detail)
    else:
        fail += 1
        print("FAIL", name, detail)


# users
active = Users.search([("active", "=", True)])
active_logins = {u.login for u in active}
missing = [l for l in real_logins if l not in active_logins]
check("all 344 staged users active", len(missing) == 0, "missing: %s" % missing[:5])
synth_active = [u.login for u in active if u.login not in real_logins and u.login not in ("admin",)]
check("no synthetic users active", len(synth_active) == 0, str(synth_active[:5]))
check(
    "internal count = 341 (340 real + admin)",
    Users.search_count([("active", "=", True), ("share", "=", False)]) == 341,
)
check("portal count = 4", Users.search_count([("active", "=", True), ("share", "=", True)]) == 4)
dup_login = (
    env.cr.execute("SELECT login, count(*) FROM res_users GROUP BY login HAVING count(*) > 1") or []
)
rows_dup = env.cr.fetchall() if not dup_login else []
check("no duplicate logins", len(rows_dup) == 0, str(rows_dup[:3]))

# org defaults on users
ou_set = Users.search_count(
    [
        ("active", "=", True),
        ("default_operating_unit_id", "!=", False),
        ("login", "in", real_logins),
    ]
)
check("users with OU default >= 341", ou_set >= 341, str(ou_set))

# employees
check("active employees = 504", Emp.search_count([("active", "=", True)]) == 504)
with_branch = Emp.search_count([("active", "=", True), ("branch_id", "!=", False)])
check("employees with branch >= 502", with_branch >= 502, str(with_branch))
with_dept = Emp.search_count([("active", "=", True), ("department_id", "!=", False)])
check("employees with department >= 500", with_dept >= 500, str(with_dept))
linked = Emp.search_count([("active", "=", True), ("user_id", "!=", False)])
check("employees linked to users = 305", linked == 305, str(linked))
with_wh = Emp.search_count([("active", "=", True), ("default_warehouse_id", "!=", False)])
check("employees with default warehouse >= 250", with_wh >= 250, str(with_wh))
legacy_ou = Emp.search_count([("active", "=", True), ("legacy_operating_unit", "!=", False)])
check("employees with legacy service line >= 290", legacy_ou >= 290, str(legacy_ou))
mgr = Emp.search_count([("active", "=", True), ("parent_id", "!=", False)])
check("employees with manager = 242", mgr == 242, str(mgr))

# roles / governance
granted = Req.search_count([("state", "=", "granted"), ("user_id.login", "in", real_logins)])
check("granted access requests = 305", granted == 305, str(granted))
live_asg = Asg.search_count([("ended_on", "=", False), ("user_id.login", "in", real_logins)])
check("live role assignments = 305", live_asg == 305, str(live_asg))
base_g = env.ref("base.group_user").id
env.cr.execute(
    "SELECT count(DISTINCT u.id) FROM res_users u "
    "JOIN res_groups_users_rel rel ON rel.uid = u.id "
    "WHERE u.active AND rel.gid <> %s AND u.share = false AND u.id <> 2",
    [base_g],
)
role_group_users = env.cr.fetchone()[0]
check(
    "internal users holding role groups (beyond base) = 305",
    role_group_users == 305,
    str(role_group_users),
)

# masters
check(
    "active warehouses = 603",
    WH.search_count([("active", "=", True)]) == 603,
    str(WH.search_count([("active", "=", True)])),
)
wh_branch = WH.search_count([("active", "=", True), ("branch_id", "!=", False)])
check("warehouses with branch >= 595", wh_branch >= 595, str(wh_branch))
env.cr.execute(
    "SELECT name, count(*) FROM fix_branch WHERE active GROUP BY name HAVING count(*) > 1"
)
check("no active duplicate branch names", len(env.cr.fetchall()) == 0)
env.cr.execute(
    "SELECT count(*) FROM fix_branch fb JOIN fix_entity fe ON fe.id = fb.entity_id "
    "WHERE fb.active AND fe.code <> '1000FIX'"
)
check("all active branches on entity 1000FIX", env.cr.fetchone()[0] == 0)
check("21 active departments", Dept.search_count([("active", "=", True)]) == 21)
check("cost elements = 3", Element.search_count([]) == 3)
smoke_br = Branch.search_count([("active", "=", True), ("name", "ilike", "SMOKE")])
check("no SMOKE branches active", smoke_br == 0)

# oauth
prov = Prov.search([("client_id", "=", "odoo-erp"), ("enabled", "=", True)], limit=1)
check("SSO provider enabled", bool(prov), prov.name or "none")

print("VALIDATION SUMMARY: %d pass, %d fail" % (ok, fail))
