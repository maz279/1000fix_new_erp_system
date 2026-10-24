"""sso_federation.py — INT-046: Corporate Client SSO Federation Broker (W6).

Implements Keycloak identity brokering across SAML 2.0 and OIDC for corporate B2B clients
(e.g., Grameenphone, Robi Axiata, Walton, Standard Chartered Bangladesh).
Validates federated identity assertions, resolves tenant scopes, and maps corporate roles
into 1000FiX P04 / M29 access tokens.

Trust material is configuration, never code: OIDC client secrets and the SAML IdP
signing certificate (with its SHA-256 pin) come from the tenant profile or the
environment variables it names (see services/corporate-sso/.env.example). A tenant
whose trust material is missing or inconsistent cannot log in at all (fail closed).
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
from datetime import UTC, datetime
from typing import Any

from cryptography import x509
from cryptography.hazmat.primitives import hashes
from lxml import etree
from signxml import SignatureConfiguration, SignatureMethod, XMLVerifier
from signxml.exceptions import SignXMLException

#: JWS algorithms a tenant shared secret can verify (RFC 7518 §3.2). The JOSE
#: header is attacker-controlled, so the algorithm is never taken from it: the
#: header must name one of the tenant's expected algorithms (default HS256),
#: and "none" / RS* / ES* / PS* (alg-confusion) are always refused.
HMAC_JWT_ALGORITHMS: dict[str, Any] = {
    "HS256": hashlib.sha256,
    "HS384": hashlib.sha384,
    "HS512": hashlib.sha512,
}
DEFAULT_JWT_ALGORITHMS: tuple[str, ...] = ("HS256",)
#: RFC 7519 §5.1 - "JWT" is the only media type an OIDC ID token carries.
EXPECTED_JWT_TYP = "JWT"

SAML2_ASSERTION_NS = "urn:oasis:names:tc:SAML:2.0:assertion"
_SAML_NS = {"saml": SAML2_ASSERTION_NS}
#: Tolerated IdP/SP clock drift when checking NotBefore / NotOnOrAfter.
SAML_CLOCK_SKEW_SECONDS = 60
#: Asymmetric XML-DSig algorithms accepted on SAML assertions (no SHA-1, no HMAC, no DSA).
SAML_SIGNATURE_METHODS = frozenset(
    {
        SignatureMethod.RSA_SHA256,
        SignatureMethod.RSA_SHA384,
        SignatureMethod.RSA_SHA512,
        SignatureMethod.ECDSA_SHA256,
        SignatureMethod.ECDSA_SHA384,
        SignatureMethod.ECDSA_SHA512,
    }
)


class SsoFederationError(Exception):
    """Base exception for SSO federation failures."""

    pass


class TokenValidationError(SsoFederationError):
    """Raised when SAML assertion or OIDC JWT fails validation."""

    pass


class TenantResolutionError(SsoFederationError):
    """Raised when client tenant cannot be mapped to an authorized realm."""

    pass


class FederationConfigurationError(SsoFederationError):
    """Raised when a tenant's trust material (secret / certificate / pin) is missing or invalid.

    Federation fails CLOSED: no login is possible for that tenant until it is fixed.
    """

    pass


def _hardened_xml_parser() -> etree.XMLParser:
    """No entity expansion, no DTD loading, no network access (XXE / billion-laughs)."""
    return etree.XMLParser(resolve_entities=False, load_dtd=False, no_network=True)


def _saml_instant(value: str) -> float:
    """xs:dateTime (UTC 'Z', offset, or naive = UTC per SAML core §1.3.3) -> epoch seconds."""
    try:
        moment = datetime.fromisoformat(value.strip())
    except ValueError as exc:
        raise TokenValidationError(f"Invalid SAML timestamp {value!r}.") from exc
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=UTC)
    return moment.timestamp()


class CorporateSsoBroker:
    """INT-046: Corporate SSO identity federation broker."""

    def __init__(
        self,
        keycloak_issuer: str = "https://auth.1000fix.com/realms/fix-corporate",
        sp_entity_id: str | None = None,
    ):
        self.keycloak_issuer = keycloak_issuer
        #: Our SAML service-provider entity ID - the Audience every assertion must name.
        self.sp_entity_id = sp_entity_id or keycloak_issuer
        # Authoritative corporate client tenant registry. Secrets and certificates are
        # referenced by environment-variable NAME (`<setting>_env`), never inlined.
        self._tenants: dict[str, dict[str, Any]] = {
            "TENANT-GP": {
                "name": "Grameenphone Ltd.",
                "protocol": "SAML2",
                "idp_entity_id": "https://idp.grameenphone.com/adfs/services/trust",
                "idp_cert_pem_env": "FIX_SSO_GP_IDP_CERT_PEM",
                "cert_fingerprint_env": "FIX_SSO_GP_IDP_CERT_SHA256",
                "role_mapping": {
                    "GP-Fleet-Admin": "corporate_admin",
                    "GP-Procurement": "corporate_buyer",
                    "GP-Staff": "corporate_employee",
                },
                "status": "active",
            },
            "TENANT-ROBI": {
                "name": "Robi Axiata Ltd.",
                "protocol": "OIDC",
                "idp_issuer": "https://sso.robi.com.bd/oauth2/v1",
                "client_id": "1000fix-corporate-b2b",
                "shared_secret_env": "FIX_SSO_ROBI_SHARED_SECRET",
                "role_mapping": {
                    "AssetManager": "corporate_admin",
                    "DeviceUser": "corporate_employee",
                },
                "status": "active",
            },
            "TENANT-WALTON": {
                "name": "Walton Micro-Tech Corp",
                "protocol": "OIDC",
                "idp_issuer": "https://auth.waltonbd.com",
                "client_id": "1000fix-walton-oem",
                "shared_secret_env": "FIX_SSO_WALTON_SHARED_SECRET",
                "role_mapping": {
                    "OEM-Service-Lead": "corporate_admin",
                    "Quality-Auditor": "corporate_auditor",
                },
                "status": "active",
            },
        }

    def register_tenant(self, tenant_id: str, config: dict[str, Any]) -> None:
        """Dynamically onboard or update a corporate client federation profile."""
        self._tenants[tenant_id] = config

    def get_tenant(self, tenant_id: str) -> dict[str, Any]:
        """Fetch tenant profile with error handling."""
        if tenant_id not in self._tenants:
            raise TenantResolutionError(
                f"Corporate tenant '{tenant_id}' not enrolled in INT-046 registry."
            )
        tenant = self._tenants[tenant_id]
        if tenant.get("status") != "active":
            raise TenantResolutionError(
                f"Corporate tenant '{tenant_id}' is suspended or decommissioned."
            )
        return tenant

    @staticmethod
    def _tenant_setting(tenant: dict[str, Any], key: str) -> str:
        """A trust setting from the profile itself, else from the env var it names."""
        value = tenant.get(key)
        if not value and tenant.get(f"{key}_env"):
            value = os.environ.get(tenant[f"{key}_env"], "")
        return str(value or "").strip()

    def _oidc_secret(self, tenant_id: str, tenant: dict[str, Any], digestmod: Any) -> bytes:
        """The tenant's HMAC key; RFC 7518 §3.2 - at least as long as the hash output."""
        secret = self._tenant_setting(tenant, "shared_secret").encode("utf-8")
        minimum = digestmod().digest_size
        if len(secret) < minimum:
            source = tenant.get("shared_secret_env", "shared_secret")
            raise FederationConfigurationError(
                f"OIDC tenant '{tenant_id}' has no usable client secret configured "
                f"(set {source}; at least {minimum} bytes) - login refused."
            )
        return secret

    def authenticate_oidc(self, tenant_id: str, id_token: str) -> dict[str, Any]:
        """Validate an OIDC ID token from a client IdP and issue a 1000FiX corporate token."""
        tenant = self.get_tenant(tenant_id)
        if tenant.get("protocol") != "OIDC":
            raise TokenValidationError(
                f"Tenant '{tenant_id}' is configured for {tenant.get('protocol')}, not OIDC."
            )

        try:
            parts = id_token.split(".")
            if len(parts) != 3:
                raise TokenValidationError(
                    "Invalid JWT structure: must contain header, payload, and signature."
                )

            header = json.loads(base64.urlsafe_b64decode(parts[0] + "==").decode("utf-8"))
            digestmod = self._verify_jose_header(tenant, header)
            secret = self._oidc_secret(tenant_id, tenant, digestmod)
            payload = json.loads(base64.urlsafe_b64decode(parts[1] + "==").decode("utf-8"))
            if not isinstance(payload, dict):
                raise TokenValidationError("Invalid JWT payload: claims must be a JSON object.")
            sig = parts[2]

            # Verify signature using tenant shared secret and the EXPECTED algorithm
            expected_sig = (
                base64.urlsafe_b64encode(
                    hmac.new(secret, f"{parts[0]}.{parts[1]}".encode(), digestmod).digest()
                )
                .decode("utf-8")
                .rstrip("=")
            )

            # Constant-time comparison: a short-circuiting `!=` leaks how many
            # leading signature characters an attacker has guessed correctly.
            if not hmac.compare_digest(sig.encode("utf-8"), expected_sig.encode("utf-8")):
                raise TokenValidationError("Cryptographic signature mismatch on OIDC assertion.")

            # Validate claims
            now = time.time()
            if payload.get("exp", 0) < now:
                raise TokenValidationError("OIDC token has expired.")
            if payload.get("iss") != tenant.get("idp_issuer"):
                raise TokenValidationError(
                    f"Issuer mismatch: expected {tenant.get('idp_issuer')}, got {payload.get('iss')}"
                )
            # OIDC Core 1.0 §3.1.3.7(3): the ID token must be addressed to this client.
            client_id = tenant.get("client_id")
            audience = payload.get("aud")
            audiences = audience if isinstance(audience, list) else [audience]
            if not client_id or client_id not in audiences:
                raise TokenValidationError(
                    f"Audience mismatch: token not issued for client {client_id}."
                )

            # Map roles
            client_roles = payload.get("roles", [])
            mapped_roles = [
                tenant["role_mapping"][r] for r in client_roles if r in tenant["role_mapping"]
            ]
            if not mapped_roles:
                mapped_roles = ["corporate_employee"]

            return self._mint_fix_session(
                tenant_id=tenant_id,
                tenant_name=tenant["name"],
                subject=payload.get("sub", ""),
                email=payload.get("email", ""),
                roles=mapped_roles,
                auth_method="oidc_federation",
            )
        except Exception as e:
            if isinstance(e, SsoFederationError):
                raise
            raise TokenValidationError(f"Failed to parse OIDC assertion: {e!s}") from e

    @staticmethod
    def _verify_jose_header(tenant: dict[str, Any], header: Any) -> Any:
        """Validate the JOSE header and return the HMAC digest for the expected algorithm.

        The header is attacker-controlled, so it can only *select among* the algorithms the
        tenant is configured to accept - it can never introduce one ("none", or RS256 with
        the shared secret used as a public key = algorithm confusion).
        """
        if not isinstance(header, dict):
            raise TokenValidationError("Invalid JWT header: must be a JSON object.")
        typ = header.get("typ")
        if not isinstance(typ, str) or typ.upper() != EXPECTED_JWT_TYP:
            raise TokenValidationError(
                f"Unsupported JWT type {typ!r}: expected {EXPECTED_JWT_TYP!r}."
            )
        if "crit" in header:
            # RFC 7515 §4.1.11: critical extensions we do not understand must be refused.
            raise TokenValidationError("Unsupported critical JWT header extensions.")
        alg = header.get("alg")
        expected = tenant.get("jwt_algorithms", DEFAULT_JWT_ALGORITHMS)
        if not isinstance(alg, str) or alg not in expected or alg not in HMAC_JWT_ALGORITHMS:
            raise TokenValidationError(
                f"Unsupported JWT algorithm {alg!r}: expected one of {sorted(expected)}."
            )
        return HMAC_JWT_ALGORITHMS[alg]

    # ------------------------------------------------------------------ SAML 2.0

    def _idp_signing_cert(self, tenant_id: str, tenant: dict[str, Any]) -> str:
        """The tenant's IdP signing certificate (PEM), checked against its SHA-256 pin."""
        pem = self._tenant_setting(tenant, "idp_cert_pem")
        pin = self._tenant_setting(tenant, "cert_fingerprint")
        if not pem or not pin:
            raise FederationConfigurationError(
                f"SAML tenant '{tenant_id}' has no IdP signing certificate and SHA-256 "
                "fingerprint configured - SAML login is disabled for it (fail closed)."
            )
        try:
            cert = x509.load_pem_x509_certificate(pem.encode("ascii"))
        except ValueError as exc:
            raise FederationConfigurationError(
                f"SAML tenant '{tenant_id}': configured IdP certificate is not a PEM X.509 "
                "certificate."
            ) from exc
        actual = cert.fingerprint(hashes.SHA256()).hex().upper()
        expected = pin.replace(":", "").replace(" ", "").upper()
        if not hmac.compare_digest(actual.encode("ascii"), expected.encode("utf-8")):
            raise FederationConfigurationError(
                f"SAML tenant '{tenant_id}': configured IdP certificate does not match the "
                "pinned SHA-256 fingerprint."
            )
        return pem

    @staticmethod
    def _verified_assertion(saml_xml: str | bytes, cert_pem: str) -> Any:
        """Verify the XML signature and return ONLY the signed <saml:Assertion> element.

        Everything downstream reads from the element signxml returns - never from the
        submitted document - so a forged assertion wrapped around (or next to) a
        genuinely signed one is never consumed (XML signature wrapping).
        """
        data = saml_xml.encode("utf-8") if isinstance(saml_xml, str) else saml_xml
        # Hardened parser: no entity expansion, no DTD, no network; DOCTYPE refused below.
        root = etree.fromstring(data, parser=_hardened_xml_parser())  # noqa: S320 - hardened parser above
        if root.getroottree().docinfo.doctype:
            raise TokenValidationError("SAML payload must not contain a DOCTYPE declaration.")
        result = XMLVerifier().verify(
            root,
            x509_cert=cert_pem,
            parser=_hardened_xml_parser(),
            expect_config=SignatureConfiguration(
                signature_methods=SAML_SIGNATURE_METHODS, expect_references=1
            ),
        )
        signed = result.signed_xml
        if signed is None or signed.tag != f"{{{SAML2_ASSERTION_NS}}}Assertion":
            raise TokenValidationError(
                "The XML signature does not cover a SAML 2.0 Assertion - only a signed "
                "Assertion is accepted."
            )
        return signed

    def _check_assertion_conditions(
        self, tenant: dict[str, Any], assertion: Any, request_id: str | None
    ) -> None:
        """Issuer, validity window, audience, recipient and InResponseTo of the signed assertion."""
        issuer = (assertion.findtext("saml:Issuer", namespaces=_SAML_NS) or "").strip()
        if issuer != tenant["idp_entity_id"]:
            raise TokenValidationError(f"SAML Issuer mismatch: expected {tenant['idp_entity_id']}.")

        conditions = assertion.find("saml:Conditions", namespaces=_SAML_NS)
        confirmation = assertion.find(
            "saml:Subject/saml:SubjectConfirmation/saml:SubjectConfirmationData",
            namespaces=_SAML_NS,
        )
        bounded = [e for e in (conditions, confirmation) if e is not None]
        not_before = [_saml_instant(e.get("NotBefore")) for e in bounded if e.get("NotBefore")]
        not_after = [_saml_instant(e.get("NotOnOrAfter")) for e in bounded if e.get("NotOnOrAfter")]
        if not not_after:
            raise TokenValidationError("SAML assertion carries no NotOnOrAfter validity bound.")
        now = time.time()
        if any(now + SAML_CLOCK_SKEW_SECONDS < moment for moment in not_before):
            raise TokenValidationError("SAML assertion is not yet valid (NotBefore).")
        if any(now - SAML_CLOCK_SKEW_SECONDS >= moment for moment in not_after):
            raise TokenValidationError("SAML assertion has expired (NotOnOrAfter).")

        audiences = {
            (a.text or "").strip()
            for a in assertion.iterfind(
                "saml:Conditions/saml:AudienceRestriction/saml:Audience", namespaces=_SAML_NS
            )
        }
        sp_entity_id = tenant.get("sp_entity_id") or self.sp_entity_id
        if sp_entity_id not in audiences:
            raise TokenValidationError(
                f"SAML Audience mismatch: assertion is not addressed to {sp_entity_id}."
            )

        recipient = confirmation.get("Recipient") if confirmation is not None else None
        acs_url = tenant.get("acs_url")
        if acs_url and recipient != acs_url:
            raise TokenValidationError(f"SAML Recipient mismatch: expected {acs_url}.")
        in_response_to = confirmation.get("InResponseTo") if confirmation is not None else None
        if request_id is not None and in_response_to != request_id:
            raise TokenValidationError("SAML InResponseTo does not match the issued AuthnRequest.")

    @staticmethod
    def _saml_attribute(assertion: Any, name: str) -> str | None:
        """First value of the named attribute in the SIGNED assertion, or None."""
        for attribute in assertion.iterfind(
            "saml:AttributeStatement/saml:Attribute", namespaces=_SAML_NS
        ):
            if attribute.get("Name") == name:
                value = (
                    attribute.findtext("saml:AttributeValue", namespaces=_SAML_NS) or ""
                ).strip()
                return value or None
        return None

    def authenticate_saml(
        self, tenant_id: str, saml_assertion_xml: str | bytes, request_id: str | None = None
    ) -> dict[str, Any]:
        """Validate a signed SAML 2.0 assertion from a corporate IdP (e.g. ADFS/Azure AD).

        ``request_id`` is the ID of the AuthnRequest we issued (SP-initiated flow); when
        given, the assertion's SubjectConfirmationData/@InResponseTo must match it.
        """
        tenant = self.get_tenant(tenant_id)
        if tenant.get("protocol") != "SAML2":
            raise TokenValidationError(
                f"Tenant '{tenant_id}' is configured for {tenant.get('protocol')}, not SAML2."
            )
        cert_pem = self._idp_signing_cert(tenant_id, tenant)
        try:
            assertion = self._verified_assertion(saml_assertion_xml, cert_pem)
        except (SignXMLException, etree.LxmlError, ValueError) as exc:
            raise TokenValidationError(f"SAML signature verification failed: {exc}") from exc
        self._check_assertion_conditions(tenant, assertion, request_id)

        subject = (
            assertion.findtext("saml:Subject/saml:NameID", namespaces=_SAML_NS) or ""
        ).strip()
        if not subject:
            raise TokenValidationError("SAML assertion carries no Subject NameID.")
        email = self._saml_attribute(assertion, "email") or f"{subject}@{tenant_id.lower()}.com"
        role_raw = self._saml_attribute(assertion, "role") or ""
        mapped_role = tenant["role_mapping"].get(role_raw, "corporate_employee")

        return self._mint_fix_session(
            tenant_id=tenant_id,
            tenant_name=tenant["name"],
            subject=subject,
            email=email,
            roles=[mapped_role],
            auth_method="saml2_federation",  # gitleaks:allow - a label, not a secret
        )

    def _mint_fix_session(
        self,
        tenant_id: str,
        tenant_name: str,
        subject: str,
        email: str,
        roles: list[str],
        auth_method: str,
    ) -> dict[str, Any]:
        """Mints the internal 1000FiX Keycloak federated session descriptor."""
        session_id = hashlib.sha256(f"{tenant_id}:{subject}:{time.time()}".encode()).hexdigest()[
            :24
        ]
        return {
            "status": "authenticated",
            "session_id": f"sso-sess-{session_id}",
            "issuer": self.keycloak_issuer,
            "tenant_id": tenant_id,
            "tenant_name": tenant_name,
            "subject": subject,
            "email": email,
            "roles": roles,
            "auth_method": auth_method,
            "authenticated_at": int(time.time()),
            "expires_in": 28800,  # 8 hours corporate work session
            "p04_portal_access": True,
            "portal_redirect": f"https://portal.1000fix.com/corporate/{tenant_id.lower()}/dashboard",
        }
