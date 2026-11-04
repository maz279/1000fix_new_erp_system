# cd_hse 19.0.0.4.0 — investigation and CAPA become child records (A09
# round 2, M59-F8), and the fitness status is split from the medical record.
#
# The incident's single root_cause / corrective_action / capa_owner_id /
# capa_due_date / capa_verified_by_id / capa_verified_on fields are removed
# from the model. Their values are kept aside here and turned into child rows
# in post-migrate.


def migrate(cr, version):
    cr.execute(
        """
        SELECT column_name FROM information_schema.columns
         WHERE table_name = 'fix_hse_incident'
           AND column_name IN ('root_cause', 'corrective_action', 'capa_owner_id',
                               'capa_due_date', 'capa_verified_by_id', 'capa_verified_on')
        """
    )
    if len(cr.fetchall()) < 6:
        return
    cr.execute(
        """
        CREATE TABLE IF NOT EXISTS _a09_r2_hse_capa_legacy AS
        SELECT id, state, root_cause, corrective_action, capa_owner_id, capa_due_date,
               capa_verified_by_id, capa_verified_on, investigated_by_id
          FROM fix_hse_incident
         WHERE root_cause IS NOT NULL OR corrective_action IS NOT NULL
            OR investigated_by_id IS NOT NULL
        """
    )
