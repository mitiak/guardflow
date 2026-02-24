# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-02-24

### Added
- Initial project scaffold with `uv` / `src/` layout
- Typer CLI with `run`, `policy`, and `redteam` commands
- Stub execution pipeline: `validate → authorize → execute`
- `guardflow run --input <json>` command parses JSON and runs the pipeline
- CLI contract test suite (`pytest -m cli_contract`)
- README with install and usage instructions
