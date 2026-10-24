"""INT-046 corporate SSO - token hardening and federation edge cases.

R01-AUDIT regression suite: the OIDC path used to ignore the JOSE header (so an
``alg: none`` / algorithm-confusion token was only stopped by accident) and
compared the HMAC with a short-circuiting ``!=``. These tests pin the hardened
behaviour: the header can only select among the tenant's expected HMAC
algorithms, ``typ`` must be ``JWT``, ``crit`` is refused, the signature is
compared in constant time, and the token must be addressed to the tenant's
client (OIDC Core §3.1.3.7).
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import importlib.util
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

import pytest

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

import sso_federation
from sso_federation import (
    DEFAULT_JWT_ALGORITHMS,
    HMAC_JWT_ALGORITHMS,
    CorporateSsoBroker,
    FederationConfigurationError,
    SsoFederationError,
    TenantResolutionError,
    TokenValidationError,
)

ROBI_ISS = "https://sso.robi.com.bd/oauth2/v1"
ROBI_CLIENT = "1000fix-corporate-b2b"
WALTON_ISS = "https://auth.waltonbd.com"
WALTON_CLIENT = "1000fix-walton-oem"


def robi_secret() -> str:
    """Tenant secrets are configuration: conftest puts test-only values in the env."""
    return os.environ["FIX_SSO_ROBI_SHARED_SECRET"]


def walton_secret() -> str:
    return os.environ["FIX_SSO_WALTON_SHARED_SECRET"]


def _b64(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _b64json(obj: Any) -> str:
    return _b64(json.dumps(obj).encode("utf-8"))


def _sign(secret: str, signing_input: str, digest: Any = hashlib.sha256) -> str:
    return _b64(hmac.new(secret.encode("utf-8"), signing_input.encode(), digest).digest())


def _claims(**overrides: Any) -> dict[str, Any]:
    claims: dict[str, Any] = {
        "iss": ROBI_ISS,
        "aud": ROBI_CLIENT,
        "sub": "robi_user_77",
        "email": "it.ops@robi.com.bd",
        "roles": ["AssetManager"],
        "exp": time.time() + 600,
    }
    claims.update(overrides)
    return claims


def _token(
    header: Any = None,
    claims: Any = None,
    secret: str | None = None,
    digest: Any = hashlib.sha256,
) -> str:
    h = _b64json({"alg": "HS256", "typ": "JWT"} if header is None else header)
    p = _b64json(_claims() if claims is None else claims)
    return f"{h}.{p}.{_sign(secret or robi_secret(), f'{h}.{p}', digest)}"


@pytest.fixture
def broker() -> CorporateSsoBroker:
    return CorporateSsoBroker()


def _reject(broker: CorporateSsoBroker, token: str, match: str, tenant: str = "TENANT-ROBI"):
    with pytest.raises(TokenValidationError, match=match):
        broker.authenticate_oidc(tenant, token)


# --------------------------------------------------------------------------- happy paths


def test_valid_token_mints_session_with_mapped_roles(broker):
    claims = _claims(
        iss=WALTON_ISS,
        aud=WALTON_CLIENT,
        sub="qa_walton_1",
        email="qa@waltonbd.com",
        roles=["Quality-Auditor", "OEM-Service-Lead", "Unknown-Group"],
    )
    session = broker.authenticate_oidc(
        "TENANT-WALTON", _token(claims=claims, secret=walton_secret())
    )

    assert session["status"] == "authenticated"
    assert session["auth_method"] == "oidc_federation"
    assert session["tenant_id"] == "TENANT-WALTON"
    assert session["tenant_name"] == "Walton Micro-Tech Corp"
    assert session["subject"] == "qa_walton_1"
    assert session["email"] == "qa@waltonbd.com"
    # Unknown IdP groups are dropped, known ones mapped in token order.
    assert session["roles"] == ["corporate_auditor", "corporate_admin"]
    assert session["issuer"] == "https://auth.1000fix.com/realms/fix-corporate"
    assert session["session_id"].startswith("sso-sess-")
    assert len(session["session_id"]) == len("sso-sess-") + 24
    assert session["expires_in"] == 8 * 3600
    assert session["portal_redirect"].endswith("/corporate/tenant-walton/dashboard")


def test_token_without_known_roles_defaults_to_employee(broker):
    session = broker.authenticate_oidc("TENANT-ROBI", _token(claims=_claims(roles=["Visitor"])))
    assert session["roles"] == ["corporate_employee"]

    no_roles = _claims()
    del no_roles["roles"], no_roles["sub"], no_roles["email"]
    session = broker.authenticate_oidc("TENANT-ROBI", _token(claims=no_roles))
    assert session["roles"] == ["corporate_employee"]
    assert session["subject"] == ""
    assert session["email"] == ""


def test_lowercase_typ_is_accepted(broker):
    # RFC 7515 §4.1.9: typ values are case-insensitive.
    token = _token(header={"alg": "HS256", "typ": "jwt"})
    assert broker.authenticate_oidc("TENANT-ROBI", token)["status"] == "authenticated"


def test_audience_may_be_a_list_containing_the_client(broker):
    token = _token(claims=_claims(aud=["some-other-rp", ROBI_CLIENT]))
    assert broker.authenticate_oidc("TENANT-ROBI", token)["status"] == "authenticated"


def test_tenant_can_opt_into_a_stronger_hmac_algorithm(broker):
    secret = "k" * 64  # RFC 7518 §3.2: HS512 needs a key of >= 64 bytes
    tenant = dict(broker.get_tenant("TENANT-ROBI"), jwt_algorithms=("HS512",))
    tenant["shared_secret"] = secret
    broker.register_tenant("TENANT-ROBI-HS512", tenant)

    hs512 = _token(header={"alg": "HS512", "typ": "JWT"}, secret=secret, digest=hashlib.sha512)
    session = broker.authenticate_oidc("TENANT-ROBI-HS512", hs512)
    assert session["tenant_id"] == "TENANT-ROBI-HS512"

    # ...and the opt-in REPLACES the default: HS256 is no longer accepted there.
    _reject(
        broker,
        _token(secret=secret),
        "Unsupported JWT algorithm 'HS256'",
        tenant="TENANT-ROBI-HS512",
    )


def test_default_policy_constants():
    assert DEFAULT_JWT_ALGORITHMS == ("HS256",)
    assert set(HMAC_JWT_ALGORITHMS) == {"HS256", "HS384", "HS512"}
    assert "none" not in HMAC_JWT_ALGORITHMS


# --------------------------------------------------------------------------- header attacks


@pytest.mark.parametrize("alg", ["none", "None", "NONE", ""])
def test_alg_none_is_rejected_with_and_without_signature(broker, alg):
    h = _b64json({"alg": alg, "typ": "JWT"})
    p = _b64json(_claims(roles=["AssetManager"]))
    _reject(broker, f"{h}.{p}.", "Unsupported JWT algorithm")
    # Even a correct HMAC over the input does not rescue an "alg: none" header.
    _reject(broker, f"{h}.{p}.{_sign(robi_secret(), f'{h}.{p}')}", "Unsupported JWT algorithm")


@pytest.mark.parametrize("alg", ["RS256", "ES256", "PS256", "EdDSA"])
def test_asymmetric_alg_confusion_is_rejected(broker, alg):
    # Classic confusion: the attacker signs with HMAC(shared secret) but claims an
    # asymmetric algorithm, hoping the verifier treats the secret as a public key.
    _reject(broker, _token(header={"alg": alg, "typ": "JWT"}), f"Unsupported JWT algorithm '{alg}'")


def test_unexpected_hmac_variant_is_rejected_even_when_correctly_signed(broker):
    token = _token(header={"alg": "HS512", "typ": "JWT"}, digest=hashlib.sha512)
    _reject(broker, token, r"expected one of \['HS256'\]")


def test_misconfigured_tenant_cannot_enable_non_hmac_algorithms(broker):
    tenant = dict(broker.get_tenant("TENANT-ROBI"), jwt_algorithms=("RS256", "none"))
    broker.register_tenant("TENANT-ROBI-BAD", tenant)
    _reject(broker, _token(header={"alg": "RS256", "typ": "JWT"}), "RS256", "TENANT-ROBI-BAD")
    _reject(broker, _token(header={"alg": "none", "typ": "JWT"}), "none", "TENANT-ROBI-BAD")


@pytest.mark.parametrize(
    "header",
    [
        {"typ": "JWT"},
        {"alg": None, "typ": "JWT"},
        {"alg": 256, "typ": "JWT"},
        {"alg": ["HS256"], "typ": "JWT"},
    ],
)
def test_missing_or_non_string_alg_is_rejected(broker, header):
    _reject(broker, _token(header=header), "Unsupported JWT algorithm")


@pytest.mark.parametrize(
    "header",
    [
        {"alg": "HS256"},
        {"alg": "HS256", "typ": "at+jwt"},
        {"alg": "HS256", "typ": "JWE"},
        {"alg": "HS256", "typ": 1},
    ],
)
def test_wrong_or_missing_typ_is_rejected(broker, header):
    _reject(broker, _token(header=header), "Unsupported JWT type")


def test_critical_header_extensions_are_refused(broker):
    _reject(
        broker,
        _token(header={"alg": "HS256", "typ": "JWT", "crit": ["exp"], "exp": 1}),
        "critical",
    )


def test_header_must_be_a_json_object(broker):
    _reject(broker, _token(header=["HS256", "JWT"]), "header: must be a JSON object")


def test_payload_must_be_a_json_object(broker):
    _reject(broker, _token(claims=["sub", "x"]), "payload: claims must be a JSON object")


# --------------------------------------------------------------------------- signature


def test_tampered_payload_fails_signature(broker):
    original = _token(claims=_claims(roles=["DeviceUser"]))
    h, _, sig = original.split(".")
    elevated = _b64json(_claims(roles=["AssetManager"]))
    _reject(broker, f"{h}.{elevated}.{sig}", "signature mismatch")


def test_tampered_header_fails_signature(broker):
    original = _token()
    _, p, sig = original.split(".")
    other_header = _b64json({"alg": "HS256", "typ": "JWT", "kid": "attacker"})
    _reject(broker, f"{other_header}.{p}.{sig}", "signature mismatch")


def test_flipped_signature_character_fails(broker):
    h, p, sig = _token().split(".")
    mid = len(sig) // 2
    flipped = sig[:mid] + ("A" if sig[mid] != "A" else "B") + sig[mid + 1 :]
    assert flipped != sig
    _reject(broker, f"{h}.{p}.{flipped}", "signature mismatch")


def test_truncated_and_empty_signatures_fail(broker):
    h, p, sig = _token().split(".")
    _reject(broker, f"{h}.{p}.{sig[:-4]}", "signature mismatch")
    _reject(broker, f"{h}.{p}.", "signature mismatch")


def test_non_ascii_signature_is_a_validation_error_not_a_crash(broker):
    h, p, _ = _token().split(".")
    _reject(broker, f"{h}.{p}.বাংলা", "signature mismatch")


def test_signature_from_another_tenant_secret_fails(broker):
    _reject(broker, _token(secret=walton_secret()), "signature mismatch")


def test_signature_is_compared_in_constant_time(broker, monkeypatch):
    calls: list[tuple[Any, Any]] = []
    real = hmac.compare_digest

    def spy(a, b):
        calls.append((a, b))
        return real(a, b)

    monkeypatch.setattr(sso_federation.hmac, "compare_digest", spy)
    token = _token()
    broker.authenticate_oidc("TENANT-ROBI", token)

    assert len(calls) == 1
    presented, expected = calls[0]
    assert isinstance(presented, bytes) and isinstance(expected, bytes)
    assert presented == token.split(".")[2].encode()
    assert presented == expected


# --------------------------------------------------------------------------- claims


def test_wrong_issuer_is_rejected(broker):
    _reject(broker, _token(claims=_claims(iss="https://evil.example")), "Issuer mismatch")


def test_missing_exp_is_treated_as_expired(broker):
    claims = _claims()
    del claims["exp"]
    _reject(broker, _token(claims=claims), "expired")


def test_audience_for_another_client_is_rejected(broker):
    _reject(broker, _token(claims=_claims(aud=WALTON_CLIENT)), "Audience mismatch")


def test_missing_audience_is_rejected(broker):
    claims = _claims()
    del claims["aud"]
    _reject(broker, _token(claims=claims), "Audience mismatch")


def test_tenant_without_client_id_never_authenticates(broker):
    tenant = dict(broker.get_tenant("TENANT-ROBI"))
    del tenant["client_id"]
    broker.register_tenant("TENANT-NOCLIENT", tenant)
    claims = _claims()
    del claims["aud"]  # aud None must not "match" a missing client_id
    _reject(broker, _token(claims=claims), "Audience mismatch", tenant="TENANT-NOCLIENT")


def test_non_numeric_exp_is_wrapped_as_parse_failure(broker):
    with pytest.raises(TokenValidationError, match="Failed to parse OIDC assertion") as exc:
        broker.authenticate_oidc("TENANT-ROBI", _token(claims=_claims(exp="tomorrow")))
    assert isinstance(exc.value.__cause__, TypeError)


# --------------------------------------------------------------------------- structure / tenancy


@pytest.mark.parametrize("token", ["", "a.b", "a.b.c.d", "header-only"])
def test_token_must_have_three_segments(broker, token):
    _reject(broker, token, "Invalid JWT structure")


def test_garbage_segments_are_wrapped_with_cause(broker):
    with pytest.raises(TokenValidationError, match="Failed to parse OIDC assertion") as exc:
        broker.authenticate_oidc("TENANT-ROBI", "!!!.???.sig")
    assert exc.value.__cause__ is not None
    assert isinstance(exc.value, SsoFederationError)


def test_oidc_against_a_saml_tenant_is_refused(broker):
    with pytest.raises(TokenValidationError, match="configured for SAML2, not OIDC"):
        broker.authenticate_oidc("TENANT-GP", _token())


def test_suspended_tenant_is_refused(broker):
    tenant = dict(broker.get_tenant("TENANT-ROBI"), status="suspended")
    broker.register_tenant("TENANT-ROBI", tenant)
    with pytest.raises(TenantResolutionError, match="suspended or decommissioned"):
        broker.authenticate_oidc("TENANT-ROBI", _token())


def test_register_tenant_onboards_a_new_client(broker):
    with pytest.raises(TenantResolutionError, match="not enrolled"):
        broker.get_tenant("TENANT-NEW")
    broker.register_tenant(
        "TENANT-NEW",
        {
            "name": "New Corp",
            "protocol": "OIDC",
            "idp_issuer": "https://idp.new.example",
            "client_id": "fix-new",
            "shared_secret": "new-corp-test-only-hmac-secret-32b+",
            "role_mapping": {"Boss": "corporate_admin"},
            "status": "active",
        },
    )
    token = _token(
        claims=_claims(iss="https://idp.new.example", aud="fix-new", roles=["Boss"]),
        secret="new-corp-test-only-hmac-secret-32b+",
    )
    assert broker.authenticate_oidc("TENANT-NEW", token)["roles"] == ["corporate_admin"]


# --------------------------------------------------------------------------- package surface


def test_src_package_re_exports_the_broker_api():
    spec = importlib.util.spec_from_file_location(
        "corporate_sso_src_pkg", SRC_DIR / "__init__.py", submodule_search_locations=[str(SRC_DIR)]
    )
    pkg = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = pkg
    try:
        spec.loader.exec_module(pkg)
        assert sorted(pkg.__all__) == [
            "CorporateSsoBroker",
            "SsoFederationError",
            "TenantResolutionError",
            "TokenValidationError",
        ]
        assert pkg.CorporateSsoBroker is pkg.sso_federation.CorporateSsoBroker
        assert issubclass(pkg.TokenValidationError, pkg.SsoFederationError)
        assert issubclass(pkg.TenantResolutionError, pkg.SsoFederationError)
        assert pkg.CorporateSsoBroker().get_tenant("TENANT-GP")["protocol"] == "SAML2"
    finally:
        sys.modules.pop("corporate_sso_src_pkg", None)
        sys.modules.pop("corporate_sso_src_pkg.sso_federation", None)


# --------------------------------------------------------------------------- secrets are configuration


def test_shipped_registry_contains_no_literal_trust_material():
    """R01-AUDIT: client secrets / IdP certificates were literals in the source."""
    broker = CorporateSsoBroker()
    for tenant_id in ("TENANT-ROBI", "TENANT-WALTON", "TENANT-GP"):
        tenant = broker.get_tenant(tenant_id)
        assert "shared_secret" not in tenant
        assert "idp_cert_pem" not in tenant
        assert "cert_fingerprint" not in tenant
    assert broker.get_tenant("TENANT-ROBI")["shared_secret_env"] == "FIX_SSO_ROBI_SHARED_SECRET"
    assert broker.get_tenant("TENANT-WALTON")["shared_secret_env"] == "FIX_SSO_WALTON_SHARED_SECRET"
    source = (SRC_DIR / "sso_federation.py").read_text(encoding="utf-8")
    assert "robi_enterprise_jwt_hmac_secret" not in source
    assert "walton_oem_sso_secret" not in source


def test_missing_client_secret_fails_closed(broker, monkeypatch):
    token = _token()  # signed with the (test) secret before it is withdrawn
    monkeypatch.delenv("FIX_SSO_ROBI_SHARED_SECRET")
    with pytest.raises(FederationConfigurationError, match="FIX_SSO_ROBI_SHARED_SECRET") as exc:
        broker.authenticate_oidc("TENANT-ROBI", token)
    assert isinstance(exc.value, SsoFederationError)


def test_empty_or_whitespace_secret_fails_closed(broker, monkeypatch):
    monkeypatch.setenv("FIX_SSO_ROBI_SHARED_SECRET", "   ")
    with pytest.raises(FederationConfigurationError, match="no usable client secret"):
        broker.authenticate_oidc("TENANT-ROBI", _token(secret="x"))


def test_secret_shorter_than_the_hash_output_is_refused(broker, monkeypatch):
    weak = "w" * 31  # HS256 needs >= 32 bytes
    monkeypatch.setenv("FIX_SSO_ROBI_SHARED_SECRET", weak)
    with pytest.raises(FederationConfigurationError, match="at least 32 bytes"):
        broker.authenticate_oidc("TENANT-ROBI", _token(secret=weak))


def test_hs512_requires_a_64_byte_secret(broker):
    tenant = dict(broker.get_tenant("TENANT-ROBI"), jwt_algorithms=("HS512",))
    tenant["shared_secret"] = "s" * 48
    broker.register_tenant("TENANT-ROBI-WEAK512", tenant)
    token = _token(header={"alg": "HS512", "typ": "JWT"}, secret="s" * 48, digest=hashlib.sha512)
    with pytest.raises(FederationConfigurationError, match="at least 64 bytes"):
        broker.authenticate_oidc("TENANT-ROBI-WEAK512", token)


def test_secret_from_env_is_trimmed_of_mount_newlines(broker, monkeypatch):
    secret = robi_secret()
    monkeypatch.setenv("FIX_SSO_ROBI_SHARED_SECRET", f"{secret}\n")
    assert broker.authenticate_oidc("TENANT-ROBI", _token(secret=secret))["status"] == (
        "authenticated"
    )


def test_inline_secret_from_a_secrets_manager_takes_precedence(broker, monkeypatch):
    vaulted = "vault-issued-test-only-secret-0123456789"
    tenant = dict(broker.get_tenant("TENANT-ROBI"), shared_secret=vaulted)
    broker.register_tenant("TENANT-ROBI", tenant)
    monkeypatch.delenv("FIX_SSO_ROBI_SHARED_SECRET")
    assert broker.authenticate_oidc("TENANT-ROBI", _token(secret=vaulted))["status"] == (
        "authenticated"
    )
    _reject(broker, _token(secret="x" * 40), "signature mismatch")


def test_tenant_without_any_secret_reference_fails_closed(broker):
    tenant = dict(broker.get_tenant("TENANT-ROBI"))
    del tenant["shared_secret_env"]
    broker.register_tenant("TENANT-NOSECRET", tenant)
    with pytest.raises(FederationConfigurationError, match="set shared_secret"):
        broker.authenticate_oidc("TENANT-NOSECRET", _token())
