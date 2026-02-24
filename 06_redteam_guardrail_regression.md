# guardflow --- Milestone 6

## Red Team Guardrail Regression

### Goal

Automated guardrail regression tests must pass.

### Codex Prompt

Create tests/redteam fixtures covering prompt injection, tool hijacking,
data exfiltration, schema manipulation, and unauthorized tool access.
Implement `guardflow redteam run`. Add pytest marker `redteam_suite`.
Update README and CHANGELOG.

### Run

uv run guardflow redteam run

### Test

uv run pytest -q -m redteam_suite

### Definition of Done

Known attack scenarios blocked. All red team tests pass.
