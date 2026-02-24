"""CLI contract tests for guardflow."""

import json

import pytest
from typer.testing import CliRunner

from guardflow.cli import app

runner = CliRunner()


@pytest.mark.cli_contract
def test_help():
    """guardflow --help exits 0 and lists commands."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "run" in result.output
    assert "policy" in result.output
    assert "redteam" in result.output


@pytest.mark.cli_contract
def test_run_valid_input():
    """guardflow run --input '<json>' exits 0 and returns JSON."""
    payload = json.dumps(
        {"actor": {"id": "u1", "role": "viewer"}, "tool_call": {"tool": "echo", "args": {"text": "hi"}}}
    )
    result = runner.invoke(app, ["run", "--input", payload])
    assert result.exit_code == 0
    # Output should contain valid JSON with pipeline result
    parsed = json.loads(result.output)
    assert parsed["ok"] is True
    assert parsed["step"] == "execute"


@pytest.mark.cli_contract
def test_run_invalid_json():
    """guardflow run with invalid JSON exits non-zero."""
    result = runner.invoke(app, ["run", "--input", "{not valid json}"])
    assert result.exit_code != 0
