# guardflow

A secure AI tool-call execution pipeline with policy enforcement.

## Installation

```bash
# Install with uv (recommended)
uv sync --extra dev
```

## Input Schema

All requests must conform to the following JSON structure:

```json
{
  "actor": {
    "id": "string",
    "role": "string"
  },
  "tool_call": {
    "tool": "string",
    "args": {}
  }
}
```

Extra fields at any level are rejected. Invalid requests return a `SCHEMA_REJECTED` error on stderr with exit code 1.

## Usage

```bash
# Show available commands
uv run guardflow --help

# Run a tool-call through the pipeline
uv run guardflow run --input '{"actor":{"id":"u1","role":"viewer"},"tool_call":{"tool":"echo","args":{"text":"hi"}}}'

# Run from a file
uv run guardflow run -i examples/echo.json

# Show the tool allowlist
uv run guardflow policy show

# Validate the policy config file
uv run guardflow policy validate

# Use a custom policy file
uv run guardflow run -i examples/echo.json --policy /path/to/policy.json

# Red-team guardrail regression (coming soon)
uv run guardflow redteam
```

## Policy

The allowlist policy is configured in `policy.json` at the project root:

```json
{
  "allowed_tools": ["echo", "http_request", "file_read"]
}
```

Requests for tools not in the allowlist are rejected with an `UNAUTHORIZED_TOOL` error on stderr and exit code 1.

## Docker Sandbox

The `python_exec` tool runs code in an isolated Docker container with the following constraints:

| Constraint | Value |
|---|---|
| Network | none |
| Memory | 128 MiB |
| CPU | 0.5 vCPU |
| Timeout | 10 seconds |

```bash
# Execute Python code in the sandbox (requires admin role)
uv run guardflow run --input tests/fixtures/python_exec_safe.json

# Inline
uv run guardflow run --input '{"actor":{"id":"u1","role":"admin"},"tool_call":{"tool":"python_exec","args":{"code":"print(2+2)"}}}'
```

Output includes a `sandbox` key with `stdout`, `stderr`, and `exit_code`.

## RBAC

Role/tool permissions are enforced by a Casbin ACL policy (`rbac_policy.csv`):

| Role | Permitted tools |
|---|---|
| viewer | echo, file_read |
| operator | echo, file_read, http_request, shell_command |
| admin | all tools including python_exec |

```bash
# Check whether a role may use a tool
uv run guardflow policy check --role viewer --tool echo
uv run guardflow policy check --role viewer --tool python_exec
```

## Running Tests

```bash
# CLI contract tests
uv run pytest -q -m cli_contract

# Schema validation tests
uv run pytest -q -m schema_validation

# Allowlist policy tests
uv run pytest -q -m allowlist_policy

# RBAC authorization tests
uv run pytest -q -m rbac_authorization

# Docker sandbox tests (requires Docker daemon)
uv run pytest -q -m sandbox_isolation

# All tests
uv run pytest -q
```

## Features

- **CLI scaffold** — Typer-based CLI with `run`, `policy`, and `redteam` commands
- **Execution pipeline** — `validate → authorize → execute` pipeline
- **Strict schema enforcement** — Pydantic v2 models reject invalid requests with `SCHEMA_REJECTED`
- **Tool allowlist policy** — JSON-configured allowlist rejects unauthorized tools with `UNAUTHORIZED_TOOL`
- **RBAC authorization** — Casbin ACL enforces role/tool matrix; unauthorized combos return `RBAC_DENIED`
- **Docker sandbox** — `python_exec` runs in isolated container with no network, CPU/memory limits, and timeout
- **Policy management** — `policy show`, `policy validate`, and `policy check` subcommands
- **JSON I/O** — accepts JSON tool-call requests, returns JSON results
