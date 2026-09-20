from __future__ import annotations

import json
import sys

import click
import pytest
from typer.testing import CliRunner

from proof import __version__
from proof.cli import _error_code, _wants_json, app, main
from proof.config import ERROR_ENVELOPE_SCHEMA_ID


def test_version() -> None:
    result = CliRunner().invoke(app, ["--version"], prog_name="proof")

    assert result.exit_code == 0
    assert result.stdout.strip() == f"proof {__version__}"
    assert result.stderr == ""


def test_help_has_no_traceback() -> None:
    result = CliRunner().invoke(app, ["--help"], prog_name="proof")

    assert result.exit_code == 0
    assert "Usage:" in result.stdout
    assert "Traceback" not in result.stdout
    assert "Traceback" not in result.stderr


def test_unknown_command_exits_two(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["missing-command"])

    captured = capsys.readouterr()
    assert exc_info.value.code == 2
    assert "No such command" in captured.err
    assert "Traceback" not in captured.err


def test_json_error_envelope_for_unknown_command(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["--format", "json", "missing-command"])

    captured = capsys.readouterr()
    assert exc_info.value.code == 2
    assert captured.out == ""
    envelope = json.loads(captured.err)
    assert envelope == {
        "schema": ERROR_ENVELOPE_SCHEMA_ID,
        "code": "unknown_command",
        "message": "No such command 'missing-command'.",
        "exit_code": 2,
    }


def test_json_error_envelope_for_equals_format(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["--format=json", "--unknown-option"])

    captured = capsys.readouterr()
    assert exc_info.value.code == 2
    assert json.loads(captured.err)["code"] == "unknown_option"


def test_main_uses_sys_argv(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "argv", ["proof", "--format", "json"])

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 2
    assert json.loads(capsys.readouterr().err)["code"] == "usage_error"


def test_internal_error_code_and_format_helpers() -> None:
    assert _wants_json(["--format", "JSON"])
    assert _wants_json(["--format=json"])
    assert not _wants_json(["--format", "text"])
    assert _error_code(click.BadParameter("bad")) == "bad_parameter"
    assert _error_code(click.ClickException("plain")) == "cli_error"
