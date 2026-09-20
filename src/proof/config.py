"""Configuration primitives for the CP-00 CLI skeleton."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

ERROR_ENVELOPE_SCHEMA_ID = "https://schemas.proof.dev/v0/error-envelope.schema.json"


class OutputFormat(StrEnum):
    """Supported command output formats."""

    TEXT = "text"
    JSON = "json"


@dataclass(frozen=True, slots=True)
class CliConfig:
    """Runtime settings established by global CLI options."""

    output_format: OutputFormat = OutputFormat.TEXT
