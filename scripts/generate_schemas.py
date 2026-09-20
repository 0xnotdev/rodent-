from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from proof.domain import DOMAIN_SCHEMA_MODELS

SCHEMA_DIR = Path("schemas")
ERROR_ENVELOPE_SCHEMA_PATH = SCHEMA_DIR / "error-envelope.schema.json"

ERROR_ENVELOPE_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://schemas.proof.dev/v0/error-envelope.schema.json",
    "title": "Proof CLI error envelope",
    "type": "object",
    "additionalProperties": False,
    "required": ["schema", "code", "message", "exit_code"],
    "properties": {
        "schema": {"const": "https://schemas.proof.dev/v0/error-envelope.schema.json"},
        "code": {"type": "string", "pattern": "^[a-z][a-z0-9_]*$"},
        "message": {"type": "string", "minLength": 1},
        "exit_code": {"type": "integer", "minimum": 1, "maximum": 255},
    },
}


def _domain_schema(name: str, model: type[Any]) -> dict[str, Any]:
    schema = model.model_json_schema(
        mode="serialization",
        ref_template="#/$defs/{model}",
    )
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"proof://schema/{name}/1.0",
        **schema,
    }


def expected_schemas() -> dict[Path, dict[str, Any]]:
    schemas: dict[Path, dict[str, Any]] = {ERROR_ENVELOPE_SCHEMA_PATH: ERROR_ENVELOPE_SCHEMA}
    for name, model in sorted(DOMAIN_SCHEMA_MODELS.items()):
        schemas[SCHEMA_DIR / f"{name}.schema.json"] = _domain_schema(name, model)
    return schemas


def rendered(schema: dict[str, Any]) -> str:
    return json.dumps(schema, indent=2, sort_keys=False) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate committed Proof JSON schemas.")
    parser.add_argument("--check", action="store_true", help="Fail if generated schemas drift.")
    args = parser.parse_args()

    expected = expected_schemas()
    if args.check:
        failures: list[str] = []
        for path, schema in expected.items():
            actual = path.read_text(encoding="utf-8") if path.exists() else None
            if actual != rendered(schema):
                failures.append(f"generated schema drift: {path}")
        expected_paths = set(expected)
        actual_paths = set(SCHEMA_DIR.glob("*.schema.json"))
        for path in sorted(actual_paths - expected_paths):
            failures.append(f"unexpected generated schema: {path}")
        if failures:
            raise SystemExit("\n".join(failures))
        return

    SCHEMA_DIR.mkdir(parents=True, exist_ok=True)
    for path, schema in expected.items():
        path.write_text(rendered(schema), encoding="utf-8")


if __name__ == "__main__":
    main()
