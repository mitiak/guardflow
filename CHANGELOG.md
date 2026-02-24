# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
