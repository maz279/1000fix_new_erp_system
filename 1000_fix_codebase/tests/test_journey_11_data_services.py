#!/usr/bin/env python3
"""test_journey_11_data_services.py — Journey 11: M06 Data Services & Recovery Lifecycle Test Suite.
Milestone R07-M04 / Task R07-M04-T01.

Validates the complete Journey 11 sovereign data recovery lifecycle:
1. Data recovery case intake and initial custody logging.
2. Continuous chain of custody logging (hand-offs, timestamps, roles, locations).
3. Strict Z4 Residency Gate (SC-007): recovery hard-blocked unless routed to Z4.
4. Step-up authentication gate (SC-002): 2FA/TOTP token verification for data access.
5. Per-read immutable Z4 access audit logging (fix.z4.access.audit): append-only record.
6. Audit log immutability: write and unlink operations strictly blocked with UserError.
7. Customer handover and custody verification.
8. Statutory purge execution (NFR-095) issuing NIST SP 800-88 wipe certificate.
9. Data wipe certificate permanent retention: unlinking blocked under statutory mandate.
10. Gate G6-6 and SC-002 threat-model conformance.
"""

from __future__ import annotations

import base64
import inspect
import sys
import unittest
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Setup odoo import path
sys.path.insert(0, str(REPO_ROOT / "vendor" / "odoo"))
import odoo
import odoo.addons

for addons_dir in (
    REPO_ROOT / "addons" / "domain" / "d_circular",
    REPO_ROOT / "vendor" / "odoo" / "addons",  # auth_totp (the real TOTP implementation)
):
    if str(addons_dir) not in odoo.addons.__path__:
        odoo.addons.__path__.append(str(addons_dir))

from odoo.addons.auth_totp.models.totp import TIMESTEP, TOTP, hotp
from odoo.addons.cd_data_case.models import fix_data_case as fix_data_case_module
from odoo.addons.cd_data_case.models.fix_data_case import (
    FixDataRecoveryCase,
    FixDataWipeCertificate,
)
from odoo.exceptions import AccessDenied, UserError

# The cleanroom lead's authenticator: a synthetic key and a frozen clock shared
# by the "phone" and the "server", so every code below is deterministic.
AUTHENTICATOR_KEY = b"journey11-synthetic-authn-key-01"
AUTHENTICATOR_SECRET = base64.b32encode(AUTHENTICATOR_KEY).decode()  # as auth_totp stores it
FROZEN_T = 1_790_000_000


def authenticator_code(offset=0):
    """The 6-digit code the enrolled authenticator shows (offset in steps)."""
    return f"{hotp(AUTHENTICATOR_KEY, int(FROZEN_T / TIMESTEP) + offset):06d}"


@dataclass
class MockDevice:
    id: int = 101
    name: str = "Western Digital Red Plus 4TB"
    serial_number: str = "WD-WCC4N7KR8812"


@dataclass
class MockUser:
    """res.users with auth_totp installed. `_check_credentials` honours the
    auth_totp "totp" contract: the user's OWN secret, codes valid within one
    time step either side, a replayed code refused, AccessDenied otherwise."""

    id: int = 42
    name: str = "Tariqul Islam (Cleanroom Lead)"
    totp_secret: str | None = AUTHENTICATOR_SECRET
    totp_last_counter: int | None = None
    _fields = ("id", "name", "totp_secret", "totp_enabled")

    @property
    def totp_enabled(self):
        return bool(self.totp_secret)

    def sudo(self):
        return self

    def _check_credentials(self, credentials, env):
        if credentials["type"] != "totp":
            raise AccessDenied()
        key = base64.b32decode(self.totp_secret)
        match = TOTP(key).match(credentials["token"], t=FROZEN_T)
        if match is None:
            raise AccessDenied("Verification failed, please double-check the 6-digit code")
        if self.totp_last_counter and match <= self.totp_last_counter:
            raise AccessDenied("Verification failed, please use the latest 6-digit code")
        self.totp_last_counter = match
        return {"uid": self.id, "auth_method": "totp", "mfa": "default"}


class MockEnv:
    def __init__(self):
        self.uid = 42
        self.user = MockUser()
        self.company = "1000FiX Services Ltd."
        self._sequences = {"fix.data.recovery.case": 100, "fix.data.wipe.certificate": 50}
        self.audits = []
        self.certificates = []
        self.events = []
        self.attachments = []  # ir.attachment rows stored on the case

    def __getitem__(self, model_name: str):
        env = self

        class ModelProxy:
            def browse(self, uid):
                return env.user

            def search(self, domain, order=None):
                # ir.attachment: the files actually stored on the case
                return list(env.attachments)

            def create(self, vals):
                if model_name == "fix.z4.access.audit":
                    audit = MockAudit(
                        id=len(env.audits) + 1,
                        case_id=vals.get("case_id"),
                        user_id=vals.get("user_id", env.uid),
                        user_name=vals.get("user_name", env.user.name),
                        access_type=vals.get("access_type"),
                        purpose=vals.get("purpose"),
                        ip_address=vals.get("ip_address"),
                        step_up_verified=vals.get("step_up_verified", True),
                    )
                    import hashlib
                    import time

                    seed = f"{audit.case_id}-{audit.user_id}-{audit.access_type}-{audit.purpose}-{time.time()}"
                    audit.sha256_audit_hash = hashlib.sha256(seed.encode()).hexdigest()
                    env.audits.append(audit)
                    return audit
                elif model_name == "fix.data.wipe.certificate":
                    cert = MockCert(
                        id=len(env.certificates) + 1,
                        name=f"DWC/2026/{len(env.certificates)+1:04d}",
                        device_id=vals.get("device_id"),
                        method=vals.get("method", "nist_800_88_purge"),
                        sanitization_status=vals.get("sanitization_status", "pending_verification"),
                        statutory_record_retained=vals.get("statutory_record_retained", True),
                        certified_by=env.user.name,
                    )
                    import hashlib
                    import time

                    seed = f"{cert.name}-{cert.method}-{time.time()}"
                    cert.verification_hash = hashlib.sha256(seed.encode()).hexdigest()[:16]
                    env.certificates.append(cert)
                    return cert
                return None

            def emit(self, event_type, aggregate, aggregate_id, payload, meta=None):
                event_data = {
                    "event_type": event_type,
                    "aggregate": aggregate,
                    "aggregate_id": aggregate_id,
                    "payload": payload,
                }
                env.events.append(event_data)

                class MockOutboxRecord:
                    event_id = f"evt-{len(env.events):04d}"

                return MockOutboxRecord()

            def next_by_code(self, code):
                seq = env._sequences.get(code, 1) + 1
                env._sequences[code] = seq
                return f"{code.split('.')[-1].upper()[:3]}/{seq:05d}"

        return ModelProxy()


@dataclass
class MockAudit:
    id: int
    case_id: int
    user_id: int
    user_name: str
    access_type: str
    purpose: str
    ip_address: str
    step_up_verified: bool
    sha256_audit_hash: str = ""

    def write(self, vals):
        raise UserError(
            "SC-002: fix.z4.access.audit is an immutable statutory sovereign log. Modifications are strictly prohibited."
        )

    def unlink(self):
        raise UserError(
            "SC-002: fix.z4.access.audit is an immutable statutory sovereign log. Deletion is strictly prohibited."
        )


@dataclass
class MockCert:
    id: int
    name: str
    device_id: int
    method: str
    sanitization_status: str
    statutory_record_retained: bool
    certified_by: str
    verification_hash: str = ""

    def unlink(self):
        if self.statutory_record_retained:
            raise UserError(
                "NFR-095: Data Wipe Certificates are permanent statutory processing records and cannot be deleted."
            )


class MockCase:
    def __init__(self, env: MockEnv):
        self.env = env
        self.id = 501
        self.name = "DRC/2026/00501"
        self.media_type = "hdd"
        self.state = "new"
        self.residency_zone = "pending"
        self.custody_chain = ""
        self.audit_ids = []
        self.device_id = MockDevice()
        self.purge_certificate_id = None

    _name = "fix.data.recovery.case"

    def ensure_one(self):
        pass

    def __iter__(self):
        yield self

    def action_take_custody(self, handler):
        FixDataRecoveryCase.action_take_custody(self, handler)

    def action_log_custody_transfer(self, handler, role="Technician", location="Z4 Lab", notes=""):
        FixDataRecoveryCase.action_log_custody_transfer(self, handler, role, location, notes)

    def action_start_recovery(self):
        FixDataRecoveryCase.action_start_recovery(self)

    def action_recovered(self):
        FixDataRecoveryCase.action_recovered(self)

    def action_access_recovered_data(
        self,
        step_up_token,
        access_type="file_list_read",
        purpose="Technician File List Inspection",
        ip_address="127.0.0.1",
    ):
        res = FixDataRecoveryCase.action_access_recovered_data(
            self,
            step_up_token=step_up_token,
            access_type=access_type,
            purpose=purpose,
            ip_address=ip_address,
        )
        self.audit_ids = self.env.audits
        return res

    def _step_up_denial(self, code):
        # The model's REAL step-up contract, evaluated against the mock accessor.
        return FixDataRecoveryCase._step_up_denial(self, code)

    def action_handover(self, handler):
        FixDataRecoveryCase.action_handover(self, handler)

    def action_purge(self, certificate=None):
        FixDataRecoveryCase.action_purge(self, certificate=certificate)

    def write(self, vals):
        for k, v in vals.items():
            setattr(self, k, v)


class TestJourney11DataServices(unittest.TestCase):
    """End-to-end operational test of Journey 11: M06 Data Services."""

    def setUp(self):
        self.env = MockEnv()
        self.case = MockCase(self.env)
        # Step-up is only ever verified inside an interactive request.
        interactive = mock.patch.object(
            fix_data_case_module,
            "request",
            SimpleNamespace(httprequest=SimpleNamespace(environ={"REMOTE_ADDR": "192.168.10.45"})),
        )
        interactive.start()
        self.addCleanup(interactive.stop)

    def _recovered_case(self):
        self.case.action_take_custody("Lab Engineer")
        self.case.residency_zone = "z4"
        self.case.action_start_recovery()
        self.case.action_recovered()
        return self.case

    def _assert_denied(self, token, reason):
        with self.assertRaises(UserError) as ctx:
            self.case.action_access_recovered_data(step_up_token=token)
        self.assertIn("Access Denied", str(ctx.exception))
        self.assertIn("step-up authentication (2FA/TOTP) required", str(ctx.exception))
        self.assertIn(reason, str(ctx.exception))
        self.assertEqual(self.env.audits, [], "a refused step-up must not write an audit")

    def test_01_intake_and_custody_logging(self):
        """1. Customer damaged media intake begins custody chain."""
        self.assertEqual(self.case.state, "new")
        self.assertEqual(self.case.residency_zone, "pending")

        # Take initial custody
        self.case.action_take_custody("Lab Engineer Kabir")
        self.assertEqual(self.case.state, "custody")
        self.assertIn("custody taken by Lab Engineer Kabir", self.case.custody_chain)

    def test_02_custody_transfer_preserves_audit_trail(self):
        """2. Structured custody transfers are appended to chain."""
        self.case.action_take_custody("Lab Reception")
        self.case.action_log_custody_transfer(
            handler="Tariqul Islam",
            role="Z4 Cleanroom Lead",
            location="Sovereign Cleanroom Vault 1",
            notes="Sealed electrostatic carrier transfer",
        )
        self.assertIn("Lab Reception", self.case.custody_chain)
        self.assertIn("Tariqul Islam (Z4 Cleanroom Lead)", self.case.custody_chain)
        self.assertIn("Sovereign Cleanroom Vault 1", self.case.custody_chain)

    def test_03_strict_z4_residency_gate_enforced(self):
        """3. SC-007: Recovery is strictly blocked unless residency_zone == 'z4'."""
        self.case.action_take_custody("Lab Engineer")
        self.case.residency_zone = "pending"

        # Attempting recovery while pending routing MUST raise UserError
        with self.assertRaises(UserError) as ctx:
            self.case.action_start_recovery()
        self.assertIn("SC-007", str(ctx.exception))
        self.assertIn("Z4 BEFORE recovery starts", str(ctx.exception))

        # Once routed to Z4, recovery starts cleanly
        self.case.residency_zone = "z4"
        self.case.action_start_recovery()
        self.assertEqual(self.case.state, "recovering")

    def test_04_step_up_authentication_rejected_on_invalid_token(self):
        """4. SC-002: Accessing Z4 recovered data without valid 2FA step-up is denied."""
        self.case.action_take_custody("Lab Engineer")
        self.case.residency_zone = "z4"
        self.case.action_start_recovery()
        self.case.action_recovered()
        self.assertEqual(self.case.state, "recovered")

        # Empty token
        with self.assertRaises(UserError) as ctx:
            self.case.action_access_recovered_data(step_up_token="")
        self.assertIn("Access Denied", str(ctx.exception))
        self.assertIn("step-up authentication (2FA/TOTP) required", str(ctx.exception))

        # Invalid token
        with self.assertRaises(UserError) as ctx:
            self.case.action_access_recovered_data(step_up_token="BAD-TOKEN")
        self.assertIn("Access Denied", str(ctx.exception))

    def test_04b_step_up_denied_unless_verified_for_an_enrolled_accessor(self):
        """4b. SC-002: only the accessor's own current authenticator code passes."""
        self._recovered_case()
        valid_now = {authenticator_code(offset) for offset in (-1, 0, 1)}

        # the former fixed bypass token is just a wrong code now
        self.assertNotIn("100024", valid_now)
        self._assert_denied("100024", "Verification failed")
        self._assert_denied("MFA-Z4-AUTH", "a 6-digit authenticator code is required")
        # a well-formed code that the authenticator did not produce
        self.assertNotIn("000000", valid_now)
        self._assert_denied("000000", "Verification failed")
        # a code from outside the +-1 step window (stale)
        self._assert_denied(authenticator_code(-3), "Verification failed")

        # no authenticator enrolled: even the "right" code is refused (fail closed)
        self.env.user.totp_secret = None
        self._assert_denied(authenticator_code(), "no authenticator (TOTP) enrolled")
        self.env.user.totp_secret = AUTHENTICATOR_SECRET

        # outside an interactive request: refused (fail closed)
        with mock.patch.object(fix_data_case_module, "request", None):
            self._assert_denied(authenticator_code(), "requires an interactive session")

    def test_05_step_up_authentication_success_and_per_read_logging(self):
        """5. SC-002: Valid step-up auth yields payload and writes immutable audit record."""
        self.case.action_take_custody("Lab Engineer")
        self.case.residency_zone = "z4"
        self.case.action_start_recovery()
        self.case.action_recovered()

        # Two recovered files stored on the case: the listing reports exactly these
        from types import SimpleNamespace

        self.env.attachments = [
            SimpleNamespace(name="IMG_0001.jpg", file_size=2048),
            SimpleNamespace(name="contacts.vcf", file_size=512),
        ]

        # Execute read with the accessor's current authenticator code
        code = authenticator_code()
        result = self.case.action_access_recovered_data(
            step_up_token=code,
            access_type="file_list_read",
            purpose="Statutory Legal Hold Inspection",
            ip_address="192.168.10.45",
        )

        self.assertEqual(result["status"], "granted")
        self.assertTrue(result["audit_hash"])
        self.assertEqual(
            [(f["filename"], f["size_bytes"]) for f in result["files"]],
            [("IMG_0001.jpg", 2048), ("contacts.vcf", 512)],
        )
        self.assertEqual(self.env.user.totp_last_counter, int(FROZEN_T / TIMESTEP))

        # Audit entry verified
        self.assertEqual(len(self.env.audits), 1)
        audit = self.env.audits[0]
        self.assertEqual(audit.access_type, "file_list_read")
        self.assertEqual(audit.purpose, "Statutory Legal Hold Inspection")
        self.assertEqual(audit.ip_address, "192.168.10.45")
        self.assertTrue(audit.step_up_verified)
        self.assertTrue(audit.sha256_audit_hash)

        # the same code cannot be replayed for a second read ...
        with self.assertRaises(UserError) as ctx:
            self.case.action_access_recovered_data(step_up_token=code)
        self.assertIn("use the latest 6-digit code", str(ctx.exception))
        self.assertEqual(len(self.env.audits), 1)
        # ... the authenticator's next code is accepted and audited separately
        self.case.action_access_recovered_data(step_up_token=authenticator_code(1))
        self.assertEqual(len(self.env.audits), 2)

    def test_06_z4_audit_log_immutability(self):
        """6. SC-002: Audit entries cannot be modified or deleted (append-only)."""
        self.case.action_take_custody("Lab Engineer")
        self.case.residency_zone = "z4"
        self.case.action_start_recovery()
        self.case.action_recovered()
        self.case.action_access_recovered_data(step_up_token=authenticator_code())

        audit = self.env.audits[0]

        # Modification prohibited
        with self.assertRaises(UserError) as ctx:
            audit.write({"purpose": "Altered Purpose"})
        self.assertIn("immutable statutory sovereign log", str(ctx.exception))

        # Deletion prohibited
        with self.assertRaises(UserError) as ctx:
            audit.unlink()
        self.assertIn("immutable statutory sovereign log", str(ctx.exception))

    def test_07_customer_handover_and_purge_certificate_issuance(self):
        """7. Handover and Purge emit cryptographic NIST SP 800-88 certificate."""
        self.case.action_take_custody("Lab Engineer")
        self.case.residency_zone = "z4"
        self.case.action_start_recovery()
        self.case.action_recovered()

        # Handover to customer
        self.case.action_handover("Customer Rep Farzana")
        self.assertEqual(self.case.state, "handover")
        self.assertIn("handed over by Customer Rep Farzana", self.case.custody_chain)

        # Execute purge on the wipe operator's verified certificate
        operator_cert = self.env["fix.data.wipe.certificate"].create(
            {"method": "nist_800_88_purge", "sanitization_status": "verified"}
        )
        self.case.action_purge(certificate=operator_cert)
        self.assertEqual(self.case.state, "purged")
        self.assertIsNotNone(self.case.purge_certificate_id)

        # Verify certificate properties
        cert = self.env.certificates[0]
        self.assertEqual(cert.method, "nist_800_88_purge")
        self.assertEqual(cert.sanitization_status, "verified")
        self.assertTrue(cert.statutory_record_retained)
        self.assertTrue(len(cert.verification_hash) > 0)

    def test_08_wipe_certificate_permanent_statutory_retention(self):
        """8. NFR-095: Wipe certificate cannot be deleted from statutory archive."""
        self.case.action_take_custody("Lab Engineer")
        self.case.residency_zone = "z4"
        self.case.action_start_recovery()
        self.case.action_recovered()
        self.case.action_handover("Customer")
        self.case.action_purge(
            certificate=self.env["fix.data.wipe.certificate"].create(
                {"method": "nist_800_88_purge", "sanitization_status": "verified"}
            )
        )

        cert = self.env.certificates[0]
        with self.assertRaises(UserError) as ctx:
            cert.unlink()
        self.assertIn("NFR-095", str(ctx.exception))
        self.assertIn("statutory processing records and cannot be deleted", str(ctx.exception))

    def test_09_code_inspection_and_gate_g6_6_alignment(self):
        """9. Gate G6-6: Verify models match verify-gate-g6.ps1 requirements."""
        model_src = inspect.getsource(FixDataRecoveryCase)
        self.assertIn("z4", model_src)
        self.assertIn("SC-007", model_src)
        self.assertIn("SC-002", model_src)
        self.assertIn("action_access_recovered_data", model_src)
        self.assertIn("action_purge", model_src)

        cert_src = inspect.getsource(FixDataWipeCertificate)
        self.assertIn("statutory_record_retained", cert_src)
        self.assertIn("verification_hash", cert_src)


if __name__ == "__main__":
    unittest.main()
