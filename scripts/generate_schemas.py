from __future__ import annotations

import argparse
import json
from pathlib import Path

SCHEMA_PATH = Path("schemas/error-envelope.schema.json")

SCHEMA = {
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


def rendered() -> str:
    return json.dumps(SCHEMA, indent=2, sort_keys=False) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate CP-00 JSON schemas.")
    parser.add_argument("--check", action="store_true", help="Fail if generated schemas drift.")
    args = parser.parse_args()

    expected = rendered()
    if args.check:
        actual = SCHEMA_PATH.read_text(encoding="utf-8")
        if actual != expected:
            raise SystemExit(f"generated schema drift: {SCHEMA_PATH}")
        return
    SCHEMA_PATH.parent.mkdir(parents=True, exist_ok=True)
    SCHEMA_PATH.write_text(expected, encoding="utf-8")


if __name__ == "__main__":
    main()
