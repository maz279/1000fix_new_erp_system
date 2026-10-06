# cd_contact_centre controllers — the P10 Agent Console API (PP5).
#
# Serves the W4 OpenAPI contract: /contact/conversations (the unified
# queue), /contact/conversations/detail (transcript + customer 360),
# /contact/handoff (claim / end / hand off), /contact/softphone (the
# integration seam — config from system parameters only).
from . import contact_api
