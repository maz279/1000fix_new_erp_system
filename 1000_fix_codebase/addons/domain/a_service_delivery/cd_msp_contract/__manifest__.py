# cd_msp_contract — M05 Remote Support & Managed Services (P08-M07).
{
    "name": "1000FiX Managed Services",
    "summary": "M05: MSP service model on the contract engine, monitored assets, alert-to-ticket automation, remote sessions, monthly service reports (CD-M05-nn)",
    "description": """
CD-M05-01 (P08-M07) — the managed-services business on M08's engine:

- fix.msp.contract — the MSP service model over fix.contract (per-device
  pricing, monitoring scope, SLA terms); M08 owns the contract spine
- fix.monitored.asset — client endpoints under management; the
  services/rmm-collector service ingests device telemetry (INT-029) and
  updates last_seen/health here
- fix.msp.alert — alerts from the collector; action creates a SERVICE
  ORDER (journey 6: alert -> ticket -> remote resolution -> SLA ->
  monthly report); acknowledged and resolved states
- fix.remote.session — MeshCentral/RustDesk session records (INT-028)
  with CONSENT captured (PDPA) and technician accountability
- fix.msp.service.report — the monthly client-facing report (bilingual,
  DE-17): uptime, alert volume, SLA attainment, resolutions
- monthly report generation is calendar-driven (journey 6 nightly)
""",
    "version": "19.0.0.1.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Service Delivery/MSP",
    "depends": ["base", "mail", "cd_entity_config", "cd_contract_core",
                 "cd_service_order", "cd_event_outbox"],
    "data": ["security/ir.model.access.csv", "views/fix_msp_views.xml"],
    "installable": True,
    "application": True,
    "x_cd_id": "CD-M05-01",
    "x_module_id": "M05",
    "x_wave": "W5",
    "x_owner": "Service Delivery",
    "x_category": "A_Service_Delivery_and_Operations",
    "x_tier": "T9",
}
