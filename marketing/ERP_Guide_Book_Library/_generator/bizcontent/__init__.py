# -*- coding: utf-8 -*-
"""
bizcontent — the authored half of the business-reader guide books.

Everything measurable comes out of the specification through `spec.Spec`.
Everything that has to be *written* — the narrative, the worked examples, the
day-in-the-life scenarios, the plain-English reading of each feature and each
rule — lives here, one module per file.

The split matters. If a figure changes in the specification the guide book
picks it up on the next build without anybody editing prose. If the *meaning*
of something changes, a person has to come here and say so, which is correct:
no generator should be inventing the sentence that explains what a quality gate
is for.

Each module file exposes a single dict named CONTENT. `require()` checks it
carries every key the builder will ask for, so a missing section fails at load
time with a useful message rather than three minutes into a build.
"""

import importlib

# Every key `bizbook.BusinessGuideBook` reads. Keys marked optional in the
# builder are not listed; anything here is mandatory.
REQUIRED = (
    "cover_line",
    "cover_inside",
    "about",
    "audience",
    "how_arranged",
    "parts_table",
    "reading_note",
    "appendix_note",
    "part1_blurb",
    "part2_blurb",
    "part3_blurb",
    "appendix_blurb",
    "part1_sections",
    "part2_sections",
    "part3_sections",
    "appendix_sections",
    "s15_lede",
    "s15_figures",
    "s15_never",
    "s15_where",
    "headline",
    "does",
    "does_not",
    "areas_map",
    "s1_lede",
    "s1_intro",
    "s1_problem",
    "s1_replaces",
    "s1_one_sentence",
    "s2_lede",
    "s2_intro",
    "s2_roles",
    "s3_lede",
    "s3_intro",
    "s3_shared_intro",
    "s3_shared",
    "s4k_title",
    "s4k_lede",
    "s4k_intro",
    "s4k_header",
    "s4k_table",
    "s4k_caption",
    "s4_lede",
    "s4_glossary",
    "s5_lede",
    "s5_intro",
    "areas",
    "s6_title",
    "s6_lede",
    "s6_intro",
    "s6_stages",
    "s6_gates_intro",
    "journey",
    "journey_title",
    "journey_sub",
    "journey_caption",
    "gates",
    "s7_lede",
    "s7_intro",
    "scenarios",
    "s9t_lede",
    "s9t_intro",
    "s9t_table",
    "s9t_close",
    "s17_lede",
    "s17_intro",
    "s17_plan",
    "s17_check_intro",
    "s17_checks",
    "s8_lede",
    "s8_intro",
    "s8_rules",
    "s9_lede",
    "s9_intro",
    "s9_table",
    "automation_groups",
    "s10_lede",
    "s10_intro",
    "s10_roles",
    "permissions",
    "s11_lede",
    "s11_intro",
    "s11_reports",
    "s11_kpis",
    "dials",
    "s12_lede",
    "s12_intro",
    "s12_upstream",
    "s12_downstream",
    "s13_lede",
    "s13_intro",
    "s13_troubleshooting",
    "s13_faq",
    "s14_lede",
    "s14_intro",
    "s14_benefits",
    "s14_soft",
    "s14_close",
    "change_control",
    "change_table",
    "change_note",
)

MODULES = {
    "M01": "m01",
    "M02": "m02",
    "M03": "m03",
    "M04": "m04",
    "M05": "m05",
    "M06": "m06",
    "M31": "m31",
}


def require(uid, content):
    """Fail loudly and early on an incomplete content pack."""
    missing = [k for k in REQUIRED if k not in content]
    if missing:
        raise KeyError(
            "%s content pack is missing %d key(s): %s"
            % (uid, len(missing), ", ".join(missing))
        )
    return content


def load(uid):
    """Return the validated CONTENT dict for a module id such as 'M01'."""
    mod = MODULES.get(uid)
    if not mod:
        raise KeyError("no business content pack registered for %s" % uid)
    m = importlib.import_module("bizcontent." + mod)
    return require(uid, m.CONTENT)
