"""Generates .specify/memory/architecture/domain-models.md."""

from __future__ import annotations

from ..models import FileNode, ModelNode


class DomainModelsGenerator:
    """Generates the domain models, DB schemas, and typed data structures documentation."""

    def generate(self, files: dict[str, FileNode]) -> str:
        all_models: list[tuple[str, ModelNode]] = []
        for fpath, fnode in files.items():
            for m in fnode.models:
                all_models.append((fpath, m))

        all_models.sort(key=lambda x: (x[1].kind, x[1].name))

        lines = [
            "# Domain Models & Data Schemas",
            "",
            "> [!NOTE]",
            "> Comprehensive catalog of domain entities, database tables, Pydantic models, Zod schemas, and data structures.",
            "",
            f"**Total Domain Models Discovered:** {len(all_models)}",
            "",
            "## 1. Summary Catalog",
            "| Model / Entity | Schema Kind | File Path | Line | Key Fields / Properties |",
            "| :--- | :--- | :--- | :--- | :--- |",
        ]

        if not all_models:
            lines.append("| *None* | *No domain models detected* | - | - | - |")
        else:
            for fpath, m in all_models:
                fields_str = ", ".join(f"`{f}`" for f in m.fields[:6])
                if len(m.fields) > 6:
                    fields_str += f" *(+{len(m.fields) - 6} more)*"
                if not fields_str:
                    fields_str = "-"
                lines.append(f"| **`{m.name}`** | {m.kind} | `{fpath}` | {m.line} | {fields_str} |")

        lines.extend([
            "",
            "## 2. Detailed Schemas",
            "",
        ])

        if not all_models:
            lines.append("*No schemas available.*")
        else:
            for fpath, m in all_models:
                lines.append(f"### `{m.name}` ({m.kind})")
                lines.append(f"- **Defined In:** `{fpath}:{m.line}`")
                if m.fields:
                    lines.append(f"- **Fields ({len(m.fields)}):**")
                    for field in m.fields:
                        lines.append(f"  - `{field}`")
                else:
                    lines.append("- **Fields:** *(dynamic or not declared inline)*")
                lines.append("")

        return "\n".join(lines)
