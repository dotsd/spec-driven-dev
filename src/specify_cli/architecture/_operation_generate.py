"""Shared application operation for architecture memory generation."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from .engine import ArchitectureEngine
from .models import ArchitectureSummary


@dataclass(frozen=True)
class ArchitectureGenerateRequest:
    """Typed request contract for architecture generation."""

    project_path: Path
    docs_dirs: list[str] = field(default_factory=list)
    ticket_paths: list[str] = field(default_factory=list)
    force: bool = False


@dataclass(frozen=True)
class ArchitectureGenerateResult:
    """Typed result contract for architecture generation."""

    summary: ArchitectureSummary | None
    success: bool
    error_message: str | None = None


@dataclass(frozen=True)
class ArchitectureOperationDescriptor:
    """Stable metadata shared by delivery adapters for architecture generation."""

    operation_id: Literal["architecture.generate"]
    contract_version: Literal["1"]
    capabilities: frozenset[Literal["local-read", "local-write"]]
    network_access: Literal["none"]


ARCHITECTURE_GENERATE_OPERATION = ArchitectureOperationDescriptor(
    operation_id="architecture.generate",
    contract_version="1",
    capabilities=frozenset({"local-read", "local-write"}),
    network_access="none",
)


def run_architecture_generate(
    request: ArchitectureGenerateRequest,
) -> ArchitectureGenerateResult:
    """Execute the architecture generation operation."""
    try:
        engine = ArchitectureEngine(request.project_path)
        summary = engine.generate(
            docs_dirs=request.docs_dirs,
            ticket_paths=request.ticket_paths,
            force=request.force,
        )
        return ArchitectureGenerateResult(summary=summary, success=True)
    except Exception as exc:
        return ArchitectureGenerateResult(
            summary=None,
            success=False,
            error_message=str(exc),
        )
