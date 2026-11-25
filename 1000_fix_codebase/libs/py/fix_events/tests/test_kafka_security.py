"""Connection-security settings for the Kafka transport (managed brokers are SASL_SSL-only)."""

from __future__ import annotations

import pytest

from libs.py.fix_events.kafka_bus import kafka_security_kwargs


def test_default_is_plaintext_for_the_local_cluster():
    assert kafka_security_kwargs({}) == {"security_protocol": "PLAINTEXT"}


def test_sasl_ssl_carries_mechanism_credentials_and_ca():
    kwargs = kafka_security_kwargs(
        {
            "KAFKA_SECURITY_PROTOCOL": "sasl_ssl",
            "KAFKA_SASL_MECHANISM": "scram-sha-256",
            "KAFKA_SASL_USERNAME": "fix-app",
            "KAFKA_SASL_PASSWORD": "s3cret",
            "KAFKA_SSL_CAFILE": "/etc/kafka/ca.pem",
        }
    )
    assert kwargs == {
        "security_protocol": "SASL_SSL",
        "sasl_mechanism": "SCRAM-SHA-256",
        "sasl_plain_username": "fix-app",
        "sasl_plain_password": "s3cret",
        "ssl_cafile": "/etc/kafka/ca.pem",
    }


@pytest.mark.parametrize(
    "env",
    [
        {"KAFKA_SECURITY_PROTOCOL": "SASL_SSL"},
        {"KAFKA_SECURITY_PROTOCOL": "SASL_SSL", "KAFKA_SASL_MECHANISM": "PLAIN"},
        {
            "KAFKA_SECURITY_PROTOCOL": "SASL_SSL",
            "KAFKA_SASL_MECHANISM": "GSSAPI",
            "KAFKA_SASL_USERNAME": "u",
            "KAFKA_SASL_PASSWORD": "p",
        },
        {"KAFKA_SECURITY_PROTOCOL": "TLS"},
    ],
)
def test_half_configured_or_unknown_security_is_refused(env):
    with pytest.raises(ValueError):
        kafka_security_kwargs(env)
