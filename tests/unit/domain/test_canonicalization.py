from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from proof.domain import InfrastructureIR, canonical_bytes, content_hash

ZERO_HASH = "sha256:" + "0" * 64
ONE_HASH = "sha256:" + "1" * 64
VECTOR_PATH = Path("tests/fixtures/domain/canonical_vectors.json")


def minimal_ir(
    *, provider_versions: dict[str, str] | None = None, content_hash_value: str = ZERO_HASH
) -> InfrastructureIR:
    return InfrastructureIR(
        ir_id="018f0d8e-3b26-7a4f-8d8e-111111111111",
        generated_at=datetime(2024, 1, 1, tzinfo=UTC),
        terraform_version="1.6.6",
        provider_versions=provider_versions or {"random": "3.6.0", "aws": "5.0.0"},
        source_hash=ZERO_HASH,
        resources=(),
        relationships=(),
        content_hash=content_hash_value,
    )


def test_equivalent_dictionary_order_hashes_identically() -> None:
    left = minimal_ir(provider_versions={"random": "3.6.0", "aws": "5.0.0"})
    right = minimal_ir(provider_versions={"aws": "5.0.0", "random": "3.6.0"})

    assert canonical_bytes(left) == canonical_bytes(right)
    assert content_hash(left) == content_hash(right)


def test_content_hash_field_is_excluded_from_hash_input() -> None:
    left = minimal_ir(content_hash_value=ZERO_HASH)
    right = minimal_ir(content_hash_value=ONE_HASH)

    assert canonical_bytes(left) == canonical_bytes(right)
    assert content_hash(left) == content_hash(right)


def test_one_value_change_hashes_differently() -> None:
    baseline = minimal_ir(provider_versions={"aws": "5.0.0", "random": "3.6.0"})
    changed = minimal_ir(provider_versions={"aws": "5.0.1", "random": "3.6.0"})

    assert canonical_bytes(baseline) != canonical_bytes(changed)
    assert content_hash(baseline) != content_hash(changed)


def test_golden_canonical_vector_matches() -> None:
    vector = json.loads(VECTOR_PATH.read_text(encoding="utf-8"))["vectors"][0]
    model = minimal_ir(content_hash_value=ONE_HASH)

    assert vector == {
        "name": "minimal-infrastructure-ir",
        "model": "InfrastructureIR",
        "canonical_json": canonical_bytes(model).decode("utf-8"),
        "content_hash": content_hash(model),
    }
