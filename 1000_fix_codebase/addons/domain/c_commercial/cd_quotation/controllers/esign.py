# The e-signature provider's completion callback for M36 quotations.
#
# A04 workflow audit (2026-11-03, M36-1): esign_state was a field a clerk set
# to 'signed'. A signature now arrives only from the provider, which signs
# its callback with the shared secret in `cd_quotation.esign_provider_secret`
# (HMAC-SHA256 over the quotation number, version, value and its signature
# reference). No secret configured = no e-signature acceptance at all.
from odoo import http
from odoo.exceptions import UserError, ValidationError
from odoo.http import request


class QuotationEsignCallback(http.Controller):
    @http.route(
        "/m36/quotation/esign/callback",
        type="jsonrpc",
        auth="public",
        csrf=False,
        methods=["POST"],
    )
    def esign_callback(
        self, quotation=None, version=None, signature_ref=None, signature=None, **kw
    ):
        try:
            with request.env.cr.savepoint():
                quote_id = (
                    request.env["fix.quotation"]
                    .sudo()
                    ._esign_provider_complete(quotation, version, signature_ref, signature)
                )
        except (UserError, ValidationError) as exc:
            return {"ok": False, "error": exc.args[0] if exc.args else str(exc)}
        return {"ok": True, "id": quote_id}
