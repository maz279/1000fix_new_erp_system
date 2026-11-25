# cd_metric_registry models.
# fix_metric_registry first: fix_data_platform now extends fix.data.entity (the
# seed-integrity repair, A11 deep audit A3-F04), and an `_inherit` of a model
# that is not in the registry yet raises at import. The two base files have no
# class-level reference to each other.
# fix_m62_capture extends models from both other files: it is imported last.
# ruff: noqa: I001
from . import fix_metric_registry, fix_data_platform
from . import fix_m62_capture
