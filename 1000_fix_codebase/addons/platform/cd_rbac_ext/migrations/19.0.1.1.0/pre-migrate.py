# A12 R1 (M29-1/13) — pre-migrate 19.0.1.1.0.
#
# The role register (data/fix_roles.xml) used to ship inside <odoo noupdate="1">,
# so every fix.role xmlid was stored with ir_model_data.noupdate = true. That
# flag silently SKIPPED the reviewed role -> permission-group mapping
# (data/fix_role_group_map.xml) on every module upgrade: the records there
# update the very same xmlids, and Odoo refuses to touch a noupdate xmlid from
# a data file during -u. The register is the reviewed baseline and must
# re-apply, so clear the flag BEFORE the module's data loads. Fresh installs
# get noupdate=0 straight from fix_roles.xml (the attribute was removed).
def migrate(cr, version):
    cr.execute(
        "UPDATE ir_model_data SET noupdate = false "
        "WHERE module = 'cd_rbac_ext' AND model = 'fix.role'"
    )
