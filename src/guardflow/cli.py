"""Guardflow CLI entry point."""

import json
import logging
import sys
from pathlib import Path

import typer
from pydantic import ValidationError
from rich import print as rprint
from rich.logging import RichHandler

from guardflow.models import PolicyError, RbacError, SandboxError, SchemaError
from guardflow.pipeline import run_pipeline
from guardflow.policy import Policy, PolicyViolation
from guardflow.rbac import RbacDenial, RbacPolicy
from guardflow.redteam import run_suite
from guardflow.sandbox import SandboxError as SandboxExc

app = typer.Typer(
    name="guardflow",
    help="Secure AI tool-call execution pipeline with policy enforcement.",
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]},
)

policy_app = typer.Typer(name="policy", help="Manage execution policies.")
app.add_typer(policy_app)


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
    policy_path: str = typer.Option("policy.json", "--policy", "-p", help="Path to policy config file."),
    rbac_model: str = typer.Option("model.conf", "--rbac-model", help="Path to Casbin model.conf file."),
    rbac_policy: str = typer.Option("rbac_policy.csv", "--rbac-policy", help="Path to Casbin RBAC policy CSV file."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show pipeline debug logs."),
) -> None:
    """Parse a tool-call request and run it through the pipeline.

    --input accepts either an inline JSON string or a path to a .json file:

    \b
      guardflow run -i examples/echo.json
      guardflow run -i examples/shell_command.json
      guardflow run -i '{"actor":{"id":"u1","role":"viewer"},"tool_call":{"tool":"echo","args":{"text":"hi"}}}'
    """
    if verbose:
        logging.basicConfig(
            level=logging.INFO,
            format="%(message)s",
            handlers=[RichHandler(show_path=False)],
        )

    raw = input
    path = Path(raw)
    if path.suffix == ".json" and path.exists():
        raw = path.read_text()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        rprint(f"[red]Error:[/red] invalid JSON — {exc}", file=sys.stderr)
        raise typer.Exit(code=1)

    try:
        loaded_policy = Policy.load(Path(policy_path))
    except FileNotFoundError:
        rprint(f"[red]Error:[/red] policy file not found: {policy_path}", file=sys.stderr)
        raise typer.Exit(code=1)

    try:
        loaded_rbac = RbacPolicy.load(Path(rbac_model), Path(rbac_policy))
    except (FileNotFoundError, OSError) as exc:
        rprint(f"[red]Error:[/red] RBAC config not found — {exc}", file=sys.stderr)
        raise typer.Exit(code=1)

    try:
        result = run_pipeline(data, loaded_policy, loaded_rbac)
        rprint(result.model_dump_json(indent=2))
    except ValidationError as exc:
        err = SchemaError(detail=str(exc))
        rprint(err.model_dump_json(indent=2), file=sys.stderr)
        raise typer.Exit(code=1)
    except PolicyViolation as exc:
        err = PolicyError(tool=exc.tool, detail=f"Tool '{exc.tool}' is not in the allowlist")
        rprint(err.model_dump_json(indent=2), file=sys.stderr)
        raise typer.Exit(code=1)
    except RbacDenial as exc:
        err = RbacError(
            role=exc.role,
            tool=exc.tool,
            detail=f"Role '{exc.role}' is not permitted to use tool '{exc.tool}'",
        )
        rprint(err.model_dump_json(indent=2), file=sys.stderr)
        raise typer.Exit(code=1)
    except SandboxExc as exc:
        err = SandboxError(detail=exc.message)
        rprint(err.model_dump_json(indent=2), file=sys.stderr)
        raise typer.Exit(code=1)


@policy_app.command("show")
def policy_show(
    policy_path: str = typer.Option("policy.json", "--policy", "-p", help="Path to policy config file."),
) -> None:
    """Show the current tool allowlist."""
    try:
        loaded_policy = Policy.load(Path(policy_path))
    except FileNotFoundError:
        rprint(f"[red]Error:[/red] policy file not found: {policy_path}", file=sys.stderr)
        raise typer.Exit(code=1)
    rprint(loaded_policy.model_dump_json(indent=2))


@policy_app.command("validate")
def policy_validate(
    policy_path: str = typer.Option("policy.json", "--policy", "-p", help="Path to policy config file."),
) -> None:
    """Validate the policy config file."""
    try:
        Policy.load(Path(policy_path))
    except FileNotFoundError:
        rprint(f"[red]Error:[/red] policy file not found: {policy_path}", file=sys.stderr)
        raise typer.Exit(code=1)
    except Exception as exc:
        rprint(f"[red]Error:[/red] invalid policy file — {exc}", file=sys.stderr)
        raise typer.Exit(code=1)
    rprint("[green]Policy file is valid.[/green]")


@policy_app.command("check")
def policy_check(
    role: str = typer.Option(..., "--role", help="Actor role to check."),
    tool: str = typer.Option(..., "--tool", help="Tool name to check."),
    rbac_model: str = typer.Option("model.conf", "--rbac-model", help="Path to Casbin model.conf file."),
    rbac_policy: str = typer.Option("rbac_policy.csv", "--rbac-policy", help="Path to Casbin RBAC policy CSV file."),
) -> None:
    """Check whether a role is permitted to use a tool under the RBAC policy."""
    try:
        loaded_rbac = RbacPolicy.load(Path(rbac_model), Path(rbac_policy))
    except (FileNotFoundError, OSError) as exc:
        rprint(f"[red]Error:[/red] RBAC config not found — {exc}", file=sys.stderr)
        raise typer.Exit(code=1)

    if loaded_rbac.is_allowed(role, tool):
        rprint(f"[green]ALLOWED:[/green] role '{role}' may use tool '{tool}'")
    else:
        rprint(f"[red]DENIED:[/red] role '{role}' is not permitted to use tool '{tool}'", file=sys.stderr)
        raise typer.Exit(code=1)


redteam_app = typer.Typer(name="redteam", help="Red-team adversarial guardrail regression suite.")
app.add_typer(redteam_app)


@redteam_app.command("run")
def redteam_run(
    policy_path: str = typer.Option("policy.json", "--policy", "-p", help="Path to policy config file."),
    rbac_model: str = typer.Option("model.conf", "--rbac-model", help="Path to Casbin model.conf file."),
    rbac_policy: str = typer.Option("rbac_policy.csv", "--rbac-policy", help="Path to Casbin RBAC policy CSV file."),
) -> None:
    """Run the red-team adversarial regression suite against the active policy."""
    from rich.console import Console
    from rich.table import Table

    try:
        loaded_policy = Policy.load(Path(policy_path))
    except FileNotFoundError:
        rprint(f"[red]Error:[/red] policy file not found: {policy_path}", file=sys.stderr)
        raise typer.Exit(code=1)
    try:
        loaded_rbac = RbacPolicy.load(Path(rbac_model), Path(rbac_policy))
    except (FileNotFoundError, OSError) as exc:
        rprint(f"[red]Error:[/red] RBAC config not found — {exc}", file=sys.stderr)
        raise typer.Exit(code=1)

    results = run_suite(loaded_policy, loaded_rbac)

    console = Console()
    table = Table(title="Red-team Results", show_lines=True)
    table.add_column("", width=2)
    table.add_column("Case", style="bold")
    table.add_column("Expected")
    table.add_column("Actual")
    for r in results:
        icon = "[green]✓[/green]" if r.passed else "[red]✗[/red]"
        style = "green" if r.passed else "red"
        table.add_row(icon, r.case.name, r.case.expected, f"[{style}]{r.actual}[/{style}]")
    console.print(table)

    passed = sum(1 for r in results if r.passed)
    total = len(results)
    if passed == total:
        rprint(f"[green]{passed}/{total} cases passed.[/green]")
    else:
        rprint(f"[red]{passed}/{total} cases passed.[/red]", file=sys.stderr)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
