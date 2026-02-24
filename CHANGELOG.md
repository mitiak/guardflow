# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-02-24

### Added
- `policy.json` — default tool allowlist config (`echo`, `http_request`, `file_read`)
- `src/guardflow/policy.py` — `Policy` model with `load()` / `is_allowed()`; `PolicyViolation` exception
- `PolicyError` model in `src/guardflow/models.py` — `UNAUTHORIZED_TOOL` structured error
- `policy show` subcommand — prints the active tool allowlist as JSON
- `policy validate` subcommand — validates the policy config file and reports errors
- `--policy` / `-p` option on `guardflow run` — path to policy config file (default: `policy.json`)
- Allowlist policy test suite (`pytest -m allowlist_policy`)

### Changed
- `pipeline.authorize()` now enforces the allowlist; raises `PolicyViolation` for blocked tools
- `run_pipeline()` now requires a `Policy` argument
- `guardflow run` loads policy before executing; returns `UNAUTHORIZED_TOOL` error on rejection
- `policy` command replaced with a subcommand group (`show`, `validate`)
- Bumped version to `0.3.0`

## [0.2.0] - 2026-02-24

### Added
- Pydantic v2 models (`Actor`, `ToolCall`, `RunRequest`, `ToolResult`, `SchemaError`) in `src/guardflow/models.py`
- Strict schema enforcement in `pipeline.validate()` — raises `pydantic.ValidationError` on invalid input
- `SCHEMA_REJECTED` error response on stderr with exit code 1 for schema violations
- Schema validation test suite (`pytest -m schema_validation`)
- Updated all 5 example JSON files to `{actor, tool_call}` schema

### Changed
- `pipeline.validate()` now returns `RunRequest` instead of `dict`
- `pipeline.authorize()` and `pipeline.execute()` now accept/return typed models
- `run_pipeline()` returns `ToolResult` instead of `dict`
- CLI `run` command prints `ToolResult.model_dump_json()` output
- Bumped version to `0.2.0`

## [0.1.0] - 2026-02-24

### Added
- Initial project scaffold with `uv` / `src/` layout
- Typer CLI with `run`, `policy`, and `redteam` commands
- Stub execution pipeline: `validate → authorize → execute`
- `guardflow run --input <json>` command parses JSON and runs the pipeline
- CLI contract test suite (`pytest -m cli_contract`)
- README with install and usage instructions
