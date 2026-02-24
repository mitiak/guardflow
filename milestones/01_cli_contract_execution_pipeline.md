# guardflow --- Milestone 1

## CLI Contract & Execution Pipeline

### Goal

Ship a stable `guardflow` CLI and deterministic pipeline stub (validate
→ authorize → execute).

### Codex Prompt

Create a Python project named `guardflow` with `src/` layout using `uv`.
Add a Typer CLI entrypoint `guardflow` with commands: `run`, `policy`,
`redteam`. Implement `guardflow run --input <json>` that loads JSON and
runs a placeholder pipeline (validate → authorize → execute) returning
JSON output. Add README.md with full install/run instructions and a
feature section for this milestone. Add CHANGELOG.md. Add pytest with
marker `cli_contract`.

### Run

uv run guardflow --help

### Test

uv run pytest -q -m cli_contract

### Definition of Done

CLI works. Pipeline stub exists. Smoke test passes.
