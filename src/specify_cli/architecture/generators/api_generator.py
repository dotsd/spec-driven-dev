"""Generates .specify/memory/architecture/api-surface.md."""

from __future__ import annotations

from ..models import FileNode, RouteNode


class ApiSurfaceGenerator:
    """Generates the API endpoints and system entrypoints documentation."""

    def generate(self, files: dict[str, FileNode]) -> str:
        all_routes: list[tuple[str, RouteNode]] = []
        for fpath, fnode in files.items():
            for r in fnode.routes:
                all_routes.append((fpath, r))

        # Sort routes by path and method
        all_routes.sort(key=lambda x: (x[1].path, x[1].method))

        lines = [
            "# API Surface & Entrypoints",
            "",
            "> [!NOTE]",
            "> Comprehensive catalog of exposed HTTP, RPC, CLI, and worker entrypoints in the system.",
            "",
            f"**Total Endpoints Discovered:** {len(all_routes)}",
            "",
            "| Method | Path / Endpoint | Handler Symbol | File | Line |",
            "| :--- | :--- | :--- | :--- | :--- |",
        ]

        if not all_routes:
            lines.append("| *None* | *No endpoints detected* | - | - | - |")
        else:
            for fpath, r in all_routes:
                handler = f"`{r.handler_symbol}`" if r.handler_symbol else "-"
                path_str = f"`{r.path}`"
                lines.append(f"| **{r.method}** | {path_str} | {handler} | `{fpath}` | {r.line} |")

        lines.append("")
        return "\n".join(lines)
