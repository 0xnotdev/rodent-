"""Command line interface for the CP-00 Proof skeleton."""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from typing import Annotated, Any, NoReturn

import click
import typer
from rich.console import Console

from proof import __version__
from proof.config import ERROR_ENVELOPE_SCHEMA_ID, CliConfig, OutputFormat
from proof.domain import DOMAIN_SCHEMA_MODELS


@dataclass(frozen=True, slots=True)
class ErrorEnvelope:
    """Stable JSON CLI error envelope."""

    schema: str
    code: str
    message: str
    exit_code: int


console = Console(stderr=False)
app = typer.Typer(
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]},
    no_args_is_help=True,
)
schema_app = typer.Typer(add_completion=False, hidden=True, no_args_is_help=True)


def _version_callback(value: bool) -> None:
    if value:
        console.print(f"proof {__version__}")
        raise typer.Exit(0)


@app.callback()
def root(
    ctx: typer.Context,
    output_format: Annotated[
        OutputFormat,
        typer.Option(
            "--format",
            case_sensitive=False,
            help="Output format for CLI errors.",
        ),
    ] = OutputFormat.TEXT,
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            callback=_version_callback,
            is_eager=True,
            help="Show the Proof version and exit.",
        ),
    ] = False,
) -> None:
    """Proof infrastructure-agent assurance CLI."""
    _ = version
    ctx.obj = CliConfig(output_format=output_format)


def _wants_json(argv: list[str]) -> bool:
    for index, arg in enumerate(argv):
        if arg == "--format" and index + 1 < len(argv) and argv[index + 1].lower() == "json":
            return True
        if arg.startswith("--format=") and arg.split("=", 1)[1].lower() == "json":
            return True
    return False


def _schema_names() -> list[str]:
    return ["error-envelope", *sorted(DOMAIN_SCHEMA_MODELS)]


def _error_envelope_schema() -> dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": ERROR_ENVELOPE_SCHEMA_ID,
        "title": "Proof CLI error envelope",
        "type": "object",
        "additionalProperties": False,
        "required": ["schema", "code", "message", "exit_code"],
        "properties": {
            "schema": {"const": ERROR_ENVELOPE_SCHEMA_ID},
            "code": {"type": "string", "pattern": "^[a-z][a-z0-9_]*$"},
            "message": {"type": "string", "minLength": 1},
            "exit_code": {"type": "integer", "minimum": 1, "maximum": 255},
        },
    }


def _schema_payload(name: str) -> dict[str, Any]:
    if name == "error-envelope":
        return _error_envelope_schema()
    model = DOMAIN_SCHEMA_MODELS.get(name)
    if model is None:
        choices = ", ".join(_schema_names())
        raise click.BadParameter(f"unknown schema {name!r}; expected one of: {choices}")
    schema = model.model_json_schema(mode="serialization", ref_template="#/$defs/{model}")
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"proof://schema/{name}/1.0",
        **schema,
    }


@schema_app.command("list")
def list_schemas() -> None:
    """List committed JSON schema names as JSON."""
    print(json.dumps(_schema_names(), sort_keys=True, separators=(",", ":")))


@schema_app.command("show")
def show_schema(name: str) -> None:
    """Show one committed JSON schema as JSON."""
    print(json.dumps(_schema_payload(name), sort_keys=True, separators=(",", ":")))


app.add_typer(schema_app, name="schema", hidden=True)


def _error_code(exc: click.ClickException) -> str:
    if isinstance(exc, click.NoSuchOption):
        return "unknown_option"
    if isinstance(exc, click.NoSuchCommand):
        return "unknown_command"
    if isinstance(exc, click.BadParameter):
        return "bad_parameter"
    if isinstance(exc, click.UsageError):
        return "usage_error"
    return "cli_error"


def _emit_json_error(exc: click.ClickException) -> NoReturn:
    envelope = ErrorEnvelope(
        schema=ERROR_ENVELOPE_SCHEMA_ID,
        code=_error_code(exc),
        message=exc.format_message(),
        exit_code=exc.exit_code,
    )
    print(json.dumps(asdict(envelope), sort_keys=True, separators=(",", ":")), file=sys.stderr)
    raise SystemExit(exc.exit_code)


def main(argv: list[str] | None = None) -> None:
    """Run the Proof CLI."""
    args = list(sys.argv[1:] if argv is None else argv)
    try:
        app(args=args, prog_name="proof", standalone_mode=False)
    except click.ClickException as exc:
        if _wants_json(args):
            _emit_json_error(exc)
        exc.show(file=sys.stderr)
        raise SystemExit(exc.exit_code) from exc


if __name__ == "__main__":
    main()
