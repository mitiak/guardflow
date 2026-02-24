# guardflow --- Milestone 5

## Docker Sandbox Isolation

### Goal

Execute code tools in isolated Docker sandbox.

### Codex Prompt

Implement Docker-based runner for python_exec tool with no network,
CPU/memory limits, and timeout. Ensure schema + allowlist + RBAC
enforced before sandbox. Add pytest marker `sandbox_isolation`. Update
README and CHANGELOG.

### Run

uv run guardflow run --input tests/fixtures/python_exec_safe.json

### Test

uv run pytest -q -m sandbox_isolation

### Definition of Done

Code executes in sandbox with restrictions applied.
