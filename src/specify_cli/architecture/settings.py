"""Persistent settings for architecture memory and custom doc/ticket paths."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


SETTINGS_FILE_NAME = "settings.json"


def get_settings_path(project_root: Path) -> Path:
    specify_dir = project_root / ".specify"
    return specify_dir / SETTINGS_FILE_NAME


def load_architecture_settings(project_root: Path) -> dict[str, Any]:
    """Load settings from .specify/settings.json."""
    settings_file = get_settings_path(project_root)
    if not settings_file.exists():
        return {
            "functional_docs_paths": [],
            "ticket_paths": [],
        }
    try:
        data = json.loads(settings_file.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return {"functional_docs_paths": [], "ticket_paths": []}
        return data
    except Exception:
        return {"functional_docs_paths": [], "ticket_paths": []}


def save_architecture_settings(project_root: Path, settings: dict[str, Any]) -> None:
    """Save settings to .specify/settings.json."""
    settings_file = get_settings_path(project_root)
    settings_file.parent.mkdir(parents=True, exist_ok=True)
    try:
        settings_file.write_text(json.dumps(settings, indent=2), encoding="utf-8")
    except Exception:
        pass


def register_doc_path(project_root: Path, doc_path: str) -> None:
    """Register and persist a functional documentation directory path."""
    settings = load_architecture_settings(project_root)
    paths: list[str] = settings.get("functional_docs_paths", [])
    if doc_path not in paths:
        paths.append(doc_path)
        settings["functional_docs_paths"] = paths
        save_architecture_settings(project_root, settings)


def register_ticket_path(project_root: Path, ticket_path: str) -> None:
    """Register and persist a ticket sheet path."""
    settings = load_architecture_settings(project_root)
    paths: list[str] = settings.get("ticket_paths", [])
    if ticket_path not in paths:
        paths.append(ticket_path)
        settings["ticket_paths"] = paths
        save_architecture_settings(project_root, settings)
