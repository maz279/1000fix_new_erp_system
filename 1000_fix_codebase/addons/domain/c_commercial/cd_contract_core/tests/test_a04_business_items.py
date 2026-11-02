"""The three items that were standing open as 'business, not engineering'.

The operator authorised completing them and asked me to decide what is best.
What was best turned out to be mostly engineering after all - each item had a
real blocker underneath it:

  Schedule I rates   there was NO SCREEN for fix.stamp.duty.schedule anywhere
                     in the workspace, so "Finance enters the rates" was never
                     actionable, and nothing recorded who stood behind a rate.
  Contract wording   is_publishable went true the moment both text fields were
                     non-empty, so seeding drafts would have made six
                     unreviewed contracts immediately issuable to customers.
  53 verifications   ZERO of the 55 live warranties has a proof document, so
                     action_verify could never have succeeded for anyone.

What is NOT done here, deliberately: no statutory rate is typed in (I could
not source the current Article 5 figures), no template is signed off, and no
warranty is stamped verified. Those three assertions need a person, and a test
that faked them would be the exact falsification this audit exists to catch.
"""

from datetime import date

import pytest
from odoo.exceptions import UserError, ValidationError


@pytest.fixture
def env(odoo_env):
    return odoo_env


# ==========================================================================
# Stamp Act 1899 Schedule I - a rate nobody confirmed is not in force
# ==========================================================================
class TestStampDutySchedule:
    def _row(self, env, **kw):
        vals = {
            "article": "art_5",
            "name": "Agreement - test row",
            "date_from": date(2026, 1, 1),
            "exemption_floor_bdt": 300000.0,
            "statutory_reference": "test fixture, not a statutory rate",
        }
        vals.update(kw)
        return env["fix.stamp.duty.schedule"].create(vals)

    def test_a_new_row_is_draft(self, env):
        assert self._row(env).state == "draft"

    def test_a_draft_rate_is_not_in_force(self, env):
        """The whole point: an unconfirmed number must not waive duty."""
        self._row(env, exemption_floor_bdt=10_000_000.0)
        assert env["fix.stamp.duty.schedule"].is_chargeable("art_5", 1000.0) is True

    def test_a_confirmed_rate_is_in_force(self, env):
        row = self._row(env, exemption_floor_bdt=300000.0)
        row.action_confirm()
        Schedule = env["fix.stamp.duty.schedule"]
        assert Schedule.is_chargeable("art_5", 300000.0) is False
        assert Schedule.is_chargeable("art_5", 300000.01) is True

    def test_confirming_requires_a_citation(self, env):
        """A rate nobody can check is not a rate."""
        row = self._row(env, statutory_reference="")
        with pytest.raises(UserError, match="Cite the Finance Act"):
            row.action_confirm()

    def test_confirmation_is_attributable(self, env):
        row = self._row(env)
        row.action_confirm()
        assert row.confirmed_by == env.user
        assert row.confirmed_on

    def test_confirming_twice_is_refused(self, env):
        row = self._row(env)
        row.action_confirm()
        with pytest.raises(UserError, match="already confirmed"):
            row.action_confirm()

    def test_withdrawing_takes_a_rate_out_of_force_at_once(self, env):
        row = self._row(env, exemption_floor_bdt=300000.0)
        row.action_confirm()
        assert env["fix.stamp.duty.schedule"].is_chargeable("art_5", 1000.0) is False
        row.action_reset_to_draft()
        assert env["fix.stamp.duty.schedule"].is_chargeable("art_5", 1000.0) is True

    def test_an_empty_table_still_charges_duty(self, env):
        assert env["fix.stamp.duty.schedule"].is_chargeable("art_35", 1.0) is True

    def test_the_in_force_lookup_uses_the_business_date(self, env):
        """A Finance Act commences on a DATE. Bangladesh is UTC+6, so the UTC
        date selects the wrong rate row for six hours of every local day."""
        import inspect

        src = inspect.getsource(
            type(env["fix.stamp.duty.schedule"]).rate_for.__wrapped__
            if hasattr(type(env["fix.stamp.duty.schedule"]).rate_for, "__wrapped__")
            else type(env["fix.stamp.duty.schedule"]).rate_for
        )
        assert "context_today" in src
        assert "fields.Date.today()" not in src

    def test_finance_has_somewhere_to_enter_them(self):
        """The actual reason this item never moved: no UI existed."""
        from pathlib import Path

        src = Path(__file__).resolve().parents[4] / "platform" / "cd_p03_portal"
        js = (src / "static" / "src" / "a04" / "m08.js").read_text(encoding="utf-8")
        py = (src / "controllers" / "a04" / "m08.py").read_text(encoding="utf-8")
        assert "'M08-stampduty'" in js, "no list screen for the rate table"
        assert "'M08-form-stampduty'" in js, "no form to enter a rate"
        assert "fix.stamp.duty.schedule" in py, "the model is not served"
        assert "action_confirm" in py, "the confirm action is not exposed"


# ==========================================================================
# Contract templates - wording is not sign-off
# ==========================================================================
class TestContractTemplateWording:
    def _tpl(self, env, ctype):
        t = env["fix.contract.template"].search([("contract_type", "=", ctype)], limit=1)
        assert t, "no %s template seeded" % ctype
        return t

    @pytest.mark.parametrize("ctype", ["amc", "ramc", "managed", "rental", "marketplace", "sla"])
    def test_every_family_has_draft_wording_in_both_languages(self, env, ctype):
        t = self._tpl(env, ctype)
        assert (t.standard_terms or "").strip(), "%s has no English terms" % ctype
        assert (t.terms_bn or "").strip(), "%s has no Bengali terms" % ctype

    @pytest.mark.parametrize("ctype", ["amc", "ramc", "managed", "rental", "marketplace", "sla"])
    def test_drafted_wording_is_marked_as_draft(self, env, ctype):
        t = self._tpl(env, ctype)
        assert "DRAFT" in (t.standard_terms or ""), (
            "%s wording does not announce itself as a draft" % ctype
        )

    @pytest.mark.parametrize("ctype", ["amc", "ramc", "managed", "rental", "marketplace", "sla"])
    def test_no_drafted_template_is_issuable(self, env, ctype):
        """The property that matters. Before the Legal gate, writing terms
        would have made six unreviewed contracts immediately usable."""
        t = self._tpl(env, ctype)
        assert t.is_publishable is False
        assert "Legal sign-off" in (t.publish_blocker or "")
        with pytest.raises(UserError, match="not ready to issue"):
            t.assert_publishable()

    def test_legal_signoff_makes_it_issuable(self, env):
        t = self._tpl(env, "sla")
        t.action_legal_signoff()
        assert t.is_publishable is True
        assert t.legal_reviewed_by == env.user
        assert t.terms_are_draft is False
        assert t.assert_publishable() is True

    def test_signoff_is_refused_without_both_languages(self, env):
        t = self._tpl(env, "amc")
        t.terms_bn = ""
        with pytest.raises(UserError, match="English and Bengali"):
            t.action_legal_signoff()

    def test_withdrawing_signoff_stops_issue_at_once(self, env):
        t = self._tpl(env, "managed")
        t.action_legal_signoff()
        assert t.is_publishable is True
        t.action_withdraw_signoff()
        assert t.is_publishable is False
        assert t.terms_are_draft is True

    def test_the_rental_template_cites_the_right_stamp_article(self, env):
        """A hire instrument is Article 35, not Article 5."""
        t = self._tpl(env, "rental")
        assert "Article 35" in (t.standard_terms or "")

    def test_the_marketplace_template_states_the_escrow_rule(self, env):
        """The wording must describe what the platform actually does."""
        t = self._tpl(env, "marketplace")
        terms = t.standard_terms or ""
        assert "dispute window" in terms
        assert "Income Tax Act 2023" in terms


# ==========================================================================
# Warranty verification - the queue, not a stamp
# ==========================================================================
class TestWarrantyVerificationQueue:
    def _device(self, env):
        """Build one. A skipped test certifies nothing - fix_test holds no
        fix.device, and four of these quietly skipped on the first run."""
        device = env["fix.device"].search([], limit=1)
        if device:
            return device
        model = env["fix.device.model"].search([], limit=1)
        if not model:
            brand = env["fix.brand"].search([], limit=1) or env["fix.brand"].create(
                {"name": "Business-item brand", "code": "BIZBRAND"}
            )
            model = env["fix.device.model"].create(
                {"name": "Business-item model", "brand_id": brand.id}
            )
        return env["fix.device"].create(
            {"device_model_id": model.id, "lifecycle_stage": "active", "state": "in_service"}
        )

    def _w(self, env, **kw):
        device = self._device(env)
        vals = {
            "device_id": device.id,
            "warranty_type": "brand_standard",
            "start_date": date(2026, 1, 1),
            "end_date": date(2027, 1, 1),
            "status": "active",
        }
        vals.update(kw)
        return env["fix.warranty"].create(vals)

    def test_brand_standard_is_a_valid_type(self, env):
        """50 of 55 live warranties carry it; it was not in the selection,
        so the type rendered with no label for 90% of them."""
        sel = dict(env["fix.warranty"]._fields["warranty_type"].selection)
        assert "brand_standard" in sel
        assert sel["brand_standard"] == "Brand Standard Warranty"

    def test_a_warranty_without_proof_says_what_it_needs(self, env):
        w = self._w(env)
        assert w.verification_state == "unverified"
        assert "Attach the purchase receipt" in (w.verification_blocker or "")

    def test_a_warranty_with_proof_says_it_is_ready(self, env):
        att = env["ir.attachment"].create({"name": "receipt", "raw": b"x"})
        doc = env["fix.document"].create(
            {"name": "Receipt", "attachment_id": att.id, "document_type": "warranty_card"}
        )
        w = self._w(env, proof_document_id=doc.id)
        assert "ready to Verify" in (w.verification_blocker or "")

    def test_verifying_still_requires_proof(self, env):
        """Authorisation to 'complete the task' does not make a receipt
        exist. This must keep refusing."""
        w = self._w(env)
        with pytest.raises(UserError, match="before verifying"):
            w.action_verify()

    def test_a_closed_warranty_is_not_in_the_queue(self, env):
        w = self._w(env, status="active")
        w.action_void(reason="test")
        assert not w.verification_blocker


# ==========================================================================
# Kit components must say what they are
# ==========================================================================
class TestKitComponentIntegrity:
    def _kit(self, env):
        tmpl = env["product.template"].create({"name": "Kit test item"})
        item = env["fix.catalogue.item"].create({"product_tmpl_id": tmpl.id})
        return env["fix.service.kit"].create(
            {
                "name": "Integrity kit",
                "catalogue_item_id": item.id,
                "component_ids": [
                    (
                        0,
                        0,
                        {
                            "component_type": "part",
                            "notes": "Screen assembly",
                            "quantity": 1.0,
                            "standard_cost": 1200.0,
                        },
                    )
                ],
            }
        )

    def test_a_component_must_identify_itself(self, env):
        """The live seed kit has a component with no product and no
        description, which is why its cost and time both read zero."""
        kit = self._kit(env)
        with pytest.raises(ValidationError, match="identifies\\s+nothing"):
            env["fix.service.kit.component"].create(
                {"kit_id": kit.id, "component_type": "part", "quantity": 1.0}
            )

    def test_a_component_needs_a_positive_quantity(self, env):
        kit = self._kit(env)
        with pytest.raises(ValidationError, match="positive quantity"):
            env["fix.service.kit.component"].create(
                {"kit_id": kit.id, "component_type": "part", "notes": "x", "quantity": 0.0}
            )

    def test_a_kit_with_costed_components_is_costed(self, env):
        assert self._kit(env).is_costed is True

    def test_a_kit_whose_components_carry_nothing_is_not_costed(self, env):
        kit = self._kit(env)
        kit.component_ids.write({"standard_cost": 0.0, "time_allocation": 0.0})
        kit.invalidate_recordset()
        assert kit.is_costed is False

    def test_component_count_reflects_the_lines(self, env):
        kit = self._kit(env)
        assert kit.component_count == 1
