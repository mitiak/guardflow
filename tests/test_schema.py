"""Schema validation tests for guardflow."""

import json

import pytest
import typer.main
from click.testing import CliRunner

from guardflow.cli import app

runner = CliRunner()
cli = typer.main.get_command(app)

VALID_PAYLOAD = {
    "actor": {"id": "u1", "role": "viewer"},
    "tool_call": {"tool": "echo", "args": {"text": "hello"}},
}


@pytest.mark.schema_validation
def test_valid_request():
    """A fully valid payload exits 0 and output contains ok: true."""
    result = runner.invoke(cli, ["run", "--input", json.dumps(VALID_PAYLOAD)])
    assert result.exit_code == 0
    parsed = json.loads(result.output)
    assert parsed["ok"] is True


@pytest.mark.schema_validation
def test_missing_actor():
    """Missing actor field exits non-zero and stderr contains SCHEMA_REJECTED."""
    payload = {"tool_call": {"tool": "echo", "args": {}}}
    result = runner.invoke(cli, ["run", "--input", json.dumps(payload)])
    assert result.exit_code != 0
    assert "SCHEMA_REJECTED" in result.stderr


@pytest.mark.schema_validation
def test_extra_field_forbidden():
    """Extra top-level field exits non-zero and stderr contains SCHEMA_REJECTED."""
    payload = {**VALID_PAYLOAD, "unexpected": "field"}
    result = runner.invoke(cli, ["run", "--input", json.dumps(payload)])
    assert result.exit_code != 0
    assert "SCHEMA_REJECTED" in result.stderr


@pytest.mark.schema_validation
def test_wrong_type():
    """actor.id as int instead of str exits non-zero and stderr contains SCHEMA_REJECTED."""
    payload = {
        "actor": {"id": 42, "role": "viewer"},
        "tool_call": {"tool": "echo", "args": {}},
    }
    result = runner.invoke(cli, ["run", "--input", json.dumps(payload)])
    assert result.exit_code != 0
    assert "SCHEMA_REJECTED" in result.stderr
