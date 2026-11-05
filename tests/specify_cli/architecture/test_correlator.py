"""Unit tests for the Traceability Correlator."""

from __future__ import annotations

from specify_cli.architecture.correlator import TraceabilityCorrelator
from specify_cli.architecture.models import (
    FileNode,
    ModelNode,
    RequirementNode,
    RouteNode,
    TicketNode,
)


def test_correlator_matches_by_route_and_model() -> None:
    files = {
        "src/auth/routes.py": FileNode(
            path="src/auth/routes.py",
            language="python",
            sha256="abc",
            size_bytes=100,
            line_count=20,
            routes=[
                RouteNode(
                    method="POST",
                    path="/api/v1/auth/login",
                    handler_symbol="login_handler",
                    file_path="src/auth/routes.py",
                    line=10,
                )
            ],
            models=[
                ModelNode(
                    name="LoginRequest",
                    kind="pydantic",
                    file_path="src/auth/routes.py",
                    fields=["username", "password"],
                    line=5,
                )
            ],
        ),
        "src/billing/service.py": FileNode(
            path="src/billing/service.py",
            language="python",
            sha256="def",
            size_bytes=120,
            line_count=25,
            models=[
                ModelNode(
                    name="SubscriptionPlan",
                    kind="pydantic",
                    file_path="src/billing/service.py",
                    fields=["plan_id", "price"],
                    line=8,
                )
            ],
        ),
    }

    requirements = [
        RequirementNode(
            id="REQ-AUTH-01",
            title="User Login Endpoint",
            source_doc="docs/auth.md",
            description="Expose /api/v1/auth/login accepting LoginRequest payload",
        ),
        RequirementNode(
            id="REQ-BILL-01",
            title="Manage Subscriptions",
            source_doc="specs/002-billing/spec.md",
            description="Handle SubscriptionPlan entities",
        ),
    ]

    tickets = [
        TicketNode(
            key="PROJ-200",
            summary="Audit /api/v1/auth/login security headers",
            source_file="tickets.csv",
        ),
        TicketNode(
            key="PROJ-201",
            summary="Refactor SubscriptionPlan database schema",
            components=["billing"],
            source_file="tickets.csv",
        ),
    ]

    correlator = TraceabilityCorrelator()
    links = correlator.correlate(files, requirements, tickets)

    assert len(links) >= 3

    # Check requirement links
    auth_req_links = [lnk for lnk in links if lnk.item_id == "REQ-AUTH-01"]
    assert any(lnk.code_file == "src/auth/routes.py" for lnk in auth_req_links)

    bill_req_links = [lnk for lnk in links if lnk.item_id == "REQ-BILL-01"]
    assert any(lnk.code_file == "src/billing/service.py" for lnk in bill_req_links)

    # Check ticket links
    ticket_auth_links = [lnk for lnk in links if lnk.item_id == "PROJ-200"]
    assert any(lnk.code_file == "src/auth/routes.py" for lnk in ticket_auth_links)
