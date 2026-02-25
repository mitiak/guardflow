"""Red-team adversarial guardrail regression suite tests."""
import json
from pathlib import Path

import pytest
import typer.main
from click.testing import CliRunner

from guardflow.cli import app
from guardflow.redteam import REDTEAM_CASES

runner = CliRunner()
cli = typer.main.get_command(app)

MODEL_CONF = (
    "[request_definition]\nr = sub, act\n\n"
    "[policy_definition]\np = sub, act\n\n"
    "[policy_effect]\ne = some(where (p.eft == allow))\n\n"
    "[matchers]\nm = r.sub == p.sub && r.act == p.act\n"
)
POLICY_CSV = (
    "p, viewer, echo\n"
    "p, viewer, file_read\n"
    "p, operator, echo\n"
    "p, operator, file_read\n"
    "p, operator, http_request\n"
    "p, operator, shell_command\n"
    "p, admin, echo\n"
    "p, admin, file_read\n"
    "p, admin, http_request\n"
    "p, admin, shell_command\n"
    "p, admin, code_exec\n"
    "p, admin, python_exec\n"
)
ALLOWLIST_ALL = json.dumps(
    {"allowed_tools": ["echo", "file_read", "http_request", "shell_command", "code_exec", "python_exec"]}
)
FIXTURES = Path(__file__).parent / "fixtures" / "redteam"


def _write_policy_files(tmp_path):
    allowlist = tmp_path / "policy.json"
    model_file = tmp_path / "model.conf"
    policy_file = tmp_path / "rbac_policy.csv"
    allowlist.write_text(ALLOWLIST_ALL)
    model_file.write_text(MODEL_CONF)
    policy_file.write_text(POLICY_CSV)
    return allowlist, model_file, policy_file


def _run(tmp_path, fixture_name):
    allowlist, model_file, policy_file = _write_policy_files(tmp_path)
    return runner.invoke(
        cli,
        [
            "run",
            "--input",
            (FIXTURES / fixture_name).read_text(),
            "--policy",
            str(allowlist),
            "--rbac-model",
            str(model_file),
            "--rbac-policy",
            str(policy_file),
        ],
    )


@pytest.mark.redteam_suite
def test_prompt_injection_contained(tmp_path):
    result = _run(tmp_path, "prompt_injection_contained.json")
    assert result.exit_code == 0
    assert json.loads(result.output)["ok"] is True


@pytest.mark.redteam_suite
def test_unauthorized_tool_blocked(tmp_path):
    result = _run(tmp_path, "unauthorized_tool_blocked.json")
    assert result.exit_code != 0
    assert "UNAUTHORIZED_TOOL" in result.stderr


@pytest.mark.redteam_suite
def test_tool_name_injection_blocked(tmp_path):
    result = _run(tmp_path, "tool_name_injection_blocked.json")
    assert result.exit_code != 0
    assert "UNAUTHORIZED_TOOL" in result.stderr


@pytest.mark.redteam_suite
def test_data_exfiltration_blocked(tmp_path):
    result = _run(tmp_path, "data_exfiltration_blocked.json")
    assert result.exit_code != 0
    assert "RBAC_DENIED" in result.stderr


@pytest.mark.redteam_suite
def test_role_escalation_blocked(tmp_path):
    result = _run(tmp_path, "role_escalation_blocked.json")
    assert result.exit_code != 0
    assert "RBAC_DENIED" in result.stderr


@pytest.mark.redteam_suite
def test_schema_extra_field_blocked(tmp_path):
    result = _run(tmp_path, "schema_extra_field_blocked.json")
    assert result.exit_code != 0
    assert "SCHEMA_REJECTED" in result.stderr


@pytest.mark.redteam_suite
def test_redteam_run_all_pass(tmp_path):
    allowlist, model_file, policy_file = _write_policy_files(tmp_path)
    result = runner.invoke(
        cli,
        [
            "redteam",
            "run",
            "--policy",
            str(allowlist),
            "--rbac-model",
            str(model_file),
            "--rbac-policy",
            str(policy_file),
        ],
    )
    assert result.exit_code == 0
    assert "6/6 cases passed" in result.output


@pytest.mark.redteam_suite
def test_redteam_run_output_contains_case_names(tmp_path):
    allowlist, model_file, policy_file = _write_policy_files(tmp_path)
    result = runner.invoke(
        cli,
        [
            "redteam",
            "run",
            "--policy",
            str(allowlist),
            "--rbac-model",
            str(model_file),
            "--rbac-policy",
            str(policy_file),
        ],
    )
    assert result.exit_code == 0
    for case in REDTEAM_CASES:
        assert case.name in result.output
