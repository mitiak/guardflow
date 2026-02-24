# guardflow --- Milestone 2

## Strict Schema Enforcement

### Goal

Enforce strict JSON tool-call schema and reject malformed inputs.

### Codex Prompt

Add Pydantic v2 models for RunRequest, ToolCall, ToolResult, and
structured errors. Enforce strict validation (extra="forbid"). Reject
invalid input with code SCHEMA_REJECTED. Add pytest marker
`schema_validation`. Update README and CHANGELOG.

### Run

uv run guardflow run --input
'{"actor":{"id":"u1","role":"viewer"},"tool_call":{"tool":"echo","args":{"text":"hi"}}}'

### Test

uv run pytest -q -m schema_validation

### Definition of Done

Malformed tool calls rejected. Valid calls pass schema.
