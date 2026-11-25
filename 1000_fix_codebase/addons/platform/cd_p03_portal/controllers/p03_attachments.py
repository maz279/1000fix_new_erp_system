# P03 workspace record attachments: list a record's documents and upload one.
#
# The service-order record view's "Upload Attachment" button only showed a
# message ("Select image or PDF to upload..."), and the in-workspace forms had
# no attachment panel at all, so the signed receipts, consents and scans the
# workflows require could only be attached in the Odoo back office (M06 audit,
# 2026-11-13).
#
# Rules:
#   * only a model the workspace serves (SURFACES) and a record that exists;
#   * listing needs read access to the record, uploading WRITE access, both
#     checked as the caller (never sudo) - the attachment is created as the
#     caller too, so Odoo's own attachment rules apply again;
#   * PDF, JPG, PNG or DOCX only, at most 10 MB, and the content must be what
#     the extension says (a renamed executable is refused);
#   * a residency-classified record (an M06 data-recovery case) lists its
#     documents without names and without a download link: they open through
#     the case's audited Z4 step-up access.
import base64
import binascii
import logging
import os

from odoo import fields, http
from odoo.exceptions import AccessError, UserError
from odoo.http import request

from .p03_generic_api import SURFACES
from .p03_service_order_api import _require_internal, _user_error

_logger = logging.getLogger(__name__)

MAX_BYTES = 10 * 1024 * 1024
# extension -> (mimetype, magic prefix of the content)
ALLOWED = {
    "pdf": ("application/pdf", (b"%PDF",)),
    "png": ("image/png", (b"\x89PNG\r\n\x1a\n",)),
    "jpg": ("image/jpeg", (b"\xff\xd8\xff",)),
    "jpeg": ("image/jpeg", (b"\xff\xd8\xff",)),
    "docx": (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        (b"PK\x03\x04",),
    ),
}
# documents of these records are listed without names or download links
NAMES_HIDDEN = frozenset({"fix.data.recovery.case"})


def _record(env, model, record_id, mode):
    """The served record, with `mode` access checked as the caller."""
    if model not in SURFACES:
        raise UserError("Documents are not available for this kind of record.")
    try:
        rec = env[model].browse(int(record_id)).exists()
    except (TypeError, ValueError):
        rec = None
    if not rec:
        raise UserError("Record not found.")
    rec.check_access(mode)
    return rec


def _row(att, hidden, index):
    ext = os.path.splitext(att.name or "")[1].lstrip(".").upper()
    # stored in UTC; shown in the user's time zone (Dhaka by default)
    local = att.with_context(tz=att.env.user.tz or "Asia/Dhaka")
    added = att.create_date and fields.Datetime.context_timestamp(local, att.create_date)
    return {
        "id": att.id,
        "name": ("Document %d" % index) if hidden else att.name,
        "type": ext or (att.mimetype or "FILE").split("/")[-1].upper(),
        "size_kb": round((att.file_size or 0) / 1024.0, 1),
        "date": added.strftime("%Y-%m-%d %H:%M") if added else "",
        "by": att.create_uid.name or "",
        "url": False if hidden else "/web/content/%d?download=true" % att.id,
    }


def _attachments(env, rec):
    return env["ir.attachment"].search(
        [("res_model", "=", rec._name), ("res_id", "=", rec.id), ("res_field", "=", False)],
        order="id desc",
    )


def _can_write(rec) -> bool:
    try:
        rec.check_access("write")
    except AccessError:
        return False
    return True


def _decode(data) -> bytes:
    if not data:
        raise UserError("Choose a file to upload.")
    if isinstance(data, str) and data.startswith("data:") and "," in data:
        data = data.split(",", 1)[1]
    # base64 is 4/3 the size: refuse an oversized payload before decoding it
    if len(data) > MAX_BYTES * 4 // 3 + 8:
        raise UserError("The file is larger than 10 MB.")
    try:
        raw = base64.b64decode(data, validate=True)
    except (binascii.Error, ValueError, TypeError):
        raise UserError("The file could not be read: upload it again.") from None
    if not raw:
        raise UserError("The file is empty.")
    if len(raw) > MAX_BYTES:
        raise UserError("The file is larger than 10 MB.")
    return raw


def _checked_name(name, raw):
    base = os.path.basename(str(name or "").replace("\\", "/")).strip()
    stem, ext = os.path.splitext(base)
    ext = ext.lstrip(".").lower()
    if not stem or ext not in ALLOWED:
        raise UserError("Upload a PDF, JPG, PNG or DOCX file.")
    mimetype, magics = ALLOWED[ext]
    if not raw.startswith(magics):
        raise UserError("%s is not a real %s file." % (base, ext.upper()))
    return base[:200], mimetype


def list_attachments(env, model, record_id):
    rec = _record(env, model, record_id, "read")
    hidden = model in NAMES_HIDDEN
    atts = _attachments(env, rec)
    count = len(atts)
    return {
        "rows": [_row(att, hidden, count - i) for i, att in enumerate(atts)],
        "can_upload": _can_write(rec),
        "names_hidden": hidden,
    }


def upload_attachment(env, model, record_id, name, data):
    rec = _record(env, model, record_id, "write")
    raw = _decode(data)
    filename, mimetype = _checked_name(name, raw)
    att = env["ir.attachment"].create(
        {
            "name": filename,
            "raw": raw,
            "mimetype": mimetype,
            "res_model": rec._name,
            "res_id": rec.id,
        }
    )
    if hasattr(rec, "message_post"):
        hidden = model in NAMES_HIDDEN
        rec.message_post(
            body="Document attached in the workspace by %s%s."
            % (env.user.name, "" if hidden else ": %s" % filename)
        )
    return att


class P03AttachmentsController(http.Controller):
    @http.route("/p03/model/attachments", type="jsonrpc", auth="user", readonly=True)
    def model_attachments(self, model=None, record_id=None, **kw):
        _require_internal(request.env)
        try:
            return list_attachments(request.env, model, record_id)
        except (UserError, AccessError) as exc:
            return {"error": _user_error(exc), "rows": [], "can_upload": False}

    @http.route("/p03/model/attachment/upload", type="jsonrpc", auth="user")
    def model_attachment_upload(self, model=None, record_id=None, name=None, data=None, **kw):
        _require_internal(request.env)
        env = request.env
        try:
            with env.cr.savepoint():
                att = upload_attachment(env, model, record_id, name, data)
            return {"success": True, "id": att.id}
        except (UserError, AccessError) as exc:
            return {"success": False, "error": _user_error(exc)}
        except Exception:
            _logger.exception("p03 attachment upload on %s/%s failed", model, record_id)
            return {"success": False, "error": "The upload failed. Try again."}
