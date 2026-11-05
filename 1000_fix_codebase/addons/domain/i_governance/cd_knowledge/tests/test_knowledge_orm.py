"""cd_knowledge — live-ORM behaviour of M61 articles and the P02 offline sync."""

from __future__ import annotations

import hashlib
import json

BRAND = "Zeltrix QA Labs"  # deliberately not an install-data brand


def _article(env, **vals):
    base = {
        "name": "Zeltrix Z14 no power",
        "category": "troubleshooting",
        "content": "<p>Check the 19V rail</p>",
        "device_brand": BRAND,
        "device_model": "Z14",
    }
    base.update(vals)
    return env["fix.knowledge.article"].create(base)


def test_content_hash_tracks_the_stored_content(odoo_env):
    art = _article(odoo_env, content_bn="<p>১৯ ভোল্ট পরীক্ষা</p>")
    expected = hashlib.sha256(
        f"{art.name}|{art.category}|{art.content}|{art.content_bn}".encode()
    ).hexdigest()
    assert art.content_hash == expected
    before = art.content_hash
    art.content = "<p>Check the 19V rail and the charging IC</p>"
    assert art.content_hash != before


def test_publish_bumps_version_and_announces(odoo_env):
    art = _article(odoo_env, article_code="KB-HW-777")
    assert (art.state, art.version) == ("draft", 1)
    art.action_publish()
    assert (art.state, art.version) == ("published", 2)
    events = odoo_env["fix.event.outbox"].search(
        [("event_type", "=", "knowledge.published"), ("aggregate_id", "=", art.id)]
    )
    # K1/M61-3: the payload carries the version and the content hash the
    # offline delta sync keys on.
    assert [json.loads(e.payload) for e in events] == [
        {
            "title": "Zeltrix Z14 no power",
            "category": "troubleshooting",
            "code": "KB-HW-777",
            "version": 2,
            "content_hash": art.content_hash,
        }
    ]


def test_offline_manual_filters_and_fallbacks(odoo_env):
    published = _article(odoo_env)
    published.action_publish()
    other_model = _article(odoo_env, name="Zeltrix Z15 hinge", device_model="Z15")
    other_model.action_publish()
    _article(odoo_env, name="Draft only")  # never published
    hidden = _article(odoo_env, name="Online only", offline_available=False)
    hidden.action_publish()

    model = odoo_env["fix.knowledge.article"]
    by_brand = model.get_offline_manuals(brand=BRAND.upper())  # =ilike: case-insensitive
    assert {m["title_en"] for m in by_brand} == {"Zeltrix Z14 no power", "Zeltrix Z15 hinge"}

    (manual,) = model.get_offline_manuals(brand=BRAND, model="z14")
    assert manual == {
        "id": published.id,
        "code": "KB-%04d" % published.id,  # no article_code
        "title_en": "Zeltrix Z14 no power",
        "title_bn": "Zeltrix Z14 no power",  # Bengali title falls back to English
        "category": "troubleshooting",
        "brand": BRAND,
        "model": "Z14",
        "fault_symptom": "",
        "rework_level": "L2",
        "content_en": published.content,
        "content_bn": published.content,
        "content_hash": published.content_hash,
        "version": 2,
    }
    assert model.get_offline_manuals(brand=BRAND, version_after=2) == []
    # K1 (M61-3): editing published content is a REVISION, not a republish —
    # the version rises and the event re-delivers it to the offline devices.
    author = (
        odoo_env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "K1 Sync Author",
                "login": "k1.sync.author@a10.test",
                "group_ids": [(6, 0, [odoo_env.ref("base.group_user").id])],
            }
        )
    )
    published.with_user(author).write(
        {"content": "<p>Check the 19V rail, the charging IC and the fuse</p>"}
    )
    assert published.version == 3  # the write itself bumped it
    assert [m["id"] for m in model.get_offline_manuals(brand=BRAND, version_after=2)] == [
        published.id
    ]
    every = model.get_offline_manuals()
    assert {published.id, other_model.id} <= {m["id"] for m in every}
    assert hidden.id not in {m["id"] for m in every}
