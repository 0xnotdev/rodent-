# Proof

Proof is the V0 infrastructure-agent assurance engine described by `spec.md`.
This checkpoint contains only CP-00 repository, packaging, and quality-gate
scaffolding: a reproducible Python package and the `proof` CLI skeleton.

Implemented CP-00 scope:

- Python package metadata for CPython `>=3.12,<3.15`.
- Typer-based `proof` entry point with `proof --version`.
- Stable JSON error envelope for `--format json` CLI errors.
- Ruff formatting/linting, strict mypy, pytest unit tests, schema drift checks,
  license allowlist checks, CycloneDX SBOM validation, and coverage XML validation.
- Apache-2.0 license, security policy, and pinned-SHA CI workflows.

Domain models, Docker, Terraform, AWS adapters, policy engines, sandboxing, and
all later-checkpoint subsystems are intentionally out of scope for CP-00.

## Local verification

```bash
uv sync --frozen
uv run ruff format --check .
uv run ruff check .
uv run mypy src
uv run pytest tests/unit -q
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
