# cd_itsm — M66 (P09).
{
    "name": "1000FiX Internal IT Service Management",
    "summary": "M66: Internal IT Service Management (CD-M66-01)",
    "description": """
CD-M66-01 (P09) — Internal IT Service Management.

Built on the existing estate (the layered model: compose, never
duplicate). AS-02 chatter + AS-03 company/OU on every transactional
model; AS-10 Monetary on every money field; events registered (AS-08).
""",
    "version": "19.0.0.3.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Internal IT Service Management",
    "depends": [
        "base",
        "mail",
        "cd_entity_config",
        "cd_msp_contract",
        "cd_event_outbox",
        # fix.project (cd_ppm) is referenced by this module's models; without the
        # dependency the relation can load against a missing model (FF-46).
        "cd_ppm",
        # A12 P1-1: fix.itsm.change inherits fix.approvable.mixin (M63), whose
        # home module must load first. Acyclic: cd_workflow_engine depends only
        # on base/mail/hr/cd_entity_config/cd_event_outbox/cd_rbac_ext.
        "cd_workflow_engine",
        # A12 finish M66-10: a retiring asset links its M06 certificate document.
        # Acyclic: cd_document_core does not depend on cd_itsm.
        "cd_document_core",
    ],
    "data": [
        "security/fix_isolation_rules.xml",
        # A12: roles first so the ACL rows below can reference them.
        "security/fix_itsm_a12_groups.xml",
        "security/ir.model.access.csv",
        # A12 finish M66: own-record rules for tickets and assets (spec s13).
        "security/fix_itsm_m66_rules.xml",
        "data/itsm_catalogue_sequences.xml",
        "data/integration_sequences.xml",
        "data/itsm_ops_sequences.xml",
        "data/itsm_core_sequences.xml",
        "data/fix_a12_crons.xml",
        # A12 finish: the M28 dispatcher, re-validation, feed, retention and expiry crons.
        "data/fix_a12_m28_crons.xml",
        # A12 D8: chatter relay for the events cd_itsm itself publishes.
        "data/fix_a12_event_consumers.xml",
        # A12 finish M66: the housekeeping, dead-letter, PIR, problem and licence crons.
        "data/fix_a12_m66_crons.xml",
        "views/cd_itsm_views.xml",
    ],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M66-01",
    "x_module_id": "M66",
    "x_wave": "W6",
    "x_owner": "Internal IT Service Management",
    "x_category": "Phase9",
    "x_tier": "T9",
}
