# cd_cx_feedback models.
# ruff: noqa: I001
# Import order is registration order, so it is NOT alphabetical: the survey
# designer extends fix.survey, and the complaint lifecycle, intake and
# concession files extend fix.complaint (and fix.cx.followup), so each comes
# after the file that defines the model it extends.
from . import fix_cx_feedback
from . import fix_cx_selfservice
from . import fix_survey_designer
from . import fix_complaint_lifecycle
from . import fix_complaint_intake
from . import fix_complaint_concession
from . import fix_complaint_party_merge

# M34 second pass: the maintained complaint taxonomy (extends fix.complaint).
from . import fix_complaint_taxonomy
