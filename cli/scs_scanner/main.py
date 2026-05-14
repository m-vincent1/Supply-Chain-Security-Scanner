from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from scs_scanner import __version__
from scs_scanner.commands import cmd_scan, cmd_sbom, cmd_validate

app = typer.Typer(
    name="scs-scanner",
    help="Supply Chain Security Scanner — analyze dependencies, detect vulnerabilities, generate SBOM.",
    add_completion=False,
)
console = Console()


@app.command("scan")
def scan(
    path: Path = typer.Argument(..., help="Path to the project to scan."),
    fmt: str = typer.Option(
        "terminal",
        "--format", "-f",
        help="Output format: terminal, json, markdown, html.",
    ),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Write report to this file."),
    fail_on: Optional[str] = typer.Option(
        None,
        "--fail-on",
        help="Exit with code 1 if vulnerabilities at or above this level exist (critical|high|medium|low).",
    ),
    offline: bool = typer.Option(True, "--offline/--online", help="Use offline vulnerability database."),
    include_dev: bool = typer.Option(True, "--include-dev/--exclude-dev", help="Include development dependencies."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed vulnerability table."),
) -> None:
    """Scan a project for vulnerable dependencies."""
    cmd_scan(path, fmt, output, fail_on, offline, include_dev, verbose)


@app.command("sbom")
def sbom(
    path: Path = typer.Argument(..., help="Path to the project."),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Write SBOM to this file."),
) -> None:
    """Generate a simplified SBOM for a project."""
    cmd_sbom(path, output)


@app.command("validate")
def validate(
    path: Path = typer.Argument(..., help="Path to the project to validate."),
) -> None:
    """Check if a project contains supported dependency files."""
    cmd_validate(path)


@app.command("version")
def version() -> None:
    """Print the scanner version."""
    console.print(f"scs-scanner v{__version__}")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
