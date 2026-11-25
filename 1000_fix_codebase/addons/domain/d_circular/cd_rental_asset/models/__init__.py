# cd_rental_asset models. fix_rental_capture (M13 capture pass 2, 2026-11-19)
# extends the models of fix_rental_asset and fix_rental_fleet: it must be
# imported after them, so this block is not sorted.
from . import fix_rental_approval, fix_rental_asset, fix_rental_fleet, rental_gl, rental_policy  # noqa: I001
from . import fix_rental_capture
