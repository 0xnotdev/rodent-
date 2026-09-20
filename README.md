# Proof

Proof is the V0 infrastructure-agent assurance engine described by `spec.md`.
This checkpoint contains CP-00 repository scaffolding plus CP-01 domain schemas
and canonical serialization. Later persistence, sandbox, Terraform, AWS, and run
orchestration subsystems remain out of scope.

Implemented CP-00 scope:

- Python package metadata for CPython `>=3.12,<3.15`.
- Typer-based `proof` entry point with `proof --version`.
- Stable JSON error envelope for `--format json` CLI errors.
- Ruff formatting/linting, strict mypy, pytest unit tests, schema drift checks,
  license allowlist checks, CycloneDX SBOM validation, and coverage XML validation.
- Apache-2.0 license, security policy, and pinned-SHA CI workflows.

Implemented CP-01 scope:

- Strict, frozen Pydantic v2 domain models for `spec.md` §§8–9.
- RFC 8785 canonical JSON bytes and SHA-256 content hashing that excludes
  `content_hash` fields.
- UUIDv7 helper, UTC timestamp validation/serialization, JSON value validation,
  and sensitive `KnownValue` validation.
- Generated JSON Schema snapshots and a hidden JSON-only `proof schema` developer
  command.

Persistence, Docker, Terraform execution, AWS adapters, policy engines,
sandboxing, and all later-checkpoint subsystems are intentionally out of scope.

## Local verification

```bash
uv sync --frozen
uv run ruff format --check .
uv run ruff check .
uv run mypy src
uv run pytest tests/unit -q
uv run pytest tests/unit/domain tests/contract/test_json_schemas.py -q
uv build
```

Additional CP-00 evidence commands:

```bash
uv run python scripts/generate_schemas.py --check
uv run python scripts/check_action_pins.py
uv run python scripts/check_licenses.py
uv export --format cyclonedx1.5 --all-groups --frozen -o artifacts/proof.cdx.json
uv run python scripts/validate_sbom.py artifacts/proof.cdx.json
uv run coverage run -m pytest tests/unit -q
uv run coverage xml -o artifacts/coverage.xml
uv run python scripts/validate_coverage.py artifacts/coverage.xml
```
