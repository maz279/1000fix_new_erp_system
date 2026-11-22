"""cd_metric_registry 19.0.0.4.0 - adopt the hand-made metric definitions.

A11 deep audit 2026-11-23 (A3-F01/A3-F04). The five governed definitions
(MET-WIP-AGE, MET-SLA-ATTAIN, MET-AR-OVERDUE, MET-BENCH-UTIL, MET-NPS) were
created BY HAND on the live and reference estates: the rows exist, but no
ir_model_data record points at them, so the module's own data file
(data/metric_definitions.xml) would create a SECOND row and die on the unique
(code, company_id) constraint.

This pre-migrate gives each such row the external id the data file expects, so
the load updates the existing row instead of duplicating it. It is idempotent
and never deletes: a code that is absent, ambiguous (two rows for one code) or
already linked is left exactly as it is - an ambiguous estate is a governance
problem for a person, not something a migration should guess at.
"""

import logging

_logger = logging.getLogger(__name__)

MODEL = "fix.metric.definition"

# xmlid (as written in data/metric_definitions.xml) -> metric code
ADOPT = {
    "metric_def_met_wip_age": "MET-WIP-AGE",
    "metric_def_met_sla_attain": "MET-SLA-ATTAIN",
    "metric_def_met_ar_overdue": "MET-AR-OVERDUE",
    "metric_def_met_bench_util": "MET-BENCH-UTIL",
    "metric_def_met_nps": "MET-NPS",
}


def migrate(cr, version):
    if not version:
        return
    cr.execute("SELECT to_regclass('fix_metric_definition'), to_regclass('ir_model_data')")
    if not all(cr.fetchone()):
        return
    for xmlid, code in ADOPT.items():
        cr.execute(
            "SELECT res_id FROM ir_model_data WHERE module='cd_metric_registry' AND name=%s",
            (xmlid,),
        )
        if cr.fetchone():
            continue  # already ours: nothing to adopt
        cr.execute("SELECT id, company_id FROM fix_metric_definition WHERE code=%s", (code,))
        rows = cr.fetchall()
        if len(rows) != 1:
            _logger.info(
                "cd_metric_registry 19.0.0.4.0: %s code %s has %d row(s) - not adopted",
                xmlid,
                code,
                len(rows),
            )
            continue
        res_id, _company_id = rows[0]
        # The live and reference rows sit in the impossible state this audit is
        # removing: state 'published' with no published version and no version at
        # all. Demote them BEFORE the data load: (a) the new
        # `_check_published_has_version` guard refuses a write to a published row
        # without a version, so the load would abort the upgrade; (b) a definition
        # nobody published through governance is not published. The definition
        # TEXT is untouched - only the claim.
        cr.execute(
            "SELECT current_version_id, state FROM fix_metric_definition WHERE id=%s",
            (res_id,),
        )
        version_id, state = cr.fetchone()
        if not version_id and state == "published":
            cr.execute(
                "UPDATE fix_metric_definition SET state='draft',"
                " write_date=now() AT TIME ZONE 'UTC' WHERE id=%s",
                (res_id,),
            )
            _logger.info(
                "cd_metric_registry 19.0.0.4.0: %s was 'published' with no version -"
                " demoted to draft (nothing published it through governance)",
                code,
            )
        cr.execute(
            "INSERT INTO ir_model_data (module, name, model, res_id, noupdate, create_date,"
            " write_date, create_uid, write_uid)"
            " VALUES ('cd_metric_registry', %s, %s, %s, true, now() AT TIME ZONE 'UTC',"
            " now() AT TIME ZONE 'UTC', 1, 1)",
            (xmlid, MODEL, res_id),
        )
        _logger.info(
            "cd_metric_registry 19.0.0.4.0: adopted existing %s (%s) as %s",
            code,
            res_id,
            xmlid,
        )
