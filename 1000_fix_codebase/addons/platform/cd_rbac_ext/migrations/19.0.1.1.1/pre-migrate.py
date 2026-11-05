# A12 R1 deployment fix (2026-11-05) — pre-migrate 19.0.1.1.1.
#
# 19.0.1.1.0's identical fix only ran on databases whose installed version
# DIFFERED at upgrade time; databases that had already absorbed 19.0.1.0 ->
# 19.0.1.1.0 during the build (or fresh installs of 19.0.1.1.0 itself) sat at
# this version, so Odoo skipped the whole migration package on the next -u
# and the noupdate flag survived: the role -> permission-group map
# (data/fix_role_group_map.xml) was silently skipped again (R-13 / R-52
# stayed menu-only on fix_dev and fix_test). Bumping the version forces this
# package to run wherever 19.0.1.1.0 is installed; the SQL is idempotent and
# safe on fresh installs (noupdate is already false there).
def migrate(cr, version):
    cr.execute(
        "UPDATE ir_model_data SET noupdate = false "
        "WHERE module = 'cd_rbac_ext' AND model = 'fix.role'"
    )
