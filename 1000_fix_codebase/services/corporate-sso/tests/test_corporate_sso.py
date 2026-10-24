"""test_corporate_sso.py — Test suite for INT-046 Corporate Client SSO federation.

Trust material comes from the environment (tests/conftest.py ``federation_trust``):
OIDC client secrets and the Grameenphone IdP signing certificate + SHA-256 pin.
"""

import base64
import hashlib
import hmac
import json
import os
import sys
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sso_federation import (
    CorporateSsoBroker,
    TenantResolutionError,
    TokenValidationError,
)


class TestCorporateSso(unittest.TestCase):
    def setUp(self):
        self.broker = CorporateSsoBroker()

    def _create_mock_jwt(
        self,
        issuer: str,
        secret: str,
        sub: str,
        email: str,
        roles: list,
        exp_offset: int = 3600,
        aud: str = "1000fix-corporate-b2b",
    ):
        header = (
            base64.urlsafe_b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode("utf-8"))
            .decode("utf-8")
            .rstrip("=")
        )
        payload_data = {
            "iss": issuer,
            "aud": aud,
            "sub": sub,
            "email": email,
            "roles": roles,
            "exp": time.time() + exp_offset,
        }
        payload = (
            base64.urlsafe_b64encode(json.dumps(payload_data).encode("utf-8"))
            .decode("utf-8")
            .rstrip("=")
        )
        sig = (
            base64.urlsafe_b64encode(
                hmac.new(
                    secret.encode("utf-8"), f"{header}.{payload}".encode(), hashlib.sha256
                ).digest()
            )
            .decode("utf-8")
            .rstrip("=")
        )
        return f"{header}.{payload}.{sig}"

    def test_oidc_federation_robi_success(self):
        """Test Robi Axiata corporate OIDC login with role mapping to corporate_admin."""
        token = self._create_mock_jwt(
            issuer="https://sso.robi.com.bd/oauth2/v1",
            secret=os.environ["FIX_SSO_ROBI_SHARED_SECRET"],
            sub="robi_user_9921",
            email="sso.admin@robi.com.bd",
            roles=["AssetManager"],
        )
        session = self.broker.authenticate_oidc("TENANT-ROBI", token)
        self.assertEqual(session["status"], "authenticated")
        self.assertEqual(session["tenant_name"], "Robi Axiata Ltd.")
        self.assertIn("corporate_admin", session["roles"])
        self.assertTrue(session["p04_portal_access"])

    def test_oidc_expired_token_rejected(self):
        """Expired OIDC JWTs must be rejected immediately."""
        token = self._create_mock_jwt(
            issuer="https://sso.robi.com.bd/oauth2/v1",
            secret=os.environ["FIX_SSO_ROBI_SHARED_SECRET"],
            sub="robi_user_9921",
            email="sso.admin@robi.com.bd",
            roles=["AssetManager"],
            exp_offset=-100,  # Expired
        )
        with self.assertRaises(TokenValidationError):
            self.broker.authenticate_oidc("TENANT-ROBI", token)

    def test_unknown_tenant_rejected(self):
        """Unenrolled corporate domains must be rejected to prevent rogue federation."""
        with self.assertRaises(TenantResolutionError):
            self.broker.authenticate_oidc("TENANT-UNKNOWN", "invalid.jwt.token")


def test_saml_federation_grameenphone_success(idp):
    """Grameenphone ADFS SAML 2.0: a signed assertion from the pinned IdP certificate."""
    response = idp.signed_response(
        name_id="gp_lead_procure_842",
        attributes={"email": "farhan@grameenphone.com", "role": "GP-Procurement"},
    )
    session = CorporateSsoBroker().authenticate_saml("TENANT-GP", response.decode("utf-8"))
    assert session["status"] == "authenticated"
    assert session["tenant_name"] == "Grameenphone Ltd."
    assert session["subject"] == "gp_lead_procure_842"
    assert session["email"] == "farhan@grameenphone.com"
    assert session["roles"] == ["corporate_buyer"]


if __name__ == "__main__":
    unittest.main()
