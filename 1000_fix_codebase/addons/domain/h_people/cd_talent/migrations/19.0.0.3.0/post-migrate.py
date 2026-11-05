# cd_talent 19.0.0.3.0 — see pre-migrate.py.
#
#   * each legacy interview with an interviewer becomes a one-panelist panel:
#     the lead interviewer's evaluation carries the typed score,
#     recommendation and notes, SUBMITTED when the round was completed;
#   * the coordinator's notes are cleared (they were evaluation notes);
#   * every interview's panel result is recomputed;
#   * a practical assessment's competency code is resolved to its M22
#     competency where one matches.
from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    cr.execute("SELECT to_regclass('_a09_r2_interview_legacy')")
    if cr.fetchone()[0]:
        cr.execute(
            "SELECT id, interviewer_id, score, recommendation, notes, state, company_id "
            "FROM _a09_r2_interview_legacy"
        )
        Evaluation = env["fix.talent.evaluation"]
        Interview = env["fix.talent.interview"]
        for iid, emp_id, score, rec, notes, state, company_id in cr.fetchall():
            interview = Interview.browse(iid).exists()
            if not interview or Evaluation.search_count([("interview_id", "=", iid)]):
                continue
            cr.execute(
                "INSERT INTO fix_talent_interview_panelist_rel (interview_id, employee_id) "
                "VALUES (%s, %s) ON CONFLICT DO NOTHING",
                (iid, emp_id),
            )
            vals = {
                "interview_id": iid,
                "panelist_id": emp_id,
                "company_id": company_id,
                "score": score or 0.0,
                "recommendation": rec or False,
                "notes": notes or False,
            }
            if state == "done" and rec:
                vals.update({"state": "submitted", "submitted_on": interview.completed_on})
            Evaluation.create(vals)
        cr.execute(
            "UPDATE fix_talent_interview SET notes = NULL "
            "WHERE id IN (SELECT id FROM _a09_r2_interview_legacy)"
        )
        cr.execute("DROP TABLE _a09_r2_interview_legacy")
    interviews = env["fix.talent.interview"].search([])
    for fname in ("panel_size", "panel_submitted", "panel_complete", "score", "recommendation"):
        env.add_to_compute(interviews._fields[fname], interviews)
    interviews.flush_model()
    # The candidate NID (A09 round 2, with the M21 residency move): every NID
    # gets its keyed hash; a hired candidate's clear NID is erased, since the
    # employee master holds it.
    from odoo.addons.cd_talent.models.fix_talent import nid_hash

    env["fix.candidate"]._fix_ensure_identity_hash_key()
    for cand in (
        env["fix.candidate"].with_context(active_test=False).search([("nid_number", "!=", False)])
    ):
        vals = {"nid_hash": nid_hash(env, cand.nid_number)}
        if cand.state == "hired" and cand.employee_id:
            vals["nid_number"] = False
        cand.write(vals)
    Competency = env["fix.competency"]
    for asmt in env["fix.talent.assessment"].search(
        [("competency_id", "=", False), ("competency_code", "!=", False)]
    ):
        comp = Competency.search(
            [
                ("code", "=", asmt.competency_code),
                ("company_id", "in", (asmt.company_id.id, False)),
            ],
            limit=1,
        )
        if comp:
            asmt.write({"competency_id": comp.id})
