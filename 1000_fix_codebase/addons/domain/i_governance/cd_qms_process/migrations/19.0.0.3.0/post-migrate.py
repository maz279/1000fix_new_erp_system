# A10 deep audit (2026-11-22): map the content-loaded quality gates' legacy
# free-text stage to the enforceable checkpoint. The two live rows (QG-01
# "Job creation", QG-02 "Before customer handover") predate the field.
# The new column arrives with its default, so the mapping rewrites a row
# whose stage names a checkpoint — it never relies on a NULL first value.

_STAGE_TO_CHECKPOINT = [
    ("job creation", "job_creation"),
    ("intake", "job_creation"),
    ("handover", "qc_pass"),
    ("hand over", "qc_pass"),
    ("qc", "qc_pass"),
]


def migrate(cr, version):
    for needle, checkpoint in _STAGE_TO_CHECKPOINT:
        cr.execute(
            """
            UPDATE fix_qms_gate
               SET checkpoint = %s
             WHERE lower(stage) LIKE %s
               AND checkpoint IS DISTINCT FROM %s
            """,
            (checkpoint, "%" + needle + "%", checkpoint),
        )
