# cd_asset_workorder_spine — A07 P1 bridge (report §6 P1 "One work-order spine",
# "Event consumers"). A NEW module so that no existing A07 module gains a
# manifest dependency (a new dependency in an installed module kills the
# un-upgraded server on a plain restart: the P0 cd_vehicle_dispatch lesson).
{
    "name": "1000FiX Asset Work-Order Spine (A07 bridge)",
    "summary": "A07 P1: M45/M46/M47/M48 maintenance demand on the M47 work order; "
    "M01 preventive orders; M21 exit clearance against asset custody",
    "description": """
A07 P1 bridge (2026-11-04).

- One work-order spine: M45 PM and calibration due, M46 vehicle.service_due,
  M47 PM and M48 dispatched interventions all become fix.facility.work.order
  rows, which keep M47's lifecycle, DOFA spend approval, permit to work and
  branch verification. The WO carries its asset (equipment / vehicle / IoT
  device / prescriptive action) and its origin; verifying it completes its
  source through the source's own method (M46 PM, M45 PM, M47 PM; an M48
  action gets its evidence reference and waits for its outcome).
- fix.maintenance.demand: the ledger of every demand (one per source item,
  the idempotency key) and the queue of those that cannot be routed
  automatically (no site for the branch, no registered customer device...):
  a person completes the missing fact and routes it.
- M01: predictive_maintenance.wo_created / iot.action_dispatched on a
  customer-premises asset, and device.maintenance_due, raise a DRAFT
  fix.service.order (the M01 intake confirms it).
- M21: fix.hr.exit.action_clear refuses while the employee holds equipment
  custody, an open vehicle assignment or a vehicle as its assigned driver.
- M01/M09: the auto-invoice and the warranty claim refuse a device whose
  identity is provisional (fix.device.assert_identity_resolved).
- Wiring (FF-48): an M45 out-of-service hold raises its repair / calibration
  demand (dismissed when the item returns to service); a silent M48 stream
  raises an inspection; a reopened spine WO reopens its demand; an M45
  impact assessment flags the M01 orders behind the suspect uses for a
  quality re-check (fix.service.order.recheck) and records the disposition;
  an M48 intervention outcome becomes an M26 ground-truth row.
- Wiring round 2: a failed M46 pre-use check raises the vehicle's repair
  demand and a silent telematics device its inspection; an M17 lost/stolen
  flag puts a hold (fix.service.order.device.hold, with an activity for the
  branch) on every open M01 order of the device, and its clearance is
  recorded on the hold. No order state is changed.
""",
    "version": "19.0.0.3.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Facility & Branch Infrastructure",
    # Every dependency is installed on fix_dev and loads before this module.
    "depends": [
        "mail",
        "cd_event_outbox",
        "cd_facility",
        "cd_equipment_register",
        "cd_vehicle_ext",
        "cd_stream_registry",
        "cd_device_registry",
        "cd_service_order",
        "cd_hr_core",
        "cd_warranty_claims",
        "cd_billing_engine",
        # A07 P1 wiring: the M48 outcome feeds M26's model monitoring
        "cd_ml_services",
        # the stock lot of a fitted component (fix.device.component)
        "stock",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/fix_spine_rules.xml",
        "data/fix_event_consumers.xml",
        "data/fix_asset_alert_consumers.xml",
        "data/ir_cron.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "x_module_id": "A07-BRIDGE-S",
    "x_owner": "Facility & Branch Infrastructure",
}
