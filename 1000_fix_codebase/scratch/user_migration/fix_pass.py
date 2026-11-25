# ruff: noqa: F821, UP031, S608, E501, S101, SIM105  (odoo-bin shell script: env/cr are injected at runtime; table/column identifiers come from the staging CSVs and information_schema, not user input)
# Fix pass — residual issues from validation (odoo shell, superuser).
import csv

STG = r"C:\software_project\software_project_14\1000fix-2\_migration\staged"


def read_csv(name):
    with open(STG + "\\" + name, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


env.cr.execute("SAVEPOINT fixpass")
try:
    Branch = env["fix.branch"].sudo()
    Emp = env["hr.employee"].sudo()
    Users = env["res.users"].sudo()
    Req = env["fix.access.request"].sudo()

    # 1. same-name duplicate rows: keep one per name
    env.cr.execute("SELECT name FROM fix_branch WHERE active GROUP BY name HAVING count(*) > 1")
    for (name,) in env.cr.fetchall():
        rows = Branch.search([("name", "=", name), ("active", "=", True)], order="id")
        keep = rows[0]
        drop = rows[1:]
        # move any children off the dropped rows first
        for d in drop:
            env.cr.execute(
                "SELECT tc.table_name, kcu.column_name FROM information_schema.table_constraints tc "
                "JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name "
                "JOIN information_schema.constraint_column_usage ccu ON tc.constraint_name = ccu.constraint_name "
                "WHERE tc.constraint_type = 'FOREIGN KEY' AND ccu.table_name = 'fix_branch'"
            )
            for tbl, col in env.cr.fetchall():
                env.cr.execute('SELECT count(*) FROM "%s" WHERE "%s" = %%s' % (tbl, col), [d.id])
                if env.cr.fetchone()[0]:
                    env.cr.execute(
                        'UPDATE "%s" SET "%s" = %%s WHERE "%s" = %%s' % (tbl, col, col),
                        [keep.id, d.id],
                    )
        drop.write({"active": False})
        print("dup branch rows deactivated:", name, [d.code for d in drop])

    # 2. re-run manager links (verify persistence)
    by_code = {
        e.employee_code: e
        for e in Emp.search([("employee_code", "!=", False), ("active", "=", True)])
    }
    rows = read_csv("staged_employees.csv")
    linked = 0
    for r in rows:
        mc = r["manager_code"]
        if not mc:
            continue
        mgr = by_code.get(mc)
        if not mgr or not r["work_email"]:
            continue
        sub = Emp.search([("work_email", "=", r["work_email"]), ("active", "=", True)], limit=1)
        if sub and not sub.parent_id:
            sub.write({"parent_id": mgr.id})
            linked += 1
    env.cr.flush()
    n = Emp.search_count([("active", "=", True), ("parent_id", "!=", False)])
    print("manager links written:", linked, "| persisted count:", n)

    # 3. any real user whose grant is stuck in approved -> grant now
    staged = read_csv("staged_users.csv")
    real_logins = [r["login"] for r in staged if r["track"] == "internal" and r["role_code"]]
    stuck = Req.search(
        [("state", "in", ("approved", "submitted")), ("user_id.login", "in", real_logins)]
    )
    for req in stuck:
        try:
            if req.state == "submitted":
                req.action_approve()
            req.action_grant()
            print("grant completed:", req.name, req.user_id.login)
        except Exception as exc:
            print("grant failed:", req.name, req.user_id.login, str(exc)[:120])

    env.cr.execute("COMMIT")
    print("FIXPASS COMMIT OK")
except Exception as exc:
    env.cr.execute("ROLLBACK TO SAVEPOINT fixpass")
    print("FIXPASS FAILED:", exc)
    raise
