# cd_knowledge registry conformance (P09-M08 & R07-M05 / CD-M61-01 & P02
# Offline Manuals) — A10 S6: this suite once certified the module by grepping
# its own source (inspect.getsource). It now reads the LIVE REGISTRY: the
# selections, fields and mixins the ORM actually exposes. The behaviour those
# greps pointed at (content hashing, publish events, offline manuals, the
# draft->published->archived journey) is proven on real records in
# test_knowledge_orm.py, test_knowledge_sync.py and test_a10_k1_controls.py.
from odoo.addons.cd_knowledge.models.fix_knowledge import FixKnowledgeArticle


def test_categories_cover_m22_rescope(odoo_env):
    selection = [
        value for value, _label in odoo_env["fix.knowledge.article"]._fields["category"].selection
    ]
    for cat in (
        "troubleshooting",
        "repair_procedure",
        "device_guide",
        "schematic",
        "safety_bulletin",
    ):
        assert cat in selection, cat


def test_bengali_title_and_content_fields():
    assert hasattr(FixKnowledgeArticle, "title_bn")
    assert hasattr(FixKnowledgeArticle, "content_bn")


def test_technical_hardware_metadata():
    assert hasattr(FixKnowledgeArticle, "device_brand")
    assert hasattr(FixKnowledgeArticle, "device_model")
    assert hasattr(FixKnowledgeArticle, "fault_symptom")
    assert hasattr(FixKnowledgeArticle, "rework_level")


def test_offline_sync_and_content_hash():
    assert hasattr(FixKnowledgeArticle, "offline_available")
    assert hasattr(FixKnowledgeArticle, "content_hash")
    assert hasattr(FixKnowledgeArticle, "version")
    assert hasattr(FixKnowledgeArticle, "get_offline_manuals")


def test_the_publish_event_reaches_the_outbox(odoo_env):
    """The old grep asserted 'knowledge.published' appears in the source; the
    behaviour test (test_knowledge_orm.test_publish_bumps_version_and_announces)
    drives action_publish and asserts the outbox row. This keeps the claim in
    this suite too, against the registry of record."""
    art = odoo_env["fix.knowledge.article"].create(
        {"name": "Registry event check", "category": "device_guide", "content": "<p>x</p>"}
    )
    art.action_publish()
    assert (
        odoo_env["fix.event.outbox"].search_count(
            [("event_type", "=", "knowledge.published"), ("aggregate_id", "=", art.id)]
        )
        == 1
    )


def test_lifecycle_states_exist_and_are_reachable(odoo_env):
    """DE-16: every state reachable — proven on a record, not by finding the
    word in the source."""
    selection = [
        value for value, _label in odoo_env["fix.knowledge.article"]._fields["state"].selection
    ]
    assert selection == ["draft", "published", "archived"]
    art = odoo_env["fix.knowledge.article"].create(
        {"name": "Lifecycle walk", "category": "device_guide", "content": "<p>y</p>"}
    )
    art.action_publish()
    art.action_archive()
    assert art.state == "archived"


def test_as02_conformance():
    for mixin in ("mail.thread", "mail.activity.mixin"):
        assert mixin in FixKnowledgeArticle._inherit
    assert hasattr(FixKnowledgeArticle, "company_id")
    assert hasattr(FixKnowledgeArticle, "operating_unit_id")
