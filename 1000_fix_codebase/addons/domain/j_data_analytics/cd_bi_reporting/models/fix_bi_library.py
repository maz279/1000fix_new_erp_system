# fix_bi_library - the canonical M25 report-key library (A1-F10, Nov 2026).
#
# The three key validators (distribution schedule, manual-pack replacement,
# report definition) used to import the PORTAL controller
# (cd_p03_portal.controllers.a11.m25) to learn the valid report keys — a
# domain addon reaching into a platform addon that its manifest does not
# depend on, and without the portal the schedule validator refused EVERY key
# while the manual-pack and alert validators silently SKIPPED. The library
# now lives here, in the module that owns the reports' subject matter; the
# controller imports it back and asserts its REPORTS dict is exactly this
# list, so the two can never drift.
#
# cd_bi_reporting depends on everything these packs read (orders, estimates,
# AR), so the keys are resolvable without the portal.

# Every pack the M25 surface serves (the controller's REPORTS dict, in no
# particular order). Keep in sync ONLY by editing this tuple — the
# controller's import-time assertion fails the request otherwise.
REPORT_LIBRARY_KEYS = (
    "weekly_exec_review",
    "commercial_board",
    "report_library",
    "executive_pack",
    "branch_league",
    "service_kpi_pack",
    "finance_pack",
    "people_pack",
    "export_catalog",
    "dataset_catalog",
)

# The standard library proper (FR-BID-011): the six canonical packs the
# library page lists — NOT the self-listing catalogues.
STANDARD_LIBRARY_KEYS = (
    "executive_pack",
    "branch_league",
    "service_kpi_pack",
    "finance_pack",
    "people_pack",
    "weekly_exec_review",
)


def valid_report_keys():
    """The report keys a schedule / replacement / definition may name, as
    module-prefixed strings. Always available — this is the domain module's
    own library, so an unknown key is REFUSED with this list, never skipped
    because 'the library is unavailable'."""
    return {"M25:%s" % key for key in REPORT_LIBRARY_KEYS}
