# E28: DQ-PARTY-002 (critical completeness) targeted res.partner.mobile, a field
# this estate does not have, so the evaluator skipped it every day and a critical
# rule measured nothing. The contact number lives in `phone`. The evaluator's
# stale result is cleared so the screen does not show a skip for a rule that now
# runs.


def migrate(cr, version):
    cr.execute(
        """
        UPDATE fix_mdm_dq_rule
           SET field_name = 'phone',
               last_status = NULL,
               last_note = 'E28: re-pointed from the non-existent mobile field to phone.',
               last_run_at = NULL,
               last_violation_count = 0,
               last_records_checked = 0
         WHERE res_model = 'res.partner' AND field_name = 'mobile'
        """
    )
