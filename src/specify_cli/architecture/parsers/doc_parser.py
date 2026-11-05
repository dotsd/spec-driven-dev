"""Functional Document, Spec Kit Spec, and Ticket Sheet Parser."""

from __future__ import annotations

import csv
import io
import json
import re
from pathlib import Path
from ..models import RequirementNode, TicketNode


class DocumentParser:
    """Extracts functional requirements, user stories, and work item tickets."""

    # Regex patterns for requirements in markdown
    REQ_ID_RE = re.compile(r"""\b(FR-\d+|REQ-[A-Z0-9_-]+|US-\d+|BR-\d+|AC-\d+)\b""", re.IGNORECASE)
    USER_STORY_HEADER_RE = re.compile(
        r"""^#{2,4}\s+(?:User\s+Story\s+(\d+)[:\s-]+|US-(\d+)[:\s-]+)(.*)$""",
        re.MULTILINE | re.IGNORECASE,
    )
    REQ_LIST_ITEM_RE = re.compile(
        r"""^[-*]\s+(?:\*\*([A-Za-z0-9_-]+):\*\*\s*|\(([A-Za-z0-9_-]+)\)\s*|([A-Z]+-\d+)[:\s-]+)?(.*)$""",
        re.MULTILINE,
    )
    JIRA_KEY_RE = re.compile(r"""\b([A-Z]{2,10}-\d+)\b""")

    def parse_markdown_doc(self, path: Path, relative_path: str, content: str) -> list[RequirementNode]:
        """Parse a markdown specification or functional PRD document."""
        requirements: list[RequirementNode] = []
        lines = content.splitlines()

        doc_title = path.stem.replace("-", " ").replace("_", " ").title()
        for line in lines[:10]:
            if line.startswith("# "):
                doc_title = line.lstrip("# ").strip()
                break

        current_section = "Overview"
        current_req_id: str | None = None
        current_req_title: str | None = None
        current_desc_lines: list[str] = []
        current_criteria: list[str] = []

        req_counter = 1

        def _flush_current() -> None:
            nonlocal current_req_id, current_req_title, current_desc_lines, current_criteria, req_counter
            if current_req_title:
                rid = current_req_id or f"REQ-{req_counter:03d}"
                req_counter += 1
                desc = "\n".join(current_desc_lines).strip() or None
                requirements.append(
                    RequirementNode(
                        id=rid,
                        title=current_req_title,
                        source_doc=relative_path,
                        section=current_section,
                        description=desc,
                        acceptance_criteria=list(current_criteria),
                        tags=[doc_title],
                    )
                )
            current_req_id = None
            current_req_title = None
            current_desc_lines = []
            current_criteria = []

        for line in lines:
            line_str = line.strip()

            # Heading 2 or 3
            if line_str.startswith("## ") or line_str.startswith("### "):
                _flush_current()
                current_section = line_str.lstrip("#").strip()

                # Check if heading is a User Story
                us_match = self.USER_STORY_HEADER_RE.match(line)
                if us_match:
                    num = us_match.group(1) or us_match.group(2)
                    title = us_match.group(3).strip()
                    current_req_id = f"US-{int(num):03d}" if num else f"US-{req_counter:03d}"
                    current_req_title = title or f"User Story {num}"
                continue

            # Check for requirement bullet item
            if line_str.startswith("- ") or line_str.startswith("* "):
                # Look for explicit ID like FR-001 or REQ-001
                id_match = self.REQ_ID_RE.search(line_str)
                if id_match:
                    _flush_current()
                    found_id = id_match.group(1).upper()
                    # Strip bullet and id from line for title
                    cleaned_title = line_str.lstrip("-* ").replace(found_id, "").strip(" :*-")
                    current_req_id = found_id
                    current_req_title = cleaned_title or found_id
                    continue

                # Check if this is an acceptance criteria / scenario line
                if "scenario:" in line_str.lower() or "given " in line_str.lower() or "[ ]" in line_str or "[x]" in line_str:
                    current_criteria.append(line_str.lstrip("-* ").strip())
                    continue

            # Otherwise accumulate description text if we have an active requirement
            if current_req_title and line_str:
                current_desc_lines.append(line_str)

        _flush_current()

        # If document had no structured bullets/US headers, create document-level requirement
        if not requirements:
            requirements.append(
                RequirementNode(
                    id=f"DOC-{path.stem.upper()}",
                    title=doc_title,
                    source_doc=relative_path,
                    section="Document Summary",
                    description=lines[0] if lines else None,
                    acceptance_criteria=[],
                    tags=[doc_title],
                )
            )

        return requirements

    def parse_ticket_file(self, path: Path, relative_path: str, content: str) -> list[TicketNode]:
        """Parse JIRA / issue tracking sheets from CSV, JSON, or Markdown."""
        ext = path.suffix.lower()
        if ext == ".csv":
            return self._parse_csv_tickets(relative_path, content)
        elif ext == ".json":
            return self._parse_json_tickets(relative_path, content)
        else:
            return self._parse_markdown_tickets(relative_path, content)

    def _parse_csv_tickets(self, relative_path: str, content: str) -> list[TicketNode]:
        tickets: list[TicketNode] = []
        try:
            reader = csv.DictReader(io.StringIO(content))
            for row in reader:
                # Find key column
                key = ""
                for k in ("Issue key", "Key", "Issue Key", "ID", "Ticket", "key", "id"):
                    if k in row and row[k]:
                        key = row[k].strip()
                        break
                if not key:
                    # Search all cells for Jira key pattern
                    for val in row.values():
                        m = self.JIRA_KEY_RE.search(str(val))
                        if m:
                            key = m.group(1)
                            break

                if not key:
                    continue

                summary = ""
                for s in ("Summary", "Title", "summary", "title", "Subject"):
                    if s in row and row[s]:
                        summary = row[s].strip()
                        break
                if not summary:
                    summary = f"Ticket {key}"

                status = ""
                for st in ("Status", "status", "State", "state"):
                    if st in row and row[st]:
                        status = row[st].strip()
                        break
                status = status or "Open"

                desc = ""
                for d in ("Description", "description", "Details", "details"):
                    if d in row and row[d]:
                        desc = row[d].strip()
                        break

                components: list[str] = []
                for c in ("Component/s", "Components", "Component", "components"):
                    if c in row and row[c]:
                        components = [x.strip() for x in row[c].split(",") if x.strip()]
                        break

                assignee = row.get("Assignee") or row.get("assignee")

                tickets.append(
                    TicketNode(
                        key=key,
                        summary=summary,
                        status=status,
                        source_file=relative_path,
                        description=desc or None,
                        target_subsystem=components[0] if components else None,
                        assignee=assignee,
                        components=components,
                    )
                )
        except Exception:
            pass
        return tickets

    def _parse_json_tickets(self, relative_path: str, content: str) -> list[TicketNode]:
        tickets: list[TicketNode] = []
        try:
            data = json.loads(content)
            items = data.get("issues", data) if isinstance(data, dict) else data
            if not isinstance(items, list):
                return tickets

            for item in items:
                if not isinstance(item, dict):
                    continue
                fields = item.get("fields", item)
                key = item.get("key") or fields.get("key") or fields.get("id") or ""
                summary = fields.get("summary") or fields.get("title") or ""
                status_raw = fields.get("status")
                status = status_raw.get("name") if isinstance(status_raw, dict) else str(status_raw or "Open")
                desc = fields.get("description")
                if isinstance(desc, dict):
                    desc = json.dumps(desc)

                components_raw = fields.get("components", [])
                components = [c.get("name", "") if isinstance(c, dict) else str(c) for c in components_raw]

                if key:
                    tickets.append(
                        TicketNode(
                            key=str(key),
                            summary=str(summary or key),
                            status=status,
                            source_file=relative_path,
                            description=str(desc) if desc else None,
                            target_subsystem=components[0] if components else None,
                            components=[c for c in components if c],
                        )
                    )
        except Exception:
            pass
        return tickets

    def _parse_markdown_tickets(self, relative_path: str, content: str) -> list[TicketNode]:
        tickets: list[TicketNode] = []
        for line in content.splitlines():
            line_str = line.strip()
            match = self.JIRA_KEY_RE.search(line_str)
            if match:
                key = match.group(1)
                summary = line_str.replace(key, "").strip(" -*|[]:`")
                status = "Done" if "[x]" in line_str.lower() else "Open"
                tickets.append(
                    TicketNode(
                        key=key,
                        summary=summary or f"Issue {key}",
                        status=status,
                        source_file=relative_path,
                    )
                )
        return tickets
