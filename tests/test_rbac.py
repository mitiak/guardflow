"""RBAC authorization gate tests for guardflow."""

import json
from pathlib import Path

import pytest
import typer.main
from click.testing import CliRunner

from guardflow.cli import app

runner = CliRunner()
cli = typer.main.get_command(app)

VIEWER_ECHO_PAYLOAD = {
    "actor": {"id": "u1", "role": "viewer"},
    "tool_call": {"tool": "echo", "args": {"text": "hi"}},
}

VIEWER_HTTP_PAYLOAD = {
    "actor": {"id": "u1", "role": "viewer"},
    "tool_call": {"tool": "http_request", "args": {}},
}

OPERATOR_HTTP_PAYLOAD = {
    "actor": {"id": "u2", "role": "operator"},
    "tool_call": {"tool": "http_request", "args": {}},
}

MODEL_CONF = """\
[request_definition]
r = sub, act

[policy_definition]
p = sub, act

[policy_effect]
e = some(where (p.eft == allow))

[matchers]
m = r.sub == p.sub && r.act == p.act
"""

POLICY_CSV = """\
p, viewer, echo
p, viewer, file_read
p, operator, echo
p, operator, file_read
p, operator, http_request
p, operator, shell_command
p, admin, echo
p, admin, file_read
p, admin, http_request
p, admin, shell_command
p, admin, code_exec
"""

ALLOWLIST_ALL = json.dumps({"allowed_tools": ["echo", "file_read", "http_request", "shell_command", "code_exec"]})


def _write_rbac_files(tmp_path: Path) -> tuple[Path, Path]:
    model_file = tmp_path / "model.conf"
    policy_file = tmp_path / "rbac_policy.csv"
    model_file.write_text(MODEL_CONF)
    policy_file.write_text(POLICY_CSV)
    return model_file, policy_file


@pytest.mark.rbac_authorization
def test_viewer_allowed_tool(tmp_path):
    """viewer + echo is explicitly allowed — exit 0, ok: true."""
    model_file, policy_file = _write_rbac_files(tmp_path)
    allowlist = tmp_path / "policy.json"
    allowlist.write_text(ALLOWLIST_ALL)
    result = runner.invoke(
        cli,
        [
            "run",
            "--input", json.dumps(VIEWER_ECHO_PAYLOAD),
            "--policy", str(allowlist),
            "--rbac-model", str(model_file),
            "--rbac-policy", str(policy_file),
        ],
    )
    assert result.exit_code == 0
    parsed = json.loads(result.output)
    assert parsed["ok"] is True


@pytest.mark.rbac_authorization
def test_viewer_denied_tool(tmp_path):
    """viewer + http_request passes allowlist but is blocked by RBAC — exit non-zero, RBAC_DENIED in stderr."""
    model_file, policy_file = _write_rbac_files(tmp_path)
    allowlist = tmp_path / "policy.json"
    allowlist.write_text(ALLOWLIST_ALL)
    result = runner.invoke(
        cli,
        [
            "run",
            "--input", json.dumps(VIEWER_HTTP_PAYLOAD),
            "--policy", str(allowlist),
            "--rbac-model", str(model_file),
            "--rbac-policy", str(policy_file),
        ],
    )
    assert result.exit_code != 0
    assert "RBAC_DENIED" in result.stderr


@pytest.mark.rbac_authorization
def test_operator_allowed_tool(tmp_path):
    """operator + http_request is allowed by both gates — exit 0, ok: true."""
    model_file, policy_file = _write_rbac_files(tmp_path)
    allowlist = tmp_path / "policy.json"
    allowlist.write_text(ALLOWLIST_ALL)
    result = runner.invoke(
        cli,
        [
            "run",
            "--input", json.dumps(OPERATOR_HTTP_PAYLOAD),
            "--policy", str(allowlist),
            "--rbac-model", str(model_file),
            "--rbac-policy", str(policy_file),
        ],
    )
    assert result.exit_code == 0
    parsed = json.loads(result.output)
    assert parsed["ok"] is True


@pytest.mark.rbac_authorization
def test_policy_check_allowed(tmp_path):
    """policy check --role viewer --tool echo exits 0."""
    model_file, policy_file = _write_rbac_files(tmp_path)
    result = runner.invoke(
        cli,
        [
            "policy", "check",
            "--role", "viewer",
            "--tool", "echo",
            "--rbac-model", str(model_file),
            "--rbac-policy", str(policy_file),
        ],
    )
    assert result.exit_code == 0


@pytest.mark.rbac_authorization
def test_policy_check_denied(tmp_path):
    """policy check --role viewer --tool http_request exits non-zero."""
    model_file, policy_file = _write_rbac_files(tmp_path)
    result = runner.invoke(
        cli,
        [
            "policy", "check",
            "--role", "viewer",
            "--tool", "http_request",
            "--rbac-model", str(model_file),
            "--rbac-policy", str(policy_file),
        ],
    )
    assert result.exit_code != 0


@pytest.mark.rbac_authorization
def test_missing_rbac_file(tmp_path):
    """--rbac-model pointing to nonexistent file exits non-zero."""
    allowlist = tmp_path / "policy.json"
    allowlist.write_text(ALLOWLIST_ALL)
    result = runner.invoke(
        cli,
        [
            "run",
            "--input", json.dumps(VIEWER_ECHO_PAYLOAD),
            "--policy", str(allowlist),
            "--rbac-model", str(tmp_path / "nonexistent.conf"),
            "--rbac-policy", str(tmp_path / "nonexistent.csv"),
        ],
    )
    assert result.exit_code != 0
