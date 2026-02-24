# guardflow --- Milestone 3

## Tool Allowlist Policy Gate

### Goal

Add allowlist policy validation before execution.

### Codex Prompt

Implement policy layer loading tool allowlist from config. Add
`guardflow policy show` and `guardflow policy validate`. Deny
unauthorized tools with code UNAUTHORIZED_TOOL. Add pytest marker
`allowlist_policy`. Update README and CHANGELOG.

### Run

uv run guardflow policy show

### Test

uv run pytest -q -m allowlist_policy

### Definition of Done

Unauthorized tools blocked at policy gate.
