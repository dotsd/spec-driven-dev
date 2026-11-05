"""Rust language parser extracting crates, use declarations, structs, enums, traits, functions, and routes."""

from __future__ import annotations

import re
from pathlib import Path
from .base import BaseLanguageParser
from ..models import ModelNode, RouteNode, SymbolNode, SymbolType


class RustParser(BaseLanguageParser):
    language = "rust"
    extensions = {".rs"}

    USE_RE = re.compile(r"""use\s+([A-Za-z0-9_:]+)(?:::\{([\s\S]*?)\})?;""")
    STRUCT_RE = re.compile(r"""(?:pub(?:\([a-z_]+\))?\s+)?struct\s+([A-Za-z0-9_]+)\s*(?:<[^>]+>)?\s*\{([\s\S]*?)\}""")
    ENUM_RE = re.compile(r"""(?:pub(?:\([a-z_]+\))?\s+)?enum\s+([A-Za-z0-9_]+)""")
    TRAIT_RE = re.compile(r"""(?:pub(?:\([a-z_]+\))?\s+)?trait\s+([A-Za-z0-9_]+)""")
    FN_RE = re.compile(r"""(?:pub(?:\([a-z_]+\))?\s+)?(?:async\s+)?fn\s+([A-Za-z0-9_]+)\s*(?:<[^>]+>)?\s*\(([^)]*)\)""")
    ACTIX_ROUTE_RE = re.compile(r"""#\[(get|post|put|delete|patch)\s*\(\s*['"]([^'"]+)['"]\s*\)\]""")
    AXUM_ROUTE_RE = re.compile(r"""\.route\s*\(\s*['"]([^'"]+)['"]\s*,\s*(get|post|put|delete)\s*\(\s*([A-Za-z0-9_:]+)\s*\)""")

    def parse(
        self,
        path: Path,
        relative_path: str,
        content: str,
    ) -> tuple[list[str], list[SymbolNode], list[RouteNode], list[ModelNode]]:
        imports: list[str] = []
        symbols: list[SymbolNode] = []
        routes: list[RouteNode] = []
        models: list[ModelNode] = []

        for m in self.USE_RE.finditer(content):
            base = m.group(1)
            group = m.group(2)
            if group:
                for item in group.split(","):
                    item = item.strip()
                    if item:
                        imports.append(f"{base}::{item}")
            else:
                imports.append(base)

        for m in self.STRUCT_RE.finditer(content):
            name = m.group(1)
            body = m.group(2)
            fields: list[str] = []
            for f_line in body.splitlines():
                f_line = f_line.strip()
                if f_line and not f_line.startswith("//") and ":" in f_line:
                    f_name = f_line.split(":")[0].replace("pub", "").strip()
                    if f_name:
                        fields.append(f_name)

            line_no = content[:m.start()].count("\n") + 1
            symbols.append(
                SymbolNode(
                    id=f"{relative_path}::{name}",
                    name=name,
                    symbol_type=SymbolType.STRUCT,
                    file_path=relative_path,
                    line_start=line_no,
                    line_end=line_no,
                )
            )
            models.append(
                ModelNode(
                    name=name,
                    kind="rust_struct",
                    file_path=relative_path,
                    fields=fields,
                    line=line_no,
                )
            )

        for m in self.ENUM_RE.finditer(content):
            name = m.group(1)
            line_no = content[:m.start()].count("\n") + 1
            symbols.append(
                SymbolNode(
                    id=f"{relative_path}::{name}",
                    name=name,
                    symbol_type=SymbolType.ENUM,
                    file_path=relative_path,
                    line_start=line_no,
                    line_end=line_no,
                )
            )

        for m in self.TRAIT_RE.finditer(content):
            name = m.group(1)
            line_no = content[:m.start()].count("\n") + 1
            symbols.append(
                SymbolNode(
                    id=f"{relative_path}::{name}",
                    name=name,
                    symbol_type=SymbolType.INTERFACE,
                    file_path=relative_path,
                    line_start=line_no,
                    line_end=line_no,
                )
            )

        for m in self.FN_RE.finditer(content):
            name = m.group(1)
            params = m.group(2)
            line_no = content[:m.start()].count("\n") + 1
            symbols.append(
                SymbolNode(
                    id=f"{relative_path}::{name}",
                    name=name,
                    symbol_type=SymbolType.FUNCTION,
                    file_path=relative_path,
                    line_start=line_no,
                    line_end=line_no,
                    signature=f"({params})",
                )
            )

        for m in self.ACTIX_ROUTE_RE.finditer(content):
            method = m.group(1).upper()
            route_path = m.group(2)
            line_no = content[:m.start()].count("\n") + 1
            routes.append(
                RouteNode(
                    method=method,
                    path=route_path,
                    file_path=relative_path,
                    line=line_no,
                )
            )

        for m in self.AXUM_ROUTE_RE.finditer(content):
            route_path = m.group(1)
            method = m.group(2).upper()
            handler = m.group(3)
            line_no = content[:m.start()].count("\n") + 1
            routes.append(
                RouteNode(
                    method=method,
                    path=route_path,
                    handler_symbol=f"{relative_path}::{handler}",
                    file_path=relative_path,
                    line=line_no,
                )
            )

        return imports, symbols, routes, models
