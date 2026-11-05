"""Generates .specify/memory/architecture/traceability.md."""

from __future__ import annotations

from typing import Sequence
from ..models import RequirementNode, TicketNode, TraceabilityLink


class TraceabilityGenerator:
    """Generates the functional and ticket traceability matrix linking specs to technical code."""

    def generate(
        self,
        requirements: Sequence[RequirementNode],
        tickets: Sequence[TicketNode],
        links: Sequence[TraceabilityLink],
    ) -> str:
        # Group links by item_id
        links_by_item: dict[str, list[TraceabilityLink]] = {}
        for link in links:
            links_by_item.setdefault(link.item_id, []).append(link)

        lines = [
            "# Functional & Work Traceability Matrix",
            "",
            "> [!NOTE]",
            "> Bridges functional requirements (PRDs, Spec Kit specifications) and work items (JIRA tickets) with technical code.",
            "",
            "## 1. JIRA / Issue Tracker Traceability",
            "| Ticket Key | Summary | Status | Subsystem | Implementing Code / Routes | Match Reason |",
            "| :--- | :--- | :--- | :--- | :--- | :--- |",
        ]

        if not tickets:
            lines.append("| *None* | *No JIRA/ticket sheets loaded* | - | - | - | - |")
        else:
            for t in tickets:
                t_links = links_by_item.get(t.key, [])
                if t_links:
                    code_targets = ", ".join(
                        f"`{lnk.symbol_or_route or lnk.code_file}`" for lnk in t_links[:3]
                    )
                    reasons = ", ".join(sorted({lnk.match_reason for lnk in t_links}))
                else:
                    code_targets = "*Pending implementation*"
                    reasons = "Unlinked"

                subsystem = t.target_subsystem or "-"
                lines.append(
                    f"| **`{t.key}`** | {t.summary} | `{t.status}` | {subsystem} | {code_targets} | {reasons} |"
                )

        lines.extend([
            "",
            "## 2. Functional Requirements & PRD Specs",
            "| Requirement ID | Title / Feature | Source Document | Implementing Code / Endpoints / Models | Traceability Status |",
            "| :--- | :--- | :--- | :--- | :--- |",
        ])

        if not requirements:
            lines.append("| *None* | *No spec or functional documents detected* | - | - | - |")
        else:
            for req in requirements:
                r_links = links_by_item.get(req.id, [])
                if r_links:
                    code_targets = ", ".join(
                        f"`{lnk.symbol_or_route or lnk.code_file}`" for lnk in r_links[:4]
                    )
                    status_badge = "✅ Linked"
                else:
                    code_targets = "*No direct code mapped*"
                    status_badge = "⚠️ Unimplemented / Untagged"

                lines.append(
                    f"| **`{req.id}`** | {req.title} | `{req.source_doc}` | {code_targets} | {status_badge} |"
                )

        lines.extend([
            "",
            "## 3. Requirement Details & Acceptance Criteria",
            "",
        ])

        if not requirements:
            lines.append("*No requirements details available.*")
        else:
            for req in requirements:
                lines.append(f"### `{req.id}`: {req.title}")
                lines.append(f"- **Source Document:** `{req.source_doc}` ({req.section or 'General'})")
                if req.description:
                    lines.append(f"- **Description:** {req.description}")
                if req.acceptance_criteria:
                    lines.append("- **Acceptance Criteria:**")
                    for ac in req.acceptance_criteria:
                        lines.append(f"  - [ ] {ac}")

                r_links = links_by_item.get(req.id, [])
                if r_links:
                    lines.append("- **Implementing Code Artifacts:**")
                    for lnk in r_links:
                        sym_info = f" ({lnk.symbol_or_route})" if lnk.symbol_or_route else ""
                        lines.append(f"  - `{lnk.code_file}`{sym_info} — *matched via {lnk.match_reason}*")
                lines.append("")

        return "\n".join(lines)
