# cd_demand_plan 19.0.0.4.1 (A06 ERP audit M43-08): a service level is any
# percentage, not one of four choices. The selection columns ('90', '95', ...)
# become numbers in place, so every existing policy, target and van par keeps
# its level (the ORM would otherwise move the column aside and start empty).
from psycopg2 import sql

COLUMNS = (
    ("fix_demand_policy", "service_level_pct"),
    ("fix_demand_service_target", "target_pct"),
    ("fix_demand_van_par", "service_level_pct"),
)


def migrate(cr, version):
    if not version:
        return
    for table, column in COLUMNS:
        cr.execute(
            """
            SELECT data_type FROM information_schema.columns
             WHERE table_name = %s AND column_name = %s
            """,
            (table, column),
        )
        row = cr.fetchone()
        if not row or row[0] == "double precision":
            continue
        cr.execute(
            sql.SQL(
                "ALTER TABLE {t} ALTER COLUMN {c} TYPE double precision "
                "USING NULLIF(trim({c}), '')::double precision"
            ).format(t=sql.Identifier(table), c=sql.Identifier(column))
        )
