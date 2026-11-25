# cd_fpa models.
# ruff: noqa: I001 - fix_fpa_capture extends fix.budget.version and
# fix.fpa.engine, so it is imported after the files that define them.
from . import (
    fix_board_pack,
    fix_fpa,
    fix_fpa_budget,
    fix_fpa_engine,
    fix_fpa_master,
    fix_fpa_reports,
)
from . import fix_fpa_capture
