from __future__ import annotations

import json

from typer.testing import CliRunner

from proof.cli import app
from proof.domain import DOMAIN_SCHEMA_MODELS


def test_hidden_schema_list_outputs_json_names() -> None:
    result = CliRunner().invoke(app, ["schema", "list"], prog_name="proof")

    assert result.exit_code == 0
    assert result.stderr == ""
    names = json.loads(result.stdout)
    assert names == ["error-envelope", *sorted(DOMAIN_SCHEMA_MODELS)]


def test_hidden_schema_show_outputs_json_schema() -> None:
    result = CliRunner().invoke(app, ["schema", "show", "evidence"], prog_name="proof")

    assert result.exit_code == 0
    schema = json.loads(result.stdout)
    assert schema["$id"] == "proof://schema/evidence/1.0"
    assert schema["additionalProperties"] is False
    assert schema["properties"]["artifact_hash"] == {"$ref": "#/$defs/Sha256"}
    assert schema["$defs"]["Sha256"]["pattern"] == "^sha256:[0-9a-f]{64}$"
