"""Shared fixtures for the corporate-sso suites.

- OIDC client secrets come from the environment (never from code): every test gets
  test-only values in FIX_SSO_ROBI_SHARED_SECRET / FIX_SSO_WALTON_SHARED_SECRET.
- SAML: a throw-away test IdP (RSA-2048 key + self-signed certificate generated with
  ``cryptography``) signs assertions with signxml exactly as an ADFS/Azure AD IdP would;
  TENANT-GP is configured (via env) with that certificate and its SHA-256 pin.
  A second, unrelated "attacker" IdP produces validly-signed-but-untrusted assertions.
"""

from __future__ import annotations

import sys
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat
from cryptography.x509.oid import NameOID
from lxml import etree
from signxml import XMLSigner, methods

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

ROBI_SECRET = "test-only-robi-oidc-hmac-secret-0123456789abcdef"
WALTON_SECRET = "test-only-walton-oidc-hmac-secret-0123456789abcd"
GP_ISSUER = "https://idp.grameenphone.com/adfs/services/trust"
SP_ENTITY_ID = "https://auth.1000fix.com/realms/fix-corporate"
SAML_NS = "urn:oasis:names:tc:SAML:2.0:assertion"
SAMLP_NS = "urn:oasis:names:tc:SAML:2.0:protocol"
EXC_C14N = "http://www.w3.org/2001/10/xml-exc-c14n#"


def iso(offset_seconds: float) -> str:
    """xs:dateTime (UTC, 'Z') at now + offset."""
    moment = datetime.now(UTC) + timedelta(seconds=offset_seconds)
    return moment.strftime("%Y-%m-%dT%H:%M:%S.") + f"{moment.microsecond // 1000:03d}Z"


class TestIdp:
    """A SAML IdP with its own signing key and self-signed certificate."""

    __test__ = False  # not a pytest test class

    def __init__(self, common_name: str) -> None:
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, common_name)])
        now = datetime.now(UTC)
        cert = (
            x509.CertificateBuilder()
            .subject_name(name)
            .issuer_name(name)
            .public_key(key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(now - timedelta(days=1))
            .not_valid_after(now + timedelta(days=365))
            .sign(key, hashes.SHA256())
        )
        self.key_pem = key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())
        self.cert_pem = cert.public_bytes(Encoding.PEM).decode("ascii")
        self.sha256 = cert.fingerprint(hashes.SHA256()).hex().upper()

    @staticmethod
    def assertion(
        *,
        assertion_id: str = "_assert-1",
        issuer: str = GP_ISSUER,
        name_id: str | None = "gp_staff_1",
        attributes: dict[str, str] | None = None,
        audience: str | None = SP_ENTITY_ID,
        not_before: float | None = -30,
        not_on_or_after: float | None = 300,
        confirmation: dict[str, str] | None = None,
        with_conditions: bool = True,
    ) -> Any:
        """Build an (unsigned) <saml:Assertion>; offsets are seconds relative to now."""
        attrs = {"email": "staff1@grameenphone.com", "role": "GP-Staff"}
        if attributes is not None:
            attrs = attributes
        subject = ""
        if name_id is not None:
            subject += f"<saml:NameID>{name_id}</saml:NameID>"
        if confirmation is not None:
            data = " ".join(f'{k}="{v}"' for k, v in confirmation.items())
            subject += (
                '<saml:SubjectConfirmation Method="urn:oasis:names:tc:SAML:2.0:cm:bearer">'
                f"<saml:SubjectConfirmationData {data}/></saml:SubjectConfirmation>"
            )
        conditions = ""
        if with_conditions:
            bounds = ""
            if not_before is not None:
                bounds += f' NotBefore="{iso(not_before)}"'
            if not_on_or_after is not None:
                bounds += f' NotOnOrAfter="{iso(not_on_or_after)}"'
            restriction = (
                f"<saml:AudienceRestriction><saml:Audience>{audience}</saml:Audience>"
                "</saml:AudienceRestriction>"
                if audience is not None
                else ""
            )
            conditions = f"<saml:Conditions{bounds}>{restriction}</saml:Conditions>"
        statement = "".join(
            f'<saml:Attribute Name="{k}"><saml:AttributeValue>{v}</saml:AttributeValue>'
            "</saml:Attribute>"
            for k, v in attrs.items()
        )
        xml = (
            f'<saml:Assertion xmlns:saml="{SAML_NS}" ID="{assertion_id}" Version="2.0" '
            f'IssueInstant="{iso(0)}"><saml:Issuer>{issuer}</saml:Issuer>'
            f"<saml:Subject>{subject}</saml:Subject>{conditions}"
            f"<saml:AttributeStatement>{statement}</saml:AttributeStatement></saml:Assertion>"
        )
        return etree.fromstring(xml.encode("utf-8"))  # noqa: S320 - test-built XML

    def sign(self, element: Any, algorithm: str = "rsa-sha256") -> Any:
        """Enveloped, exclusive-c14n XML-DSig over the element (reference #ID)."""
        signer = XMLSigner(
            method=methods.enveloped,
            signature_algorithm=algorithm,
            digest_algorithm="sha256",
            c14n_algorithm=EXC_C14N,
        )
        return signer.sign(element, key=self.key_pem, cert=self.cert_pem)

    @staticmethod
    def response(*children: Any, response_id: str = "_resp-1") -> bytes:
        """Wrap assertion element(s) in a <samlp:Response> and serialise it."""
        root = etree.fromstring(  # noqa: S320 - test-built XML
            f'<samlp:Response xmlns:samlp="{SAMLP_NS}" xmlns:saml="{SAML_NS}" '
            f'ID="{response_id}" Version="2.0" IssueInstant="{iso(0)}">'
            f"<saml:Issuer>{GP_ISSUER}</saml:Issuer></samlp:Response>".encode()
        )
        for child in children:
            root.append(child)
        return etree.tostring(root)

    def signed_response(self, **assertion_kwargs: Any) -> bytes:
        return self.response(self.sign(self.assertion(**assertion_kwargs)))


@pytest.fixture(scope="session")
def idp() -> TestIdp:
    return TestIdp("adfs.test.grameenphone.example")


@pytest.fixture(scope="session")
def attacker_idp() -> TestIdp:
    return TestIdp("evil-idp.example")


@pytest.fixture(autouse=True)
def federation_trust(monkeypatch, idp) -> None:
    """Configure tenant trust material the way production does: through the environment."""
    monkeypatch.setenv("FIX_SSO_ROBI_SHARED_SECRET", ROBI_SECRET)
    monkeypatch.setenv("FIX_SSO_WALTON_SHARED_SECRET", WALTON_SECRET)
    monkeypatch.setenv("FIX_SSO_GP_IDP_CERT_PEM", idp.cert_pem)
    monkeypatch.setenv("FIX_SSO_GP_IDP_CERT_SHA256", idp.sha256)


@pytest.fixture
def now() -> float:
    return time.time()
