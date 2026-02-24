"""Guardflow CLI entry point."""

import json
import logging
import sys

import typer
from pydantic import ValidationError
from rich import print as rprint
from rich.logging import RichHandler

from guardflow.models import SchemaError
from guardflow.pipeline import run_pipeline

app = typer.Typer(
    name="guardflow",
    help="Secure AI tool-call execution pipeline with policy enforcement.",
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]},
)


@app.command()
def run(
    input: str = typer.Option(
        ...,
        "--input",
        "-i",
        help=(
            "JSON-encoded tool-call request, or a path to a .json file. "
            "Examples: examples/echo.json, examples/shell_command.json, "
            "examples/http_request.json, examples/file_read.json, examples/code_exec.json"
        ),
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show pipeline debug logs."),
) -> None:
    """Parse a tool-call request and run it through the pipeline.

    --input accepts either an inline JSON string or a path to a .json file:

    \b
      guardflow run -i examples/echo.json
      guardflow run -i examples/shell_command.json
      guardflow run -i '{"actor":{"id":"u1","role":"viewer"},"tool_call":{"tool":"echo","args":{"text":"hi"}}}'
    """
    import pathlib

    if verbose:
        logging.basicConfig(
            level=logging.INFO,
            format="%(message)s",
            handlers=[RichHandler(show_path=False)],
        )

    raw = input
    path = pathlib.Path(raw)
    if path.suffix == ".json" and path.exists():
        raw = path.read_text()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        rprint(f"[red]Error:[/red] invalid JSON — {exc}", file=sys.stderr)
        raise typer.Exit(code=1)

    try:
        result = run_pipeline(data)
        rprint(result.model_dump_json(indent=2))
    except ValidationError as exc:
        err = SchemaError(detail=str(exc))
        rprint(err.model_dump_json(indent=2), file=sys.stderr)
        raise typer.Exit(code=1)


@app.command()
def policy() -> None:
    """Manage execution policies (coming soon)."""
    rprint("[yellow]Policy management coming soon.[/yellow]")


@app.command()
def redteam() -> None:
    """Run the red-team guardrail regression suite (coming soon)."""
    rprint("[yellow]Red-team suite coming soon.[/yellow]")


if __name__ == "__main__":
    app()
