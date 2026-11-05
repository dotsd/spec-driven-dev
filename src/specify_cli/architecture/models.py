"""Data models for the Multi-File Architecture Memory Engine."""

from __future__ import annotations

from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class SymbolType(str, Enum):
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    INTERFACE = "interface"
    STRUCT = "struct"
    MODEL = "model"
    ENDPOINT = "endpoint"
    TYPE = "type"
    ENUM = "enum"
    VARIABLE = "variable"


class SymbolNode(BaseModel):
    id: str
    name: str
    symbol_type: SymbolType
    file_path: str
    line_start: int
    line_end: int
    docstring: str | None = None
    signature: str | None = None
    summary: str | None = None
    references: list[str] = Field(default_factory=list)
    decorators_or_annotations: list[str] = Field(default_factory=list)
    specified_in: str | None = None


class RouteNode(BaseModel):
    method: str
    path: str
    handler_symbol: str | None = None
    file_path: str
    line: int


class ModelNode(BaseModel):
    name: str
    kind: str
    file_path: str
    fields: list[str] = Field(default_factory=list)
    line: int


class RequirementNode(BaseModel):
    """A functional requirement or user story extracted from specs or PRDs."""

    id: str
    title: str
    source_doc: str
    section: str | None = None
    description: str | None = None
    acceptance_criteria: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class TicketNode(BaseModel):
    """A work item / issue from JIRA, GitHub Issues, or ticket sheets."""

    key: str
    summary: str
    status: str = "Open"
    source_file: str
    description: str | None = None
    target_subsystem: str | None = None
    assignee: str | None = None
    components: list[str] = Field(default_factory=list)


class TraceabilityLink(BaseModel):
    """Link connecting a functional requirement or ticket to code components."""

    item_id: str
    item_type: str  # "requirement", "user_story", "ticket"
    source_doc: str
    title: str
    code_file: str
    symbol_or_route: str | None = None
    match_reason: str  # "explicit_tag", "symbol_name", "route_path", "spec_file"


class FileNode(BaseModel):
    path: str
    language: str
    sha256: str
    size_bytes: int
    line_count: int
    mtime: float = 0.0
    imports: list[str] = Field(default_factory=list)
    symbols: list[str] = Field(default_factory=list)
    routes: list[RouteNode] = Field(default_factory=list)
    models: list[ModelNode] = Field(default_factory=list)


class ArchitectureCache(BaseModel):
    """Persistent cache for delta refreshes."""

    version: str = "1.0"
    project_root: str
    updated_at: str
    file_hashes: dict[str, str] = Field(default_factory=dict)
    file_mtimes: dict[str, float] = Field(default_factory=dict)
    files: dict[str, FileNode] = Field(default_factory=dict)
    symbols: dict[str, SymbolNode] = Field(default_factory=dict)
    requirements: list[RequirementNode] = Field(default_factory=list)
    tickets: list[TicketNode] = Field(default_factory=list)
    settings: dict[str, Any] = Field(default_factory=dict)


class ArchitectureSummary(BaseModel):
    total_files: int
    total_symbols: int
    total_routes: int
    total_models: int
    total_requirements: int
    total_tickets: int
    languages: dict[str, int]
    generated_categories: list[str]
    delta_files_reparsed: int
    duration_ms: float
