"""CLI command adapter for ``specify architecture generate``."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.panel import Panel
from rich.table import Table

from .._console import console
from ._commands import architecture_app
from ._operation_generate import (
    ArchitectureGenerateRequest,
    run_architecture_generate,
)


@architecture_app.command("generate")
def generate(
    path: Annotated[
        Path,
        typer.Option(
            "--path",
            "-p",
            help="Target project root directory (defaults to current directory).",
        ),
    ] = Path("."),
    docs_dir: Annotated[
        list[str] | None,
        typer.Option(
            "--docs-dir",
            "-d",
            help="Additional functional documentation directory to index.",
        ),
    ] = None,
    tickets: Annotated[
        str | None,
        typer.Option(
            "--tickets",
            "-t",
            help="Path to JIRA or issue tracking sheet (CSV, JSON, or MD).",
        ),
    ] = None,
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            "-f",
            help="Bypass cache and force a complete re-parse of all files.",
        ),
    ] = False,
    json_output: Annotated[
        bool,
        typer.Option(
            "--json",
            help="Output generation summary as JSON.",
        ),
    ] = False,
) -> None:
    """Analyze codebase and generate category-based architecture memory."""
    project_path = path.resolve()
    docs_dirs_list = docs_dir or []
    ticket_paths_list = [tickets] if tickets else []

    request = ArchitectureGenerateRequest(
        project_path=project_path,
        docs_dirs=docs_dirs_list,
        ticket_paths=ticket_paths_list,
        force=force,
    )

    result = run_architecture_generate(request)

    if not result.success or not result.summary:
        if json_output:
            console.print_json(data={"success": False, "error": result.error_message})
        else:
            console.print(f"[bold red]Error generating architecture memory:[/bold red] {result.error_message}")
        raise typer.Exit(code=1)

    s = result.summary

    if json_output:
        console.print_json(data={
            "success": True,
            "total_files": s.total_files,
            "total_symbols": s.total_symbols,
            "total_routes": s.total_routes,
            "total_models": s.total_models,
            "total_requirements": s.total_requirements,
            "total_tickets": s.total_tickets,
            "languages": s.languages,
            "generated_categories": s.generated_categories,
            "delta_files_reparsed": s.delta_files_reparsed,
            "duration_ms": s.duration_ms,
        })
        return

    # Rich human-friendly output
    table = Table(title="Architecture Memory Generated", show_header=True, header_style="bold cyan")
    table.add_column("Category / Metric", style="bold")
    table.add_column("Count / Details", style="green")

    table.add_row("Total Files Analyzed", str(s.total_files))
    table.add_row("Files Re-parsed (Delta)", str(s.delta_files_reparsed))
    table.add_row("API Endpoints & Routes", str(s.total_routes))
    table.add_row("Domain Models & Schemas", str(s.total_models))
    table.add_row("Functional Requirements", str(s.total_requirements))
    table.add_row("Work Items / Tickets", str(s.total_tickets))
    table.add_row("Languages", ", ".join(f"{k} ({v})" for k, v in s.languages.items()) or "None")
    table.add_row("Duration", f"{s.duration_ms:.2f} ms")

    console.print(table)
    console.print()
    console.print(
        Panel(
            "[bold green]✔ Architecture memory updated at:[/bold green] `.specify/memory/architecture/`\n"
            "- `overview.md` (Topology & Summary)\n"
            "- `api-surface.md` (Routes & Endpoints)\n"
            "- `domain-models.md` (Schemas & Entities)\n"
            "- `traceability.md` (Functional Specs & Tickets $\\leftrightarrow$ Code)\n"
            "- `dependencies.md` (Coupling & Blast Radius)\n"
            "- `test-map.md` (Source to Test Mapping)",
            title="Spec Kit Architecture Engine",
            border_style="cyan",
        )
    )
