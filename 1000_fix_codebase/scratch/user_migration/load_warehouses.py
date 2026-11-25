# ruff: noqa: F821, UP031, S608, E501, S101, SIM105  (odoo-bin shell script: env/cr are injected at runtime; table/column identifiers come from the staging CSVs and information_schema, not user input)
# Loader 1b — 603 warehouses from warehouse.xlsx crosswalk (odoo shell, superuser).
import csv

STG = r"C:\software_project\software_project_14\1000fix-2\_migration\staged"


def read_csv(name):
    with open(STG + "\\" + name, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


env.cr.execute("SAVEPOINT masters_wh")
try:
    WH = env["fix.warehouse"].sudo()
    Branch = env["fix.branch"].sudo()
    OU = env["operating.unit"].sudo()
    company = env["res.company"].sudo().search([("name", "=", "1000Fix Services Limited")], limit=1)
    main_ou = OU.search([("name", "=", "Main Operating Unit")], limit=1)

    br_ids = {}
    for b in Branch.search([("active", "=", True)]):
        br_ids[b.name] = b.id

    existing = {w.code for w in WH.search([])}
    existing_names = {w.name for w in WH.search([])}
    rows = read_csv("staged_warehouses.csv")
    vals, skipped = [], 0
    for r in rows:
        if r["code"] in existing or r["name"] in existing_names:
            skipped += 1
            continue
        branch = br_ids.get(r["new_branch"])
        vals.append(
            {
                "code": r["code"],
                "name": r["name"],
                "company_id": company.id,
                "branch_id": branch or False,
                "operating_unit_id": (
                    Branch.browse(branch).operating_unit_id if branch else main_ou
                ).id,
            }
        )
    created = 0
    BATCH = 100
    for i in range(0, len(vals), BATCH):
        WH.create(vals[i : i + BATCH])
        created += len(vals[i : i + BATCH])
        env.cr.execute("SAVEPOINT masters_wh")
    print(
        "warehouses created:",
        created,
        "| skipped existing:",
        skipped,
        "| total now:",
        WH.search_count([]),
    )
    env.cr.execute("COMMIT")
    print("WAREHOUSES COMMIT OK")
except Exception as exc:
    env.cr.execute("ROLLBACK TO SAVEPOINT masters_wh")
    print("WAREHOUSES FAILED:", exc)
    raise
