# cd_hse 19.0.0.4.0 — see pre-migrate.py.
#
#   * the investigator becomes the lead of the investigation team;
#   * a typed root cause becomes a root-cause row ("other");
#   * a typed corrective action becomes a CAPA row with its owner and due
#     date: VERIFIED when it had been verified (with who and when), DONE when
#     the incident had reached "action taken" or "closed", OPEN otherwise;
#     each is flagged `migrated`;
#   * every health record with a fitness decision publishes a fitness status,
#     WITHOUT its restriction text (it may name a diagnosis): Occupational
#     Health re-publishes the functional restriction.
from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    cr.execute("SELECT to_regclass('_a09_r2_hse_capa_legacy')")
    if cr.fetchone()[0]:
        cr.execute(
            "SELECT id, state, root_cause, corrective_action, capa_owner_id, capa_due_date, "
            "capa_verified_by_id, capa_verified_on, investigated_by_id "
            "FROM _a09_r2_hse_capa_legacy"
        )
        Member = env["fix.hse.investigation.member"]
        Cause = env["fix.hse.root.cause"]
        Capa = env["fix.hse.capa"]
        Users = env["res.users"]
        for (
            iid,
            state,
            root_cause,
            action,
            owner_id,
            due,
            verified_by,
            verified_on,
            investigator,
        ) in cr.fetchall():
            incident = env["fix.hse.incident"].browse(iid).exists()
            if not incident:
                continue
            lead = Users.browse(investigator).exists().employee_ids[:1] if investigator else None
            if lead and not Member.search_count([("incident_id", "=", iid)]):
                Member.create({"incident_id": iid, "employee_id": lead.id, "role": "lead"})
            if (root_cause or "").strip() and not Cause.search_count([("incident_id", "=", iid)]):
                Cause.create({"incident_id": iid, "category": "other", "description": root_cause})
            if (action or "").strip() and not Capa.search_count([("incident_id", "=", iid)]):
                vals = {
                    "incident_id": iid,
                    "name": action[:250],
                    "owner_id": owner_id or False,
                    "due_date": due or False,
                    "migrated": True,
                }
                if verified_by:
                    vals.update(
                        {
                            "state": "verified",
                            "verified_by_id": verified_by,
                            "verified_on": verified_on,
                            "verification_note": "Verified before round 2 (migrated).",
                        }
                    )
                elif state in ("action_taken", "closed"):
                    vals.update(
                        {"state": "done", "completion_note": "Recorded before round 2 (migrated)."}
                    )
                Capa.create(vals)
        cr.execute("DROP TABLE _a09_r2_hse_capa_legacy")

    Status = env["fix.hse.fitness.status"]
    mapping = {"fit": "fit", "fit_restricted": "restricted", "unfit": "unfit"}
    for health in env["fix.hse.health"].search(
        [("fitness", "in", list(mapping)), ("fitness_status_id", "=", False)],
        order="record_date, id",
    ):
        status = mapping[health.fitness]
        new = Status._fix_publish(
            health.employee_id,
            status,
            "Restriction on file with Occupational Health (to be re-published)"
            if status == "restricted"
            else False,
            health.record_date,
            health.valid_until,
            health=health,
        )
        new.write({"migrated": True})
        health.write({"fitness_status_id": new.id})
