"""Shared infrastructure and registration for ``specify architecture`` commands."""

from __future__ import annotations

import typer

architecture_app = typer.Typer(
    name="architecture",
    help="Manage and generate category-based codebase architecture memory.",
    no_args_is_help=True,
)


def register(app: typer.Typer) -> None:
    """Attach the architecture command group to the root Typer app."""
    # isort: off
    from . import command_generate  # noqa: F401 — registers handler via decorator
    # isort: on

    app.add_typer(architecture_app, name="architecture")
