from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType
from typing import Any


def _generate_schemas_module() -> ModuleType:
    path = Path("scripts/generate_schemas.py")
    spec = importlib.util.spec_from_file_location("generate_schemas", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _expected_schemas() -> dict[Path, dict[str, Any]]:
    return _generate_schemas_module().expected_schemas()


def _rendered(schema: dict[str, Any]) -> str:
    return _generate_schemas_module().rendered(schema)


def test_json_schema_snapshots_match_generated_output() -> None:
    expected = _expected_schemas()

    for path, schema in expected.items():
        assert path.read_text(encoding="utf-8") == _rendered(schema), path

    assert set(Path("schemas").glob("*.schema.json")) == set(expected)


def test_domain_schema_ids_follow_proof_scheme() -> None:
    for path, schema in _expected_schemas().items():
        schema_id = schema["$id"]
        if path.name == "error-envelope.schema.json":
            assert schema_id == "https://schemas.proof.dev/v0/error-envelope.schema.json"
        else:
            assert schema_id.startswith("proof://schema/")
            assert schema_id.endswith("/1.0")
