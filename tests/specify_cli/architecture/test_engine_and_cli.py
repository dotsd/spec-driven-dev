"""End-to-end tests for ArchitectureEngine and CLI command."""

from __future__ import annotations

import json
from pathlib import Path
from typer.testing import CliRunner

from specify_cli import app
from specify_cli.architecture.engine import ArchitectureEngine
from specify_cli.architecture.settings import load_architecture_settings


def test_engine_end_to_end_generation(tmp_path: Path) -> None:
    # 1. Setup mock codebase
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "user_service.py").write_text(
        """
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
    id: str
    email: str

@app.get("/api/v1/users")
def get_users():
    return []
""",
        encoding="utf-8",
    )

    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_user_service.py").write_text(
        """
def test_get_users():
    assert True
""",
        encoding="utf-8",
    )

    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "prd.md").write_text(
        """# Product Requirements Document

## User Accounts
- **FR-001**: System must support retrieving all users via /api/v1/users.
""",
        encoding="utf-8",
    )

    tickets_file = tmp_path / "jira.csv"
    tickets_file.write_text(
        """Issue key,Summary,Status
PROJ-50,Expose user listing endpoint,Done
""",
        encoding="utf-8",
    )

    # 2. Run engine
    engine = ArchitectureEngine(tmp_path)
    summary = engine.generate(
        docs_dirs=["docs"],
        ticket_paths=["jira.csv"],
    )

    assert summary.total_files >= 2
    assert summary.total_routes == 1
    assert summary.total_models == 1
    assert summary.total_requirements >= 1
    assert summary.total_tickets == 1

    # 3. Verify category files written in .specify/memory/architecture/
    arch_dir = tmp_path / ".specify/memory/architecture"
    assert (arch_dir / "overview.md").exists()
    assert (arch_dir / "api-surface.md").exists()
    assert (arch_dir / "domain-models.md").exists()
    assert (arch_dir / "traceability.md").exists()
    assert (arch_dir / "dependencies.md").exists()
    assert (arch_dir / "test-map.md").exists()

    # Verify content in traceability.md
    trace_content = (arch_dir / "traceability.md").read_text(encoding="utf-8")
    assert "PROJ-50" in trace_content
    assert "FR-001" in trace_content or "User Accounts" in trace_content

    # Verify content in api-surface.md
    api_content = (arch_dir / "api-surface.md").read_text(encoding="utf-8")
    assert "/api/v1/users" in api_content

    # Verify content in domain-models.md
    models_content = (arch_dir / "domain-models.md").read_text(encoding="utf-8")
    assert "User" in models_content

    # 4. Verify settings persistence
    settings = load_architecture_settings(tmp_path)
    assert "docs" in settings.get("functional_docs_paths", [])
    assert "jira.csv" in settings.get("ticket_paths", [])

    # 5. Delta refresh test: modify 1 file
    (src_dir / "user_service.py").write_text(
        """
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
    id: str
    email: str

@app.get("/api/v1/users")
def get_users():
    return []

@app.post("/api/v1/users")
def create_user(u: User):
    return u
""",
        encoding="utf-8",
    )

    delta_summary = engine.generate()
    # Only 1 file should be re-parsed!
    assert delta_summary.delta_files_reparsed == 1
    assert delta_summary.total_routes == 2


def test_cli_architecture_generate(tmp_path: Path) -> None:
    runner = CliRunner()

    # Create dummy file in tmp_path
    f = tmp_path / "hello.py"
    f.write_text("print('hello')", encoding="utf-8")

    result = runner.invoke(app, ["architecture", "generate", "--path", str(tmp_path), "--json"])
    assert result.exit_code == 0

    data = json.loads(result.output)
    assert data["success"] is True
    assert data["total_files"] == 1
    assert "overview.md" in data["generated_categories"]
