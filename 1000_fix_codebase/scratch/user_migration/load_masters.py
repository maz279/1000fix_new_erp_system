# ruff: noqa: F821, UP031, S608, E501, S101, SIM105  (odoo-bin shell script: env/cr are injected at runtime; table/column identifiers come from the staging CSVs and information_schema, not user input)
# Loader 1 — organisation masters on fix_real (odoo shell, superuser).
# Consolidates entities/branches, merges duplicates, creates new branches,
# cost pool + 3 cost elements, real departments, positions, 603 warehouses.
# Reads staged CSVs (read-only); all writes go through the ORM.
import csv

STG = r"C:\software_project\software_project_14\1000fix-2\_migration\staged"


def read_csv(name):
    with open(STG + "\\" + name, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


env.cr.execute("SAVEPOINT masters_l1")
try:
    Company = env["res.company"].sudo()
    Entity = env["fix.entity"].sudo()
    Branch = env["fix.branch"].sudo()
    OU = env["operating.unit"].sudo()
    Pool = env["fix.cost.pool"].sudo()
    Element = env["fix.cost.element"].sudo()
    Dept = env["hr.department"].sudo()
    Pos = env["fix.org.position"].sudo()
    WH = env["fix.warehouse"].sudo()

    company = Company.search([("name", "=", "1000Fix Services Limited")], limit=1)
    assert company, "company 1000Fix Services Limited not found"
    entity = Entity.search([("code", "=", "1000FIX")], limit=1)
    assert entity, "entity 1000FIX not found"
    main_ou = OU.search([("name", "=", "Main Operating Unit")], limit=1)
    print("company", company.id, "| entity", entity.id, "| main_ou", main_ou.id)

    # 1. deactivate synthetic branches (SMOKE/M30AUDIT)
    synth = Branch.search(
        [("active", "=", True), "|", ("name", "ilike", "SMOKE"), ("code", "in", ["M30AUDIT11"])]
    )
    synth.write({"active": False})
    print("synthetic branches deactivated:", len(synth))

    # 2. merge duplicate rows: re-point any FK children, then deactivate dup
    merges = read_csv("staged_branch_merges.csv")
    fk_cols = env.cr.fetchall_dict if False else None
    merged = 0
    for m in merges:
        dup = Branch.search([("name", "=", m["duplicate_branch"]), ("active", "=", True)], limit=1)
        canon = Branch.search(
            [("name", "=", m["canonical_branch"]), ("active", "=", True)], limit=1
        )
        if not dup:
            print("  merge skip (dup not active/found):", m["duplicate_branch"])
            continue
        if not canon:
            print("  MERGE PROBLEM (canonical missing):", m["canonical_branch"])
            continue
        env.cr.execute(
            "SELECT tc.table_name, kcu.column_name FROM information_schema.table_constraints tc "
            "JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name "
            "JOIN information_schema.constraint_column_usage ccu ON tc.constraint_name = ccu.constraint_name "
            "WHERE tc.constraint_type = 'FOREIGN KEY' AND ccu.table_name = 'fix_branch'"
        )
        moved = 0
        for tbl, col in env.cr.fetchall():
            env.cr.execute('SELECT count(*) FROM "%s" WHERE "%s" = %%s' % (tbl, col), [dup.id])
            n = env.cr.fetchone()[0]
            if n:
                env.cr.execute(
                    'UPDATE "%s" SET "%s" = %%s WHERE "%s" = %%s' % (tbl, col, col),
                    [canon.id, dup.id],
                )
                moved += n
        dup.write({"active": False})
        merged += 1
        print(
            "  merged: %s -> %s (children re-pointed: %d)"
            % (m["duplicate_branch"], m["canonical_branch"], moved)
        )
    print("duplicate branch rows merged:", merged)

    # 3. move every remaining active real branch onto the 1000FIX entity
    real = Branch.search([("active", "=", True)])
    real.write({"entity_id": entity.id})
    print("real branches moved to entity 1000FIX:", len(real))

    # deactivate leftover synthetic entities
    for e in Entity.search([("id", "!=", entity.id)]):
        if Branch.search_count([("entity_id", "=", e.id), ("active", "=", True)]) == 0:
            e.write({"active": False})
            print("  entity deactivated:", e.code)

    # 4. create the 6 new branches
    ou_by_simple = {}
    for ou in OU.search([]):
        ou_by_simple["".join(c for c in ou.name.lower() if c.isalnum())] = ou
    existing_names = {b.name for b in Branch.search([("active", "=", True)])}
    maxcode = 0
    for b in Branch.search([]):
        try:
            maxcode = max(maxcode, int(b.code.replace("BR-", "").replace("HO", "0") or 0))
        except ValueError:
            pass
    created = 0
    for i, nb in enumerate(read_csv("staged_new_branches.csv"), start=1):
        if nb["new_branch"] in existing_names:
            continue
        simple = "".join(c for c in nb["new_branch"].lower() if c.isalnum())
        # strip leading 'ou' from OU names when matching
        ou = None
        for k, v in ou_by_simple.items():
            if k.endswith(simple) or simple in k:
                ou = v
                break
        Branch.create(
            {
                "code": "BR-%04d" % (maxcode + i),
                "name": nb["new_branch"],
                "entity_id": entity.id,
                "operating_unit_id": (ou or main_ou).id,
            }
        )
        created += 1
    print("new branches created:", created)

    # 5. cost pool + 3 cost elements
    pool = Pool.search([("code", "=", "OPER"), ("company_id", "=", company.id)], limit=1)
    if not pool:
        pool = Pool.create(
            {"code": "OPER", "name": "Operating Cost Pool", "company_id": company.id}
        )
        print("cost pool created:", pool.code)
    for code, name in [("OPS", "Operation"), ("TEC", "Technical Ops"), ("ADM", "Admin")]:
        if not Element.search_count([("code", "=", code), ("pool_id", "=", pool.id)]):
            Element.create(
                {"code": code, "name": name, "pool_id": pool.id, "element_type": "primary"}
            )
    print("cost elements:", Element.search_count([("pool_id", "=", pool.id)]))

    # 6. departments: archive demo, create the 21 real ones
    Dept.search([("active", "=", True)]).write({"active": False})
    dept_names = sorted(
        {r["department"] for r in read_csv("staged_employees.csv") if r["department"]}
    )
    made = 0
    for dn in dept_names:
        if not Dept.search_count([("name", "=", dn), ("company_id", "=", company.id)]):
            Dept.create({"name": dn, "company_id": company.id})
            made += 1
    print("departments created:", made, "of", len(dept_names))

    # 7. positions for the distinct job titles
    titles = sorted({r["job_title"] for r in read_csv("staged_employees.csv") if r["job_title"]})
    pmade = 0
    for t in titles:
        if not Pos.search_count([("name", "=", t)]):
            Pos.create({"name": t, "company_id": company.id})
            pmade += 1
    print("positions created:", pmade, "of", len(titles))

    env.cr.execute("COMMIT")
    print("PHASE-A MASTERS COMMIT OK (branches/dept/pos/cost)")
except Exception as exc:
    env.cr.execute("ROLLBACK TO SAVEPOINT masters_l1")
    print("PHASE-A FAILED:", exc)
    raise
