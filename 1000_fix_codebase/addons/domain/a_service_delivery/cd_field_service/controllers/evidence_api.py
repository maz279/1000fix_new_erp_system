"""evidence_api — Resumable deferred evidence upload controller (SP-09).

Ensures media files (photos, Bengali voice notes, documents, signature bitmaps)
are uploaded over a dedicated deferred channel with chunked resumable transfers.
Invariant SP-09: Media evidence upload NEVER blocks work order status sync.

Security: ``auth="bearer"``; the uploader is the authenticated technician
(``resolve_technician``), evidence may only target a field/work order assigned
to that technician, and upload sessions are keyed per technician so nobody can
inject chunks into another technician's upload.
"""

import hashlib
import logging

from odoo import SUPERUSER_ID, http
from odoo.addons.cd_service_order.controllers.technician_api import (
    _error,
    _to_int,
    resolve_technician,
)
from odoo.exceptions import UserError
from odoo.http import request

from libs.py.fix_api_edge import api_edge

_logger = logging.getLogger(__name__)

# In-memory chunk buffer for active multipart uploads, keyed by
# (technician hr.employee id, media_uuid).
# In production, this can be backed by Redis / S3 multipart upload.
_ACTIVE_CHUNKS = {}

# Records evidence may be attached to (each carries technician_id).
EVIDENCE_TARGET_MODELS = ("fix.field.order", "fix.work.order")
MAX_TOTAL_CHUNKS = 200  # 200 x 512 KB = 100 MB per media item
MAX_CHUNK_B64_CHARS = 1024 * 1024  # a 512 KB chunk is ~700 KB of base64


def _su_env():
    return request.env(user=SUPERUSER_ID, su=True)


class OfflineEvidenceApiController(http.Controller):
    """Deferred evidence channel API for P02 Technician mobile app (SP-09)."""

    @http.route(
        ["/api/v1/offline/evidence/chunk", "/technician/offline/evidence/chunk"],
        type="jsonrpc",
        auth="bearer",
        methods=["POST"],
    )
    @api_edge("/api/v1/offline/evidence/chunk")
    def upload_chunk(self, **kwargs):
        """Upload a single chunk of evidence for a record assigned to the caller.

        Payload:
        {
            "media_uuid": "uuid-media-1234",
            "chunk_index": 0,
            "total_chunks": 4,
            "chunk_data": "<base64_data>",
            "chunk_hash": "<sha256>",
            "media_type": "photo", // "photo" | "voice_note_bengali" | "signature"
            "model": "fix.field.order", // or "fix.work.order"
            "record_id": 12,
            "filename": "job_before_photo_01.jpg"
        }
        """
        tech, err = resolve_technician(kwargs)
        if err:
            return err

        media_uuid = kwargs.get("media_uuid")
        chunk_index = _to_int(kwargs.get("chunk_index"))
        total_chunks = _to_int(kwargs.get("total_chunks", 1))
        chunk_data = kwargs.get("chunk_data") or ""
        chunk_hash = kwargs.get("chunk_hash")
        media_type = kwargs.get("media_type", "photo")
        model_name = kwargs.get("model", "fix.field.order")
        record_id = kwargs.get("record_id")

        if not media_uuid or not isinstance(media_uuid, str) or chunk_index is None:
            return _error("missing_params", "media_uuid and chunk_index required")
        if total_chunks is None or not 1 <= total_chunks <= MAX_TOTAL_CHUNKS:
            return _error(
                "invalid_chunking", f"total_chunks must be between 1 and {MAX_TOTAL_CHUNKS}"
            )
        if not isinstance(chunk_data, str) or len(chunk_data) > MAX_CHUNK_B64_CHARS:
            return _error("invalid_chunk", "chunk_data must be a base64 string of at most 1 MB")

        # The evidence target must be a record assigned to the authenticated technician.
        if model_name not in EVIDENCE_TARGET_MODELS:
            return _error(
                "invalid_target", f"Evidence can only be attached to {EVIDENCE_TARGET_MODELS}"
            )
        env = _su_env()
        target_id = _to_int(record_id)
        target_rec = env[model_name]
        if target_id:
            target_rec = env[model_name].search(
                [("id", "=", target_id), ("technician_id", "=", tech.id)], limit=1
            )
        if not target_rec:
            return _error("forbidden", "Evidence target not found or not assigned to you")

        # Verify chunk checksum if provided
        if chunk_hash:
            computed = hashlib.sha256(chunk_data.encode("utf-8")).hexdigest()
            if computed != chunk_hash:
                return _error(
                    "checksum_mismatch",
                    f"Chunk checksum mismatch: expected {chunk_hash}, got {computed}",
                )

        session_key = (tech.id, media_uuid)
        session = _ACTIVE_CHUNKS.get(session_key)
        if session is not None:
            if (session["model"], session["record_id"]) != (model_name, target_rec.id):
                return _error("invalid_target", "media_uuid is already bound to another record")
            total_chunks = session["total_chunks"]
        if not 0 <= chunk_index < total_chunks:
            return _error("invalid_chunk", f"chunk_index must be in [0, {total_chunks})")
        if session is None:
            session = _ACTIVE_CHUNKS[session_key] = {
                "total_chunks": total_chunks,
                "chunks": {},
                "media_type": media_type,
                "model": model_name,
                "record_id": target_rec.id,
                "filename": kwargs.get("filename") or f"{media_type}_{media_uuid[:8]}.bin",
            }
        session["chunks"][chunk_index] = chunk_data

        received_count = len(session["chunks"])
        is_complete = received_count >= total_chunks

        attachment_id = None
        if is_complete:
            # Reassemble all chunks in index order
            assembled_b64 = "".join(session["chunks"][i] for i in range(total_chunks))
            filename = session["filename"]

            try:
                # SP-02 style isolation: a failed store must not poison the request
                with env.cr.savepoint():
                    attachment = env["ir.attachment"].create(
                        {
                            "name": filename,
                            "type": "binary",
                            "datas": assembled_b64,
                            "res_model": session["model"],
                            "res_id": session["record_id"],
                            "mimetype": "audio/mp4"
                            if "voice" in session["media_type"]
                            else "image/jpeg",
                            "description": f"SP-09 Deferred Evidence ({session['media_type']}) "
                            f"- Session {media_uuid}",
                        }
                    )
                    # Chatter notification on the (technician-owned) target record;
                    # both EVIDENCE_TARGET_MODELS are mail.thread models.
                    target_rec.message_post(
                        body=f"Uploaded offline evidence [{session['media_type']}]: {filename}",
                        attachment_ids=[attachment.id],
                    )
            except Exception as e:
                # Reported, never swallowed: the old code answered "complete" with
                # no attachment and dropped the chunks - the client deleted its
                # copy and the evidence was lost.
                _logger.exception(
                    "Failed assembling deferred evidence attachment %s: %s", media_uuid, e
                )
                return _error(
                    "assembly_failed",
                    f"Evidence {media_uuid} could not be stored; restart its upload",
                )
            finally:
                # Clean up buffer
                _ACTIVE_CHUNKS.pop(session_key, None)
            attachment_id = attachment.id
            # A02 audit M02-2: a signature or photo uploaded here is the
            # completion evidence of a field order. Linking it never blocks the
            # upload (SP-09): a photo taken in the wrong state is kept, unlinked.
            if session["model"] == "fix.field.order":
                try:
                    with env.cr.savepoint():
                        target_rec._fix_attach_field_evidence(attachment, session["media_type"])
                except UserError as exc:
                    _logger.info("evidence %s kept unlinked: %s", media_uuid, exc)

        return {
            "status": "complete" if is_complete else "chunk_accepted",
            "media_uuid": media_uuid,
            "chunk_index": chunk_index,
            "received_chunks": received_count,
            "total_chunks": total_chunks,
            "complete": is_complete,
            "attachment_id": attachment_id,
        }
