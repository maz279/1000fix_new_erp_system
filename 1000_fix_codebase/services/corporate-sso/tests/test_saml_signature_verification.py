"""INT-046 SAML 2.0 - XML-DSig verification against the pinned IdP certificate.

R01-AUDIT regression suite: ``authenticate_saml`` used to accept ANY XML that
contained the issuer string - no signature check at all, the configured
certificate fingerprint was never used. Assertions are now verified with signxml
against the tenant's configured IdP certificate (pinned by SHA-256), and only the
element the signature actually covers is consumed (XML signature wrapping).
The IdPs are throw-away test keys from conftest - no network, no real IdP.
"""

from __future__ import annotations

import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from lxml import etree
from signxml import XMLSigner, methods

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import sso_federation
from sso_federation import (
    SAML_CLOCK_SKEW_SECONDS,
    CorporateSsoBroker,
    FederationConfigurationError,
    TenantResolutionError,
    TokenValidationError,
)

SAML_NS = "urn:oasis:names:tc:SAML:2.0:assertion"
SP_ENTITY_ID = "https://auth.1000fix.com/realms/fix-corporate"
ACS_URL = "https://auth.1000fix.com/realms/fix-corporate/broker/tenant-gp/endpoint"
ADMIN = {"email": "ceo@grameenphone.com", "role": "GP-Fleet-Admin"}


def sso_iso(offset: float) -> str:
    """xs:dateTime (UTC 'Z') at now + offset seconds."""
    return (datetime.now(UTC) + timedelta(seconds=offset)).strftime("%Y-%m-%dT%H:%M:%SZ")


@pytest.fixture
def broker() -> CorporateSsoBroker:
    return CorporateSsoBroker()


def _gp_variant(broker: CorporateSsoBroker, tenant_id: str, **overrides) -> str:
    broker.register_tenant(tenant_id, dict(broker.get_tenant("TENANT-GP"), **overrides))
    return tenant_id


def _reject(broker, xml, match, tenant="TENANT-GP", **kwargs):
    with pytest.raises(TokenValidationError, match=match):
        broker.authenticate_saml(tenant, xml, **kwargs)


# --------------------------------------------------------------------------- valid


def test_valid_signed_assertion_authenticates(broker, idp):
    session = broker.authenticate_saml(
        "TENANT-GP", idp.signed_response(attributes={"email": "a@gp.com", "role": "GP-Fleet-Admin"})
    )
    assert session["status"] == "authenticated"
    assert session["auth_method"] == "saml2_federation"
    assert session["subject"] == "gp_staff_1"
    assert session["email"] == "a@gp.com"
    assert session["roles"] == ["corporate_admin"]


def test_string_with_xml_declaration_is_accepted(broker, idp):
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n' + idp.signed_response().decode("utf-8")
    assert broker.authenticate_saml("TENANT-GP", xml)["subject"] == "gp_staff_1"


def test_sp_initiated_flow_checks_recipient_and_in_response_to(broker, idp):
    tenant = _gp_variant(broker, "TENANT-GP-ACS", acs_url=ACS_URL)
    confirmation = {"NotOnOrAfter": sso_iso(120), "Recipient": ACS_URL, "InResponseTo": "_req-42"}
    response = idp.signed_response(confirmation=confirmation)
    session = broker.authenticate_saml(tenant, response, request_id="_req-42")
    assert session["tenant_id"] == "TENANT-GP-ACS"


def test_idp_initiated_assertion_with_in_response_to_is_fine_without_request_id(broker, idp):
    response = idp.signed_response(confirmation={"InResponseTo": "_req-1"})
    assert broker.authenticate_saml("TENANT-GP", response)["status"] == "authenticated"


# --------------------------------------------------------------------------- signature


def test_unsigned_assertion_is_rejected(broker, idp):
    """The defect: the old broker accepted this (issuer string present, no signature)."""
    _reject(broker, idp.response(idp.assertion(attributes=ADMIN)), "signature verification failed")


def test_tampered_subject_breaks_the_digest(broker, idp):
    tampered = idp.signed_response().replace(b"gp_staff_1", b"gp_chief_x")
    _reject(broker, tampered, "Digest mismatch")


def test_tampered_role_breaks_the_digest(broker, idp):
    tampered = idp.signed_response().replace(b"GP-Staff", b"GP-Fleet-Admin")
    _reject(broker, tampered, "signature verification failed")


def test_assertion_signed_by_another_key_is_rejected(broker, attacker_idp):
    _reject(broker, attacker_idp.signed_response(attributes=ADMIN), "signature verification failed")


def test_attacker_cannot_borrow_the_trusted_certificate_in_key_info(broker, idp, attacker_idp):
    """KeyInfo is attacker-controlled: verification uses ONLY the configured certificate."""
    signer = XMLSigner(
        method=methods.enveloped,
        signature_algorithm="rsa-sha256",
        digest_algorithm="sha256",
        c14n_algorithm="http://www.w3.org/2001/10/xml-exc-c14n#",
    )
    forged = signer.sign(
        idp.assertion(attributes=ADMIN), key=attacker_idp.key_pem, cert=idp.cert_pem
    )
    _reject(broker, idp.response(forged), "signature verification failed")


def test_hmac_signed_assertion_is_refused(broker, idp):
    """Algorithm confusion on SAML: an HMAC "signature" with a guessable key."""
    signer = XMLSigner(
        method=methods.enveloped,
        signature_algorithm="hmac-sha256",
        digest_algorithm="sha256",
        c14n_algorithm="http://www.w3.org/2001/10/xml-exc-c14n#",
    )
    forged = signer.sign(idp.assertion(attributes=ADMIN), key=b"guessable")
    _reject(broker, idp.response(forged), "forbidden by configuration")


def test_signature_over_the_response_instead_of_the_assertion_is_refused(broker, idp):
    response = etree.fromstring(idp.response(idp.assertion()))  # noqa: S320 - test-built XML
    signed_response = etree.tostring(idp.sign(response))
    _reject(broker, signed_response, "does not cover a SAML 2.0 Assertion")


# --------------------------------------------------------------------------- XML signature wrapping


def test_xsw_unsigned_sibling_assertion_is_never_consumed(broker, idp):
    evil = idp.assertion(assertion_id="_evil", name_id="ceo", attributes=ADMIN)
    signed = idp.sign(idp.assertion())
    session = broker.authenticate_saml("TENANT-GP", idp.response(evil, signed))
    assert session["subject"] == "gp_staff_1"
    assert session["roles"] == ["corporate_employee"]


def test_xsw_signed_assertion_wrapped_inside_a_forged_one(broker, idp):
    evil = idp.assertion(assertion_id="_evil", name_id="ceo", attributes=ADMIN)
    advice = etree.SubElement(evil, f"{{{SAML_NS}}}Advice")
    advice.append(idp.sign(idp.assertion()))
    session = broker.authenticate_saml("TENANT-GP", idp.response(evil))
    assert session["subject"] == "gp_staff_1"
    assert session["email"] == "staff1@grameenphone.com"


def test_xsw_duplicate_id_is_ambiguous_and_rejected(broker, idp):
    evil = idp.assertion(assertion_id="_assert-1", name_id="ceo", attributes=ADMIN)
    signed = idp.sign(idp.assertion(assertion_id="_assert-1"))
    _reject(broker, idp.response(evil, signed), "Ambiguous reference")


# --------------------------------------------------------------------------- trust configuration


def test_tenant_without_certificate_fails_closed(broker, idp, monkeypatch):
    monkeypatch.delenv("FIX_SSO_GP_IDP_CERT_PEM")
    with pytest.raises(FederationConfigurationError, match="fail closed"):
        broker.authenticate_saml("TENANT-GP", idp.signed_response())


def test_tenant_without_fingerprint_pin_fails_closed(broker, idp, monkeypatch):
    monkeypatch.delenv("FIX_SSO_GP_IDP_CERT_SHA256")
    with pytest.raises(FederationConfigurationError, match="no IdP signing certificate"):
        broker.authenticate_saml("TENANT-GP", idp.signed_response())


def test_certificate_not_matching_the_pin_fails_closed(broker, idp, attacker_idp, monkeypatch):
    monkeypatch.setenv("FIX_SSO_GP_IDP_CERT_SHA256", attacker_idp.sha256)
    with pytest.raises(FederationConfigurationError, match="pinned SHA-256 fingerprint"):
        broker.authenticate_saml("TENANT-GP", idp.signed_response())


def test_swapped_certificate_is_caught_by_the_pin(broker, attacker_idp, monkeypatch):
    """Someone replaces the configured PEM (but not the pin) with an attacker cert."""
    monkeypatch.setenv("FIX_SSO_GP_IDP_CERT_PEM", attacker_idp.cert_pem)
    with pytest.raises(FederationConfigurationError, match="does not match"):
        broker.authenticate_saml("TENANT-GP", attacker_idp.signed_response())


def test_pin_may_be_written_colon_separated_lowercase(broker, idp, monkeypatch):
    pin = ":".join(idp.sha256[i : i + 2] for i in range(0, 64, 2)).lower()
    monkeypatch.setenv("FIX_SSO_GP_IDP_CERT_SHA256", pin)
    assert broker.authenticate_saml("TENANT-GP", idp.signed_response())["status"] == "authenticated"


def test_invalid_pem_fails_closed(broker, idp, monkeypatch):
    monkeypatch.setenv("FIX_SSO_GP_IDP_CERT_PEM", "-----BEGIN CERTIFICATE-----\nnope\n")
    with pytest.raises(FederationConfigurationError, match=r"not a PEM X.509"):
        broker.authenticate_saml("TENANT-GP", idp.signed_response())


def test_inline_certificate_config_is_supported(broker, idp, monkeypatch):
    monkeypatch.delenv("FIX_SSO_GP_IDP_CERT_PEM")
    monkeypatch.delenv("FIX_SSO_GP_IDP_CERT_SHA256")
    tenant = _gp_variant(
        broker, "TENANT-GP-INLINE", idp_cert_pem=idp.cert_pem, cert_fingerprint=idp.sha256
    )
    assert broker.authenticate_saml(tenant, idp.signed_response())["tenant_id"] == tenant


# --------------------------------------------------------------------------- validity window


def test_expired_assertion_is_rejected(broker, idp):
    response = idp.signed_response(not_on_or_after=-(SAML_CLOCK_SKEW_SECONDS + 60))
    _reject(broker, response, "expired")


def test_small_clock_skew_is_tolerated(broker, idp):
    late = idp.signed_response(not_on_or_after=-(SAML_CLOCK_SKEW_SECONDS // 2))
    early = idp.signed_response(not_before=SAML_CLOCK_SKEW_SECONDS // 2)
    assert broker.authenticate_saml("TENANT-GP", late)["status"] == "authenticated"
    assert broker.authenticate_saml("TENANT-GP", early)["status"] == "authenticated"


def test_not_yet_valid_assertion_is_rejected(broker, idp):
    _reject(broker, idp.signed_response(not_before=600), "not yet valid")


def test_assertion_without_any_expiry_is_rejected(broker, idp):
    _reject(broker, idp.signed_response(not_before=None, not_on_or_after=None), "no NotOnOrAfter")


def test_expired_subject_confirmation_is_rejected(broker, idp):
    response = idp.signed_response(confirmation={"NotOnOrAfter": sso_iso(-600)})
    _reject(broker, response, "expired")


def test_invalid_timestamp_is_rejected(broker, idp):
    _reject(broker, idp.signed_response(confirmation={"NotOnOrAfter": "tomorrow"}), "timestamp")


def test_naive_timestamp_is_read_as_utc(broker, idp):
    naive_future = sso_iso(120).rstrip("Z")
    naive_past = sso_iso(-600).rstrip("Z")
    ok = idp.signed_response(confirmation={"NotOnOrAfter": naive_future})
    assert broker.authenticate_saml("TENANT-GP", ok)["status"] == "authenticated"
    _reject(broker, idp.signed_response(confirmation={"NotOnOrAfter": naive_past}), "expired")


# --------------------------------------------------------------------------- audience / recipient / request


def test_wrong_audience_is_rejected(broker, idp):
    _reject(broker, idp.signed_response(audience="https://other-sp.example"), "Audience mismatch")


def test_missing_audience_restriction_is_rejected(broker, idp):
    _reject(broker, idp.signed_response(audience=None), "Audience mismatch")


def test_assertion_without_conditions_has_no_audience(broker, idp):
    response = idp.signed_response(
        with_conditions=False, confirmation={"NotOnOrAfter": sso_iso(120)}
    )
    _reject(broker, response, "Audience mismatch")


def test_audience_follows_the_configured_sp_entity_id(idp):
    custom = CorporateSsoBroker(sp_entity_id="https://sp.1000fix.example/saml")
    _reject(custom, idp.signed_response(), "not addressed to https://sp.1000fix.example/saml")
    ok = idp.signed_response(audience="https://sp.1000fix.example/saml")
    assert custom.authenticate_saml("TENANT-GP", ok)["status"] == "authenticated"


def test_tenant_level_sp_entity_id_overrides_the_broker(broker, idp):
    tenant = _gp_variant(broker, "TENANT-GP-SP", sp_entity_id="https://sp.tenant.example")
    ok = idp.signed_response(audience="https://sp.tenant.example")
    assert broker.authenticate_saml(tenant, ok)["status"] == "authenticated"


def test_wrong_recipient_is_rejected(broker, idp):
    tenant = _gp_variant(broker, "TENANT-GP-ACS", acs_url=ACS_URL)
    response = idp.signed_response(
        confirmation={"NotOnOrAfter": sso_iso(120), "Recipient": "https://evil.example/acs"}
    )
    _reject(broker, response, "Recipient mismatch", tenant=tenant)


def test_missing_recipient_is_rejected_when_an_acs_is_configured(broker, idp):
    tenant = _gp_variant(broker, "TENANT-GP-ACS", acs_url=ACS_URL)
    _reject(broker, idp.signed_response(), "Recipient mismatch", tenant=tenant)


def test_wrong_in_response_to_is_rejected(broker, idp):
    response = idp.signed_response(confirmation={"InResponseTo": "_req-attacker"})
    _reject(broker, response, "InResponseTo", request_id="_req-42")


def test_missing_in_response_to_is_rejected_for_sp_initiated_logins(broker, idp):
    _reject(broker, idp.signed_response(), "InResponseTo", request_id="_req-42")


# --------------------------------------------------------------------------- content of the signed assertion


def test_foreign_issuer_inside_a_valid_signature_is_rejected(broker, idp):
    _reject(broker, idp.signed_response(issuer="https://idp.evil.example"), "SAML Issuer mismatch")


@pytest.mark.parametrize("name_id", [None, "   "])
def test_assertion_without_subject_is_rejected(broker, idp, name_id):
    _reject(broker, idp.signed_response(name_id=name_id), "no Subject NameID")


def test_missing_email_falls_back_to_the_tenant_address(broker, idp):
    session = broker.authenticate_saml(
        "TENANT-GP", idp.signed_response(name_id="gp_buyer", attributes={"role": "GP-Procurement"})
    )
    assert session["email"] == "gp_buyer@tenant-gp.com"
    assert session["roles"] == ["corporate_buyer"]


def test_empty_attribute_values_count_as_absent(broker, idp):
    session = broker.authenticate_saml(
        "TENANT-GP", idp.signed_response(name_id="gp_e", attributes={"email": " ", "role": ""})
    )
    assert session["email"] == "gp_e@tenant-gp.com"
    assert session["roles"] == ["corporate_employee"]


def test_unknown_or_missing_group_maps_to_employee(broker, idp):
    unknown = idp.signed_response(attributes={"role": "GP-Contractor", "email": "c@gp.com"})
    missing = idp.signed_response(attributes={})
    assert broker.authenticate_saml("TENANT-GP", unknown)["roles"] == ["corporate_employee"]
    assert broker.authenticate_saml("TENANT-GP", missing)["roles"] == ["corporate_employee"]


# --------------------------------------------------------------------------- parsing / tenancy


def test_doctype_is_refused(broker, idp):
    body = idp.signed_response()
    with_doctype = b'<!DOCTYPE r [<!ENTITY x "gp_ceo">]>' + body
    _reject(broker, with_doctype, "DOCTYPE")


def test_malformed_xml_is_a_validation_error(broker):
    _reject(broker, "<saml:Assertion", "signature verification failed")


def test_saml_against_an_oidc_tenant_is_refused(broker, idp):
    _reject(broker, idp.signed_response(), "configured for OIDC, not SAML2", tenant="TENANT-ROBI")


def test_suspended_saml_tenant_is_refused(broker, idp):
    tenant = _gp_variant(broker, "TENANT-GP-OFF", status="suspended")
    with pytest.raises(TenantResolutionError):
        broker.authenticate_saml(tenant, idp.signed_response())


def test_only_strong_asymmetric_xmldsig_algorithms_are_accepted():
    names = {m.name for m in sso_federation.SAML_SIGNATURE_METHODS}
    assert names == {
        "RSA_SHA256",
        "RSA_SHA384",
        "RSA_SHA512",
        "ECDSA_SHA256",
        "ECDSA_SHA384",
        "ECDSA_SHA512",
    }
