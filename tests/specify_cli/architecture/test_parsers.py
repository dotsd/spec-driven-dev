"""Unit tests for AST and Document/Ticket parsers."""

from __future__ import annotations

from pathlib import Path
from specify_cli.architecture.parsers import (
    DataMLParser,
    DocumentParser,
    GoParser,
    PythonParser,
    RustParser,
    WebParser,
)


def test_python_parser(tmp_path: Path) -> None:
    code = """
import os
from fastapi import FastAPI, APIRouter
from pydantic import BaseModel

app = FastAPI()

class UserCreate(BaseModel):
    username: str
    email: str

@app.post("/api/v1/users")
def create_user(user: UserCreate):
    return {"status": "ok"}
"""
    f = tmp_path / "app.py"
    f.write_text(code, encoding="utf-8")

    parser = PythonParser()
    assert parser.can_parse(f)

    imports, symbols, routes, models = parser.parse(f, "app.py", code)
    assert "os" in imports
    assert "fastapi.FastAPI" in imports
    assert any(m.name == "UserCreate" for m in models)
    assert any(r.path == "/api/v1/users" and r.method == "POST" for r in routes)
    assert any(s.name == "create_user" for s in symbols)


def test_web_parser(tmp_path: Path) -> None:
    code = """
import express from 'express';
import { z } from 'zod';

const router = express.Router();

export interface AccountProfile {
    id: string;
    displayName: string;
}

export const AccountSchema = z.object({
    username: z.string(),
    age: z.number(),
});

router.get('/api/accounts', (req, res) => {
    res.json([]);
});
"""
    f = tmp_path / "server.ts"
    f.write_text(code, encoding="utf-8")

    parser = WebParser()
    assert parser.can_parse(f)

    imports, symbols, routes, models = parser.parse(f, "server.ts", code)
    assert "express" in imports
    assert any(m.name == "AccountProfile" for m in models)
    assert any(m.name == "AccountSchema" for m in models)
    assert any(r.path == "/api/accounts" and r.method == "GET" for r in routes)


def test_go_parser(tmp_path: Path) -> None:
    code = """
package main

import (
    "github.com/gin-gonic/gin"
)

type Customer struct {
    ID string
    Name string
}

func main() {
    r := gin.Default()
    r.POST("/api/customers", CreateCustomer)
}
"""
    f = tmp_path / "main.go"
    f.write_text(code, encoding="utf-8")

    parser = GoParser()
    assert parser.can_parse(f)

    imports, symbols, routes, models = parser.parse(f, "main.go", code)
    assert "github.com/gin-gonic/gin" in imports
    assert any(m.name == "Customer" for m in models)
    assert any(r.path == "/api/customers" and r.method == "POST" for r in routes)


def test_rust_parser(tmp_path: Path) -> None:
    code = """
use actix_web::{get, web, App, HttpServer, Responder};

pub struct Order {
    pub id: u64,
    pub amount: f64,
}

#[get("/api/orders")]
async fn list_orders() -> impl Responder {
    "orders"
}
"""
    f = tmp_path / "main.rs"
    f.write_text(code, encoding="utf-8")

    parser = RustParser()
    assert parser.can_parse(f)

    imports, symbols, routes, models = parser.parse(f, "main.rs", code)
    assert any("actix_web" in imp for imp in imports)
    assert any(m.name == "Order" for m in models)
    assert any(r.path == "/api/orders" and r.method == "GET" for r in routes)


def test_sql_and_prisma_parser(tmp_path: Path) -> None:
    sql_code = """
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    created_at TIMESTAMP
);
"""
    sql_file = tmp_path / "schema.sql"
    parser = DataMLParser()
    imports, symbols, routes, models = parser.parse(sql_file, "schema.sql", sql_code)
    assert any(m.name == "users" and m.kind == "sql_table" for m in models)

    prisma_code = """
model Subscription {
    id        String   @id @default(cuid())
    userId    String
    plan      String
    active    Boolean  @default(true)
}
"""
    prisma_file = tmp_path / "schema.prisma"
    imports, symbols, routes, models = parser.parse(prisma_file, "schema.prisma", prisma_code)
    assert any(m.name == "Subscription" and m.kind == "prisma_model" for m in models)


def test_doc_parser_markdown(tmp_path: Path) -> None:
    doc_content = """# Authentication & SSO Specification

## User Story 1 - OAuth Login
Users can authenticate with Google or GitHub SSO.

- **FR-001**: System must validate OAuth state parameter.
  - Scenario: Invalid state token redirects with error.
- **FR-002**: System must issue JWT access token upon successful exchange.
"""
    doc_file = tmp_path / "auth.md"
    doc_file.write_text(doc_content, encoding="utf-8")

    parser = DocumentParser()
    reqs = parser.parse_markdown_doc(doc_file, "docs/auth.md", doc_content)

    assert len(reqs) >= 2
    req_ids = {r.id for r in reqs}
    assert "FR-001" in req_ids or "US-001" in req_ids


def test_doc_parser_tickets(tmp_path: Path) -> None:
    csv_content = """Issue key,Summary,Status,Component/s,Description
PROJ-101,Implement Google OAuth,In Progress,auth,Add OAuth provider
PROJ-102,Create Billing Table,Done,billing,Add subscriptions table
"""
    csv_file = tmp_path / "jira.csv"
    csv_file.write_text(csv_content, encoding="utf-8")

    parser = DocumentParser()
    tickets = parser.parse_ticket_file(csv_file, "jira.csv", csv_content)

    assert len(tickets) == 2
    t1 = tickets[0]
    assert t1.key == "PROJ-101"
    assert t1.status == "In Progress"
    assert t1.target_subsystem == "auth"
