"""A12 D8 hand-off: retiring an ITSM asset surfaces the destruction review
on the governed documents linked to it."""

from __future__ import annotations


def _event(asset_id, asset_tag, event_id="evt-a1"):
    return {
        "event_id": event_id,
        "event_type": "itsm.asset_retired",
        "payload": {"asset_id": asset_id, "asset_tag": asset_tag},
        "company_id": 1,
    }


def _document(odoo_env, res_id, name):
    attachment = odoo_env["ir.attachment"].create(
        {"name": name, "datas": b"ZGVzdHJveC1yZXZpZXc=", "mimetype": "text/plain"}
    )
    return odoo_env["fix.document"].create(
        {
            "name": name,
            "attachment_id": attachment.id,
            "document_type": "asset_document",
            "res_model": "fix.itsm.asset",
            "res_id": res_id,
        }
    )


def test_consumer_record_exists(odoo_env):
    consumer = odoo_env.ref(
        "cd_document_core.consumer_itsm_asset_retired", raise_if_not_found=False
    )
    assert consumer, "fix.event.consumer record for itsm.asset_retired is missing"
    assert consumer.method == "consume_itsm_asset_retired"


def test_retired_asset_documents_get_the_destruction_note(odoo_env):
    doc = _document(odoo_env, 421, "Warranty card LT-421")
    posted = odoo_env["fix.document"].consume_itsm_asset_retired(_event(421, "LT-421"))
    assert posted == 1
    assert "LT-421 retired" in doc.message_ids[0].body
    assert "destruction review" in doc.message_ids[0].body


def test_documents_of_other_assets_are_untouched(odoo_env):
    doc = _document(odoo_env, 999, "Warranty card LT-999")
    posted = odoo_env["fix.document"].consume_itsm_asset_retired(_event(422, "LT-422"))
    assert posted == 0
    assert not [m for m in doc.message_ids if "retired" in (m.body or "")]


def test_redelivery_does_not_duplicate_the_note(odoo_env):
    doc = _document(odoo_env, 423, "Asset file LT-423")
    first = odoo_env["fix.document"].consume_itsm_asset_retired(_event(423, "LT-423"))
    again = odoo_env["fix.document"].consume_itsm_asset_retired(_event(423, "LT-423"))
    assert (first, again) == (1, 0)
    notes = [m for m in doc.message_ids if "evt-a1" in (m.body or "")]
    assert len(notes) == 1, "redelivery must not duplicate the destruction note"
