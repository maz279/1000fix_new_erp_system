# R5 scheduled branded report delivery — behavioural tests on the live ORM
# (`odoo_env`, rolled back per test). The delivery uses the SAME shared
# byte-builders as the download buttons (report_bytes), so these also pin
# that the scheduled artefact is the branded artefact.
from __future__ import annotations

import base64

import pytest
from odoo.exceptions import ValidationError


@pytest.fixture()
def subscription(odoo_env):
    return odoo_env["fix.report.subscription"].create(
        {
            "name": "Close pack — weekly",
            "module_key": "M19",
            "report_key": "close_sla",
            "format": "pdf",
            "recipients": "close-team@example.com, cfo@example.com",
            "period": "weekly",
        }
    )


class TestScheduledDelivery:
    def test_pack_must_exist(self, odoo_env):
        with pytest.raises(ValidationError):
            odoo_env["fix.report.subscription"].create(
                {
                    "name": "bad",
                    "module_key": "M19",
                    "report_key": "no_such_pack",
                    "recipients": "a@example.com",
                }
            )

    def test_recipients_validated(self, odoo_env):
        with pytest.raises(ValidationError):
            odoo_env["fix.report.subscription"].create(
                {
                    "name": "bad emails",
                    "module_key": "M19",
                    "report_key": "close_sla",
                    "recipients": "not-an-email",
                }
            )

    def test_delivery_creates_branded_mail_with_attachment(self, odoo_env, subscription):
        result = subscription.action_deliver_now()
        assert result["attachment"] == "M19_close_sla.pdf"
        assert result["rows"] >= 0  # the pack renders whatever the close state holds
        mail = odoo_env["mail.mail"].browse(result["mail_id"])
        assert "close-team@example.com" in (mail.email_to or "")
        assert mail.attachment_ids, "the branded pack must be attached"
        att = mail.attachment_ids[0]
        data = base64.b64decode(att.datas)
        assert data[:4] == b"%PDF"
        # the artefact carries the official letterhead
        import io

        # PyPDF2 ships with Odoo's own requirements; pymupdf was never a
        # declared dependency, so this assertion could not run anywhere clean
        from PyPDF2 import PdfReader

        text = "".join(page.extract_text() or "" for page in PdfReader(io.BytesIO(data)).pages)
        # brand constants (company record may differ between databases); the
        # company-document letterhead (report_pdf.py, 12 Nov) prints
        # "<ISO line> · Hotline 16743" on every page
        assert "Hotline 16743" in text, text[:400]
        assert "ISO 9001:2015" in text, text[:400]
        assert subscription.last_state and subscription.delivery_count == 1

    def test_xlsx_format_delivery(self, odoo_env, subscription):
        subscription.write({"format": "xlsx"})
        result = subscription.action_deliver_now()
        assert result["attachment"] == "M19_close_sla.xlsx"
        att = odoo_env["mail.mail"].browse(result["mail_id"]).attachment_ids[0]
        data = base64.b64decode(att.datas)
        assert data[:2] == b"PK"

    def test_cron_delivers_due_and_reschedules(self, odoo_env, subscription):
        import datetime

        from odoo import fields as odoo_fields

        # force due now
        subscription.write({"next_run": odoo_fields.Datetime.now() - datetime.timedelta(hours=1)})
        Subs = odoo_env["fix.report.subscription"]
        sent = Subs.action_deliver_due()
        assert sent >= 1
        subscription.invalidate_recordset()
        assert subscription.delivery_count >= 1
        assert subscription.next_run > odoo_fields.Datetime.now()
        # a not-due subscription is not touched
        far = odoo_env["fix.report.subscription"].create(
            {
                "name": "far future",
                "module_key": "M19",
                "report_key": "close_sla",
                "recipients": "a@example.com",
                "period": "monthly",
                "next_run": odoo_fields.Datetime.now() + datetime.timedelta(days=20),
            }
        )
        far.write({"next_run": odoo_fields.Datetime.now() + datetime.timedelta(days=20)})
        before = far.delivery_count
        Subs.action_deliver_due()
        far.invalidate_recordset()
        assert far.delivery_count == before
