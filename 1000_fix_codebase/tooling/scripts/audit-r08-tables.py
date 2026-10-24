"""PostgreSQL 17 schema audit for R08-M03 models."""

import os

import psycopg2


def main():
    conn = psycopg2.connect(
        dbname="fix_dev",
        user="fix",
        # dev DB credential from .env (POSTGRES_PASSWORD); default = .env.example dev value
        password=os.environ.get("POSTGRES_PASSWORD", "change-me-dev-only"),
        host="127.0.0.1",
        port=5433,
    )
    cur = conn.cursor()
    tables = [
        "fix_storefront_cart",
        "fix_storefront_order",
        "fix_storefront_return",
        "fix_dynamic_price_rule",
        "fix_price_explanation",
        "fix_site",
        "fix_facility_work_order",
        "fix_project",
        "fix_project_milestone",
        "fix_project_task",
    ]
    print("PostgreSQL 17 Database Table Schema Audit:")
    all_ok = True
    for t in tables:
        cur.execute("SELECT 1 FROM information_schema.tables WHERE table_name = %s", (t,))
        exists = cur.fetchone() is not None
        rows = 0
        if exists:
            cur.execute(f"SELECT COUNT(1) FROM {t}")
            rows = cur.fetchone()[0]
        else:
            all_ok = False
        print(f" - {t:30}: exists={exists} (rows: {rows})")
    conn.close()
    if all_ok:
        print("\nALL R08-M03 POSTGRESQL 17 TABLES VERIFIED AND ACTIVE!")
    else:
        print("\nSOME TABLES ARE MISSING!")


if __name__ == "__main__":
    main()
