from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()
err_console = Console(stderr=True)


SEVERITY_RANK = {"critical": 4, "high": 3, "medium": 2, "low": 1}
FAIL_ON_RANK = {"critical": 4, "high": 3, "medium": 2, "low": 1}


def cmd_scan(
    path: Path,
    fmt: str,
    output: Optional[Path],
    fail_on: Optional[str],
    offline: bool,
    include_dev: bool,
    verbose: bool,
) -> None:
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

    from app.services.scan_service import run_scan
    from app.reporters import generate_report

    if not path.exists():
        err_console.print(f"[red]Error:[/red] Path not found: {path}")
        raise typer.Exit(code=1)

    with console.status(f"Scanning [bold]{path}[/bold]..."):
        result = run_scan(path, include_dev=include_dev, offline=offline)

    _print_summary(result, verbose)

    if fmt != "terminal":
        content = generate_report(result, fmt=fmt, output_path=output)
        if output:
            console.print(f"\nReport saved to [green]{output}[/green]")
        else:
            console.print(content)

    if fail_on:
        fail_rank = FAIL_ON_RANK.get(fail_on.lower(), 0)
        sv = result.vulnerabilities_by_severity
        triggered = any(
            count > 0
            for sev, count in sv.items()
            if SEVERITY_RANK.get(sev, 0) >= fail_rank
        )
        if triggered:
            err_console.print(
                f"\n[red]FAIL:[/red] Vulnerabilities at or above '{fail_on}' level detected. Exiting with code 1."
            )
            raise typer.Exit(code=1)


def cmd_sbom(path: Path, output: Optional[Path]) -> None:
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))
    from app.services.scan_service import run_scan

    if not path.exists():
        err_console.print(f"[red]Error:[/red] Path not found: {path}")
        raise typer.Exit(code=1)

    with console.status("Generating SBOM..."):
        result = run_scan(path)

    import json
    sbom_data = result.sbom.model_dump(mode="json")
    content = json.dumps(sbom_data, indent=2, default=str)

    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(content, encoding="utf-8")
        console.print(f"SBOM saved to [green]{output}[/green]")
    else:
        console.print(content)


def cmd_validate(path: Path) -> None:
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))
    from app.parsers import detect_and_parse, SUPPORTED_FILES

    if not path.exists():
        err_console.print(f"[red]Error:[/red] Path not found: {path}")
        raise typer.Exit(code=1)

    found_files = []
    for f in path.rglob("*"):
        if f.is_file() and f.name in SUPPORTED_FILES:
            found_files.append(f)

    if not found_files:
        console.print("[yellow]No supported dependency files found.[/yellow]")
        console.print(f"Supported: {', '.join(sorted(SUPPORTED_FILES))}")
        raise typer.Exit(code=1)

    console.print(f"[green]Found {len(found_files)} supported file(s):[/green]")
    for f in found_files:
        console.print(f"  {f.relative_to(path)}")


def _print_summary(result, verbose: bool) -> None:
    sv = result.vulnerabilities_by_severity
    level = result.risk_score.level.value
    score = result.risk_score.total

    level_color = {"Critical": "red", "High": "orange3", "Medium": "yellow", "Low": "green"}.get(level, "white")

    console.print(f"\n[bold]Project:[/bold] {result.project_name}")
    console.print(f"[bold]Dependencies analyzed:[/bold] {result.total_dependencies}")
    console.print(f"[bold]Vulnerabilities found:[/bold] {result.total_vulnerabilities}")
    if result.total_vulnerabilities > 0:
        console.print(f"  Critical: [red]{sv.get('critical', 0)}[/red]")
        console.print(f"  High:     [orange3]{sv.get('high', 0)}[/orange3]")
        console.print(f"  Medium:   [yellow]{sv.get('medium', 0)}[/yellow]")
        console.print(f"  Low:      [green]{sv.get('low', 0)}[/green]")
    console.print(f"[bold]Risk score:[/bold] [{level_color}]{score}/100[/{level_color}]")
    console.print(f"[bold]Status:[/bold] [{level_color}]{level}[/{level_color}]")

    if verbose and result.vulnerabilities:
        table = Table(title="Vulnerabilities", box=box.SIMPLE)
        table.add_column("Package", style="bold")
        table.add_column("Version")
        table.add_column("Severity")
        table.add_column("CVSS")
        table.add_column("ID")
        for v in sorted(result.vulnerabilities, key=lambda x: x.cvss, reverse=True):
            sev_color = {"critical": "red", "high": "orange3", "medium": "yellow", "low": "green"}.get(v.severity.value, "white")
            table.add_row(
                v.package,
                v.installed_version or "unknown",
                f"[{sev_color}]{v.severity.value.upper()}[/{sev_color}]",
                str(v.cvss),
                v.vulnerability_id,
            )
        console.print(table)
