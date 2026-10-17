# -*- coding: utf-8 -*-
"""evidence_api — Resumable deferred evidence upload controller (SP-09).

Ensures media files (photos, Bengali voice notes, documents, signature bitmaps)
are uploaded over a dedicated deferred channel with chunked resumable transfers.
Invariant SP-09: Media evidence upload NEVER blocks work order status sync.
"""

import base64
import hashlib
import json
import logging
from odoo import http, fields, api, SUPERUSER_ID
from odoo.http import request

_logger = logging.getLogger(__name__)

# In-memory chunk buffer for active multipart uploads (keyed by media_uuid)
# In production, this can be backed by Redis / S3 multipart upload.
_ACTIVE_CHUNKS = {}


def _su_env():
    return api.Environment(request.cr, SUPERUSER_ID, {})


class OfflineEvidenceApiController(http.Controller):
    """Deferred evidence channel API for P02 Technician mobile app (SP-09)."""

    @http.route(
        ["/api/v1/offline/evidence/chunk", "/technician/offline/evidence/chunk"],
        type="json",
        auth="public",
        methods=["POST"],
        csrf=False,
        cors="*"
    )
    def upload_chunk(self, **kwargs):
        """Upload a single chunk of evidence.
        
        Payload:
        {
            "media_uuid": "uuid-media-1234",
            "chunk_index": 0,
            "total_chunks": 4,
            "chunk_data": "<base64_data>",
            "chunk_hash": "<sha256>",
            "media_type": "photo", // "photo" | "voice_note_bengali" | "signature"
            "model": "fix.field.order",
            "record_id": 12,
            "filename": "job_before_photo_01.jpg"
        }
        """
        media_uuid = kwargs.get("media_uuid")
        chunk_index = kwargs.get("chunk_index")
        total_chunks = kwargs.get("total_chunks", 1)
        chunk_data = kwargs.get("chunk_data", "")
        chunk_hash = kwargs.get("chunk_hash")
        media_type = kwargs.get("media_type", "photo")
        model_name = kwargs.get("model", "fix.field.order")
        record_id = kwargs.get("record_id")
        filename = kwargs.get("filename") or f"{media_type}_{media_uuid[:8]}.bin"

        if not media_uuid or chunk_index is None:
            return {"error": {"code": "missing_params", "message": "media_uuid and chunk_index required"}}

        # Verify chunk checksum if provided
        if chunk_hash:
            computed = hashlib.sha256(chunk_data.encode("utf-8")).hexdigest()
            if computed != chunk_hash:
                return {
                    "error": {
                        "code": "checksum_mismatch",
                        "message": f"Chunk checksum mismatch: expected {chunk_hash}, got {computed}"
                    }
                }

        # Store chunk in session buffer
        if media_uuid not in _ACTIVE_CHUNKS:
            _ACTIVE_CHUNKS[media_uuid] = {
                "total_chunks": total_chunks,
                "chunks": {},
                "media_type": media_type,
                "model": model_name,
                "record_id": record_id,
                "filename": filename,
            }

        session = _ACTIVE_CHUNKS[media_uuid]
        session["chunks"][chunk_index] = chunk_data

        received_count = len(session["chunks"])
        is_complete = received_count >= total_chunks

        attachment_id = None
        if is_complete:
            # Reassemble all chunks in index order
            assembled_b64 = "".join(session["chunks"][i] for i in range(total_chunks))
            env = _su_env()
            
            try:
                # Create ir.attachment
                att_vals = {
                    "name": filename,
                    "type": "binary",
                    "datas": assembled_b64,
                    "res_model": model_name,
                    "res_id": int(record_id) if record_id else 0,
                    "mimetype": "audio/mp4" if "voice" in media_type else "image/jpeg",
                    "description": f"SP-09 Deferred Evidence ({media_type}) - Session {media_uuid}",
                }
                attachment = env["ir.attachment"].create(att_vals)
                attachment_id = attachment.id

                # Post chatter notification if target record exists
                if model_name and record_id:
                    target_rec = env[model_name].browse(int(record_id))
                    if target_rec.exists() and hasattr(target_rec, "message_post"):
                        target_rec.message_post(
                            body=f"Uploaded offline evidence [{media_type}]: {filename}",
                            attachment_ids=[attachment.id]
                        )

            except Exception as e:
                _logger.exception("Failed assembling deferred evidence attachment %s: %s", media_uuid, e)
            finally:
                # Clean up buffer
                _ACTIVE_CHUNKS.pop(media_uuid, None)

        return {
            "status": "complete" if is_complete else "chunk_accepted",
            "media_uuid": media_uuid,
            "chunk_index": chunk_index,
            "received_chunks": received_count,
            "total_chunks": total_chunks,
            "complete": is_complete,
            "attachment_id": attachment_id,
        }
