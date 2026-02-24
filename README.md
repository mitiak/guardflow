# guardflow

A secure AI tool-call execution pipeline with policy enforcement.

## Installation

```bash
# Install with uv (recommended)
uv sync --extra dev
```

## Usage

```bash
# Show available commands
uv run guardflow --help

# Run a tool-call through the pipeline
uv run guardflow run --input '{"tool":"echo","args":["hi"]}'

# Policy management (coming soon)
uv run guardflow policy

# Red-team guardrail regression (coming soon)
uv run guardflow redteam
```

## Running Tests

```bash
uv run pytest -q -m cli_contract
```

## Milestone 1 Features

- **CLI scaffold** — Typer-based CLI with `run`, `policy`, and `redteam` commands
- **Execution pipeline** — stub `validate → authorize → execute` pipeline
- **JSON I/O** — accepts JSON tool-call requests, returns JSON results
- **CLI contract tests** — pytest suite marked `cli_contract`
