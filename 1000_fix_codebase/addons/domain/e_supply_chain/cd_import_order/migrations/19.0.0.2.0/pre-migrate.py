# cd_import_order 19.0.0.2.0 (A06 final pass): "By Weight" allocation was offered
# and always refused, because import lines carry no weight, and it is gone. A
# draft sheet holding it could never finalise; it now allocates by value.
def migrate(cr, version):
    if not version:
        return
    cr.execute(
        "UPDATE fix_import_landed SET allocation_method = 'value' "
        "WHERE allocation_method = 'weight' AND state = 'draft'"
    )
