# guardflow --- Milestone 4

## RBAC Authorization Layer

### Goal

Enforce role-based access control for tool execution.

### Codex Prompt

Integrate Casbin RBAC. Extend RunRequest with actor role. Deny
unauthorized role/tool combinations with code RBAC_DENIED. Add CLI
`guardflow policy check`. Add pytest marker `rbac_authorization`. Update
README and CHANGELOG.

### Run

uv run guardflow policy check --role viewer --tool echo

### Test

uv run pytest -q -m rbac_authorization

### Definition of Done

Role/tool matrix enforced correctly.
