from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from proof.domain import (
    Confidence,
    Evidence,
    KnownValue,
    ProvenanceKind,
    canonical_bytes,
    content_hash,
    is_uuid7,
    uuid7,
)

ZERO_HASH = "sha256:" + "0" * 64


def evidence_kwargs() -> dict[str, object]:
    return {
        "evidence_id": "018f0d8e-3b26-7a4f-8d8e-111111111111",
        "kind": ProvenanceKind.TERRAFORM_PLAN,
        "artifact_hash": ZERO_HASH,
        "observed_at": datetime(2024, 1, 1, tzinfo=UTC),
        "collector": "unit-test",
        "collector_version": "1.0.0",
        "confidence": Confidence.HIGH,
        "summary": "terraform plan fixture",
    }


def test_extra_fields_are_rejected() -> None:
    with pytest.raises(ValidationError, match="extra_forbidden"):
        Evidence(**evidence_kwargs(), unexpected=True)


def test_naive_timestamps_are_rejected() -> None:
    kwargs = evidence_kwargs()
    kwargs["observed_at"] = datetime(2024, 1, 1)

    with pytest.raises(ValidationError, match="timezone-aware UTC"):
        Evidence(**kwargs)


def test_timestamps_serialize_as_utc_rfc3339_microseconds_z() -> None:
    evidence = Evidence(**evidence_kwargs())

    assert evidence.model_dump(mode="json")["observed_at"] == "2024-01-01T00:00:00.000000Z"


def test_nan_json_values_are_rejected() -> None:
    with pytest.raises(ValidationError, match="NaN or Infinity"):
        KnownValue(known=True, value=float("nan"))


def test_plaintext_sensitive_values_are_rejected() -> None:
    with pytest.raises(ValidationError, match="sensitive values retain only a hash"):
        KnownValue(known=True, sensitive=True, value="secret", value_hash=ZERO_HASH)


def test_unknown_values_cannot_carry_plaintext() -> None:
    with pytest.raises(ValidationError, match="unknown values cannot carry plaintext"):
        KnownValue(known=False, value="plaintext")


def test_invalid_hashes_are_rejected() -> None:
    kwargs = evidence_kwargs()
    kwargs["artifact_hash"] = "sha256:" + "A" * 64

    with pytest.raises(ValidationError, match="pattern"):
        Evidence(**kwargs)


def test_authoritative_models_are_frozen() -> None:
    evidence = Evidence(**evidence_kwargs())

    with pytest.raises(ValidationError, match="frozen_instance"):
        evidence.summary = "mutated"  # type: ignore[misc]


def test_uuid7_helper_returns_lowercase_uuidv7() -> None:
    value = uuid7()

    assert is_uuid7(value)
    assert value == value.lower()
    assert value.split("-")[2].startswith("7")


def test_canonical_helpers_accept_json_values() -> None:
    payload = {"b": [2, 3], "a": {"nested": True}}

    assert canonical_bytes(payload) == b'{"a":{"nested":true},"b":[2,3]}'
    assert content_hash(payload).startswith("sha256:")
