# cd_document_core — controlled external release (FR-DMS-042, BRU-DMS-13,
# AC-13), M24 capture pass 2, 19 Nov 2026.
#
# The one public surface of the document kernel. A link works only while
# its fix.external.release is GRANTED and unexpired; it serves only the
# documents in that release's scope; every access is written to the
# append-only access log with the requester's IP; PDFs and images are
# stamped with the release on every copy served. A file type that cannot be
# watermarked is withheld when the release requires a watermark — the
# release fails closed rather than leaking an unmarked copy.
import base64
import html
import io
import logging

from odoo import fields, http
from odoo.http import request

logger = logging.getLogger(__name__)

_GONE = (
    "<html><body style='font-family:sans-serif'><h3>This link is not active.</h3>"
    "<p>It has expired, been revoked, or was never issued. Ask the sender for a new release.</p>"
    "</body></html>"
)


def _stamp_text(release):
    return "Released to %s - %s - valid until %s - not for onward distribution" % (
        release.partner_id.name or "external party",
        release.name,
        release.expires_on,
    )


def _watermark_pdf(raw, text):
    from odoo.tools.pdf import PdfFileReader, PdfFileWriter
    from reportlab.lib.colors import Color
    from reportlab.pdfgen import canvas

    reader = PdfFileReader(io.BytesIO(raw), strict=False)
    writer = PdfFileWriter()
    for page in reader.pages:
        box = page.mediabox
        width, height = float(box.width), float(box.height)
        buf = io.BytesIO()
        overlay = canvas.Canvas(buf, pagesize=(width, height))
        overlay.setFillColor(Color(0.75, 0, 0, alpha=0.35))
        overlay.setFont("Helvetica", 10)
        overlay.drawString(18, 14, text)
        overlay.saveState()
        overlay.translate(width / 2, height / 2)
        overlay.rotate(35)
        overlay.setFont("Helvetica-Bold", 28)
        overlay.drawCentredString(0, 0, "CONTROLLED RELEASE")
        overlay.restoreState()
        overlay.save()
        buf.seek(0)
        page.merge_page(PdfFileReader(buf).pages[0])
        writer.add_page(page)
    out = io.BytesIO()
    writer.write(out)
    return out.getvalue()


def _watermark_image(raw, text):
    from PIL import Image, ImageDraw

    img = Image.open(io.BytesIO(raw))
    fmt = img.format or "PNG"
    img = img.convert("RGBA")
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    band = max(14, img.size[1] // 30)
    draw.rectangle(
        [(0, img.size[1] - band - 6), (img.size[0], img.size[1])], fill=(255, 255, 255, 170)
    )
    draw.text((6, img.size[1] - band - 3), text, fill=(180, 0, 0, 255))
    out = io.BytesIO()
    merged = Image.alpha_composite(img, layer)
    if fmt.upper() in ("JPEG", "JPG"):
        merged.convert("RGB").save(out, format="JPEG", quality=90)
        return out.getvalue(), "image/jpeg"
    merged.save(out, format="PNG")
    return out.getvalue(), "image/png"


class DmsExternalRelease(http.Controller):
    def _log(self, release, doc, action):
        request.env["fix.document.access.log"].sudo().create(
            {
                "document_id": doc.id,
                "release_id": release.id,
                "action": action,
                "external_party_id": release.partner_id.id,
                "ip_or_device": (request.httprequest.remote_addr or "")[:64],
                "purpose": (release.purpose or "")[:200],
            }
        )

    @http.route(
        "/dms/release/<string:token>", type="http", auth="public", methods=["GET"], sitemap=False
    )
    def release_index(self, token, **kw):
        release = request.env["fix.external.release"]._resolve_token(token)
        if not release:
            return request.make_response(_GONE, headers=[("Content-Type", "text/html")], status=404)
        docs = release._released_documents()
        for doc in docs:
            self._log(release, doc, "view")
        rows = "".join(
            "<li><a href='/dms/release/%s/%d'>%s</a> (v%s)</li>"
            % (html.escape(token), d.id, html.escape(d.name or ""), html.escape(d.version or ""))
            for d in docs
        )
        body = (
            "<html><body style='font-family:sans-serif'><h3>%s</h3><p>%s</p>"
            "<p>Valid until %s. Every access is logged.</p><ul>%s</ul></body></html>"
            % (
                html.escape(release.name),
                html.escape(_stamp_text(release)),
                release.expires_on,
                rows or "<li>No document in scope.</li>",
            )
        )
        return request.make_response(
            body,
            headers=[("Content-Type", "text/html; charset=utf-8"), ("Cache-Control", "no-store")],
        )

    @http.route(
        "/dms/release/<string:token>/<int:doc_id>",
        type="http",
        auth="public",
        methods=["GET"],
        sitemap=False,
    )
    def release_file(self, token, doc_id, **kw):
        release = request.env["fix.external.release"]._resolve_token(token)
        if not release:
            return request.make_response(_GONE, headers=[("Content-Type", "text/html")], status=404)
        doc = release._released_documents().filtered(lambda d: d.id == doc_id)
        if not doc:
            return request.make_response(_GONE, headers=[("Content-Type", "text/html")], status=404)
        attachment = doc.sudo().attachment_id
        raw = base64.b64decode(attachment.datas or b"") if attachment else b""
        mimetype = attachment.mimetype or "application/octet-stream"
        if release.watermark:
            text = _stamp_text(release)
            try:
                if mimetype == "application/pdf" or raw[:4] == b"%PDF":
                    raw, mimetype = _watermark_pdf(raw, text), "application/pdf"
                elif mimetype.startswith("image/"):
                    raw, mimetype = _watermark_image(raw, text)
                else:
                    return request.make_response(
                        "This file type cannot be watermarked, so this release does not serve it. "
                        "Ask the sender for a PDF copy.",
                        headers=[("Content-Type", "text/plain; charset=utf-8")],
                        status=415,
                    )
            except Exception:
                logger.exception(
                    "watermarking failed for release %s document %s", release.id, doc.id
                )
                return request.make_response(
                    "The copy could not be watermarked and was withheld.",
                    headers=[("Content-Type", "text/plain; charset=utf-8")],
                    status=500,
                )
        self._log(release, doc, "download")
        filename = (attachment.name or doc.name or "document").replace('"', "")
        return request.make_response(
            raw,
            headers=[
                ("Content-Type", mimetype),
                ("Content-Disposition", 'attachment; filename="%s"' % filename),
                ("Cache-Control", "no-store"),
                ("X-Release", release.name),
                ("X-Release-Expires", fields.Date.to_string(release.expires_on)),
            ],
        )
