# A10 deep audit (2026-11-22): map the content-loaded quality gates' legacy
# free-text stage to the enforceable checkpoint. The two live rows (QG-01
# "Job creation", QG-02 "Before customer handover") predate the field.

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
             WHERE checkpoint IS NULL
               AND lower(stage) LIKE %s
            """,
            (checkpoint, "%" + needle + "%"),
        )
    # anything still unassigned bites at the QC pass (the conservative
    # default for an unlabelled blocking gate)
    cr.execute(
        "UPDATE fix_qms_gate SET checkpoint = 'qc_pass' WHERE checkpoint IS NULL"
    )
