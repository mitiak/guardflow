"""Docker sandbox isolation tests for guardflow."""

import json
from pathlib import Path

import pytest
import typer.main
from click.testing import CliRunner

from guardflow.cli import app
from guardflow.sandbox import run_python, SandboxError

runner = CliRunner()
cli = typer.main.get_command(app)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _is_docker_available() -> bool:
    try:
        import docker
        docker.from_env().ping()
        return True
    except Exception:
        return False


requires_docker = pytest.mark.skipif(
    not _is_docker_available(), reason="Docker daemon not available"
)

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
p, admin, python_exec
"""

ALLOWLIST_ALL = json.dumps({
    "allowed_tools": ["echo", "file_read", "http_request", "shell_command", "code_exec", "python_exec"]
})


def _write_policy_files(tmp_path: Path) -> tuple[Path, Path, Path]:
    allowlist = tmp_path / "policy.json"
    model_file = tmp_path / "model.conf"
    policy_file = tmp_path / "rbac_policy.csv"
    allowlist.write_text(ALLOWLIST_ALL)
    model_file.write_text(MODEL_CONF)
    policy_file.write_text(POLICY_CSV)
    return allowlist, model_file, policy_file


# ---------------------------------------------------------------------------
# Unit tests — sandbox.run_python() directly
# ---------------------------------------------------------------------------

@pytest.mark.sandbox_isolation
@requires_docker
def test_python_exec_stdout():
    """Safe code produces correct stdout."""
    result = run_python("print('hello from sandbox')")
    assert result["exit_code"] == 0
    assert "hello from sandbox" in result["stdout"]


@pytest.mark.sandbox_isolation
@requires_docker
def test_python_exec_no_network():
    """Network access fails inside the sandbox (network_mode=none)."""
    result = run_python(
        "import urllib.request; urllib.request.urlopen('http://example.com', timeout=3)"
    )
    assert result["exit_code"] != 0


@pytest.mark.sandbox_isolation
@requires_docker
def test_python_exec_timeout():
    """Long-running code is killed and raises SandboxError."""
    with pytest.raises(SandboxError, match="timed out"):
        run_python("import time; time.sleep(60)", timeout=3)


# ---------------------------------------------------------------------------
# Integration tests — full pipeline via CLI
# ---------------------------------------------------------------------------

@pytest.mark.sandbox_isolation
@requires_docker
def test_pipeline_python_exec_admin(tmp_path):
    """admin + python_exec runs in sandbox — exit 0, ok: true, stdout captured."""
    allowlist, model_file, policy_file = _write_policy_files(tmp_path)
    payload = {
        "actor": {"id": "u1", "role": "admin"},
        "tool_call": {"tool": "python_exec", "args": {"code": "print('hi')"}},
    }
    result = runner.invoke(
        cli,
        [
            "run",
            "--input", json.dumps(payload),
            "--policy", str(allowlist),
            "--rbac-model", str(model_file),
            "--rbac-policy", str(policy_file),
        ],
    )
    assert result.exit_code == 0
    parsed = json.loads(result.output)
    assert parsed["ok"] is True
    assert "hi" in parsed["data"]["sandbox"]["stdout"]


@pytest.mark.sandbox_isolation
def test_pipeline_python_exec_viewer_denied(tmp_path):
    """viewer + python_exec is blocked by RBAC — no Docker needed."""
    allowlist, model_file, policy_file = _write_policy_files(tmp_path)
    payload = {
        "actor": {"id": "u1", "role": "viewer"},
        "tool_call": {"tool": "python_exec", "args": {"code": "print('hi')"}},
    }
    result = runner.invoke(
        cli,
        [
            "run",
            "--input", json.dumps(payload),
            "--policy", str(allowlist),
            "--rbac-model", str(model_file),
            "--rbac-policy", str(policy_file),
        ],
    )
    assert result.exit_code != 0
    assert "RBAC_DENIED" in result.stderr
