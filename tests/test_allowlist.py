"""Allowlist policy gate tests for guardflow."""

import json

import pytest
import typer.main
from click.testing import CliRunner

from guardflow.cli import app

runner = CliRunner()
cli = typer.main.get_command(app)

ECHO_PAYLOAD = {
    "actor": {"id": "u1", "role": "viewer"},
    "tool_call": {"tool": "echo", "args": {"text": "hi"}},
}

SHELL_PAYLOAD = {
    "actor": {"id": "u2", "role": "operator"},
    "tool_call": {"tool": "shell_command", "args": {"cmd": "ls"}},
}


@pytest.mark.allowlist_policy
def test_allowed_tool(tmp_path):
    """Allowed tool exits 0 and output has ok: true."""
    policy_file = tmp_path / "policy.json"
    policy_file.write_text(json.dumps({"allowed_tools": ["echo"]}))
    result = runner.invoke(cli, ["run", "--input", json.dumps(ECHO_PAYLOAD), "--policy", str(policy_file)])
    assert result.exit_code == 0
    parsed = json.loads(result.output)
    assert parsed["ok"] is True


@pytest.mark.allowlist_policy
def test_denied_tool(tmp_path):
    """Denied tool exits non-zero and stderr has UNAUTHORIZED_TOOL."""
    policy_file = tmp_path / "policy.json"
    policy_file.write_text(json.dumps({"allowed_tools": ["echo"]}))
    result = runner.invoke(cli, ["run", "--input", json.dumps(SHELL_PAYLOAD), "--policy", str(policy_file)])
    assert result.exit_code != 0
    assert "UNAUTHORIZED_TOOL" in result.stderr


@pytest.mark.allowlist_policy
def test_missing_policy_file(tmp_path):
    """--policy pointing to nonexistent file exits non-zero."""
    nonexistent = tmp_path / "nonexistent.json"
    result = runner.invoke(cli, ["run", "--input", json.dumps(ECHO_PAYLOAD), "--policy", str(nonexistent)])
    assert result.exit_code != 0


@pytest.mark.allowlist_policy
def test_policy_show(tmp_path):
    """policy show exits 0 and output contains allowed tools."""
    policy_file = tmp_path / "policy.json"
    policy_file.write_text(json.dumps({"allowed_tools": ["echo", "file_read"]}))
    result = runner.invoke(cli, ["policy", "show", "--policy", str(policy_file)])
    assert result.exit_code == 0
    assert "echo" in result.output


@pytest.mark.allowlist_policy
def test_policy_validate_valid(tmp_path):
    """Valid policy file exits 0."""
    policy_file = tmp_path / "policy.json"
    policy_file.write_text(json.dumps({"allowed_tools": ["echo"]}))
    result = runner.invoke(cli, ["policy", "validate", "--policy", str(policy_file)])
    assert result.exit_code == 0


@pytest.mark.allowlist_policy
def test_policy_validate_invalid(tmp_path):
    """Malformed JSON policy exits non-zero."""
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("this is not valid json {{{")
    result = runner.invoke(cli, ["policy", "validate", "--policy", str(bad_file)])
    assert result.exit_code != 0
