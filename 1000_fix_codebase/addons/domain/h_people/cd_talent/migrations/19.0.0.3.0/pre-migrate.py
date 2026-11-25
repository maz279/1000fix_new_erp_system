# cd_talent 19.0.0.3.0 — interview panels (A09 round 2, BRU-TAO-07).
#
# An interview's score, recommendation and notes were one evaluation typed by
# the recruiter. They become each panelist's own fix.talent.evaluation, and
# the interview's score and recommendation become the panel's consolidated
# (computed) result. The typed values are kept aside here and turned into the
# lead interviewer's evaluation in post-migrate.


def migrate(cr, version):
    cr.execute(
        """
        CREATE TABLE IF NOT EXISTS _a09_r2_interview_legacy AS
        SELECT id, interviewer_id, score, recommendation, notes, state, company_id
          FROM fix_talent_interview
         WHERE interviewer_id IS NOT NULL
        """
    )
