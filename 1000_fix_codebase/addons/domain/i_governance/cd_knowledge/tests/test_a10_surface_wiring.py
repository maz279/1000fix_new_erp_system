# A10 deep audit (2026-11-23, D-A10-1/#4): the knowledge surface ON the job.
#
# surface_for() (FR-KMS-015) ranked published knowledge perfectly and had no
# production caller. Now every service order carries its surface — the M01
# drawer and the P02 app read order.knowledge_surface_ids.
import pytest


@pytest.fixture
def job(odoo_env):
    env = odoo_env
    brand = env["fix.brand"].search([], limit=1) or env["fix.brand"].create(
        {"name": "SurfBrand", "code": "SURFB"}
    )
    model = env["fix.device.model"].search([("brand_id", "=", brand.id)], limit=1)
    if not model:
        model = env["fix.device.model"].create({"name": "SurfPhone", "brand_id": brand.id})
    customer = env["res.partner"].create({"name": "Surf Customer", "phone": "01711000111"})
    device = env["fix.device"].create(
        {
            "device_model_id": model.id,
            "owner_id": customer.id,
            "serial_number": "SN-SURF-1",
        }
    )
    ou = env["operating.unit"].search([], limit=1)
    entity = env["fix.entity"].search([], limit=1) or env["fix.entity"].create(
        {"code": "SURFE", "legal_name": "Surface Test Entity", "company_id": env.company.id}
    )
    branch = env["fix.branch"].search([("operating_unit_id", "=", ou.id)], limit=1)
    if not branch:
        branch = env["fix.branch"].create(
            {
                "name": "Surface Branch",
                "code": "SURFB",
                "entity_id": entity.id,
                "operating_unit_id": ou.id,
            }
        )
    order = env["fix.service.order"].create(
        {
            "device_id": device.id,
            "customer_id": customer.id,
            "branch_id": branch.id,
            "service_type": "walk_in",
            "order_category": "standard",
            "fault_description": "no power",
        }
    )
    return env, order, brand, model


def test_the_order_carries_its_knowledge_surface(job):
    env, order, brand, model = job
    # nothing published for this brand yet: honest empty
    order.invalidate_recordset()
    assert not [r for r in (order.knowledge_surface_ids or []) if r["kind"] == "article"]

    article = env["fix.knowledge.article"].create(
        {
            "name": "SurfPhone no power fix",
            "category": "repair_procedure",
            "content": "<p>Check the rail</p>",
            "device_brand": brand.name,
            "device_model": model.name,
        }
    )
    article.sudo().action_publish()
    article.invalidate_recordset()
    order.invalidate_recordset()
    rows = order.knowledge_surface_ids or []
    matched = [r for r in rows if r["kind"] == "article" and r["id"] == article.id]
    assert matched, rows
    assert matched[0]["name"] == "SurfPhone no power fix"
    assert matched[0]["relevance"] >= 1  # the brand match counted

    # the drawer's read action resolves to the articles
    action = order.action_read_the_knowledge()
    assert action["res_model"] == "fix.knowledge.article"
    (field, operator, ids) = action["domain"][0]
    assert (field, operator) == ("id", "in")
    assert article.id in ids


def test_draft_and_unpublished_knowledge_never_surfaces(job):
    env, order, brand, model = job
    draft = env["fix.knowledge.article"].create(
        {
            "name": "Draft only SurfPhone",
            "category": "troubleshooting",
            "content": "<p>unpublished</p>",
            "device_brand": brand.name,
            "device_model": model.name,
        }
    )
    order.invalidate_recordset()
    ids = [r["id"] for r in (order.knowledge_surface_ids or [])]
    assert draft.id not in ids
