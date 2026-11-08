# cd_p03_portal — the Admin Operations Portal P03 (R1 OWL, PP2).
# The registry-driven workspace surface: no DOMAIN models of its own
# (AS-09 — it reads and navigates; the domain modules hold the data).
# Exception (R5, 2026-11-08): fix.report.subscription is platform
# infrastructure scheduling THIS module's own report packs — it lives here
# so delivery can never drift from the pack registry.
from . import controllers, models
