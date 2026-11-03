"""A03 audit W8: a pre-sales estimate can be saved from every estimate form.

A pre-sales estimate quotes a CRM opportunity before any service order
exists; cd_crm_ext makes order_id optional and requires an order OR an
opportunity. The M01 and M36 estimate forms still marked Service Order
required, so the workspace refused to save such an estimate when it was
opened there (the model maps to one form per module).
"""

import re

import pytest
from odoo.addons.cd_p03_portal.controllers import form_fields
from odoo.exceptions import ValidationError


def _estimate_form_bodies():
    for js in sorted(form_fields.STATIC.glob("*/m*.js")):
        text = js.read_text(encoding="utf-8")
        starts = [(m.start(), m.group(1)) for m in form_fields.SCREEN.finditer(text)]
        for i, (pos, sid) in enumerate(starts):
            end = starts[i + 1][0] if i + 1 < len(starts) else len(text)
            body = text[pos:end]
            if "kind: 'model_form'" in body and "model: 'fix.estimate'" in body:
                yield sid, body


def test_no_estimate_form_requires_a_service_order():
    seen = []
    for sid, body in _estimate_form_bodies():
        seen.append(sid)
        for line in body.splitlines():
            if re.search(r"name:\s*'order_id'", line):
                assert "required: true" not in line, sid
    assert {"M01-form-estimate", "M36-form-estimate", "M07-form-quote"} <= set(seen)


def test_the_server_still_requires_an_order_or_an_opportunity(odoo_env):
    env = odoo_env
    lead = env["crm.lead"].create({"name": "W8 deal", "type": "opportunity"})
    est = env["fix.estimate"].create({"lead_id": lead.id})
    assert est.lead_id == lead and not est.order_id
    with pytest.raises(ValidationError, match="service order or to a CRM opportunity"):
        env["fix.estimate"].create({})
