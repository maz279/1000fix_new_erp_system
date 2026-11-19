# cd_qms_process — M23 Quality Management System (P08-M06).
{
    "name": "1000FiX Quality Management",
    "summary": "M23: NCR, root-cause/CAPA, internal audit programme (ISO 9001:2015), QC checklist takeover — closes the M31/M34/M42 -> M23 stubs (CD-M23-nn)",
    "description": """
CD-M23-01 (P08-M06) — the quality estate completes on the OCA
management-system patterns:

- fix.ncr — non-conformance records from ANY source (service order, QC
  checklist, complaint (M34 -> M23 STUB CLOSED), supplier (M42),
  internal audit); journey 14's middle
- fix.capa — root cause and CORRECTIVE/PREVENTIVE action with
  verification and closure; a CRITICAL NCR closes only through verified
  CAPA
- fix.qc.checklist EXTENSION — QC ownership transfers from M01 to M23
  (P08-M06-T04, AR-005 exactly-one-owner): the failed checklist now
  RAISES an NCR instead of a string; the M31 -> M23 stub closes
- fix.internal.audit — the ISO 9001:2015 audit programme (CON-11: zero
  major non-conformances traced to systems at surveillance); consumed
  by the P11 field-auditor surface (audit execution with offline
  capture fields)
- fix.complaint EXTENSION — the M34 -> M23 stubs close: ncr_stub_ref /
  capa_stub_ref become real relations; action_raise_ncr creates the NCR
""",
    "version": "19.0.0.2.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Quality/Management System",
    "depends": [
        "base",
        "mail",
        "cd_entity_config",
        "cd_event_outbox",
        "cd_service_order",
        "cd_cx_feedback",
        "cd_document_core",
        # A10 P1-6 (M23-8): fix.qms.review inherits fix.approvable.mixin —
        # the management review closure routes through M63 to Tier 5
        "cd_workflow_engine",
    ],
    "data": [
        "security/fix_isolation_rules.xml",
        "security/fix_qms_groups.xml",
        "security/ir.model.access.csv",
        "data/qms_ops_sequences.xml",
        # A10 S6 (M23-12): the M42 supplier-CAR hand-off — supplier.car.raised
        # arrives through the relay and raises the QMS NCR for majors.
        "data/fix_qms_consumers.xml",
        # M23 capture audit (2026-11-19): numbering of the new records
        "data/fix_qms_capture_data.xml",
        "views/fix_qms_views.xml",
    ],
    "installable": True,
    "application": True,
    "x_cd_id": "CD-M23-01",
    "x_module_id": "M23",
    "x_wave": "W5",
    "x_owner": "Quality",
    "x_category": "H_People_Payroll_and_Quality",
    "x_tier": "T8",
}
