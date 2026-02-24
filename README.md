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

## Running Tests

```bash
# CLI contract tests
uv run pytest -q -m cli_contract

# Schema validation tests
uv run pytest -q -m schema_validation

# Allowlist policy tests
uv run pytest -q -m allowlist_policy

# All tests
uv run pytest -q
```

## Features

- **CLI scaffold** — Typer-based CLI with `run`, `policy`, and `redteam` commands
- **Execution pipeline** — `validate → authorize → execute` pipeline
- **Strict schema enforcement** — Pydantic v2 models reject invalid requests with `SCHEMA_REJECTED`
- **Tool allowlist policy** — JSON-configured allowlist rejects unauthorized tools with `UNAUTHORIZED_TOOL`
- **Policy management** — `policy show` and `policy validate` subcommands
- **JSON I/O** — accepts JSON tool-call requests, returns JSON results
- **CLI contract tests** — pytest suite marked `cli_contract`
- **Schema validation tests** — pytest suite marked `schema_validation`
- **Allowlist policy tests** — pytest suite marked `allowlist_policy`
