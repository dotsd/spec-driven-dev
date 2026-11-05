"""Go language parser extracting packages, imports, structs, interfaces, functions, and routes."""

from __future__ import annotations

import re
from pathlib import Path
from .base import BaseLanguageParser
from ..models import ModelNode, RouteNode, SymbolNode, SymbolType


class GoParser(BaseLanguageParser):
    language = "go"
    extensions = {".go"}

    IMPORT_SINGLE_RE = re.compile(r"""import\s+['"]([^'"]+)['"]""")
    IMPORT_BLOCK_RE = re.compile(r"""import\s*\(([\s\S]*?)\)""")
    STRUCT_RE = re.compile(r"""type\s+([A-Za-z0-9_]+)\s+struct\s*\{([\s\S]*?)\}""")
    INTERFACE_RE = re.compile(r"""type\s+([A-Za-z0-9_]+)\s+interface\s*\{""")
    FUNC_RE = re.compile(r"""func\s+(?:\((?:[A-Za-z0-9_*]+)?\s*\*?([A-Za-z0-9_]+)\)\s+)?([A-Za-z0-9_]+)\s*\(([^)]*)\)""")
    GIN_ROUTE_RE = re.compile(r"""(?:r|router|group|v1|api)\.(GET|POST|PUT|DELETE|PATCH)\s*\(\s*['"]([^'"]+)['"]\s*,\s*([A-Za-z0-9_.]+)""")
    HTTP_ROUTE_RE = re.compile(r"""http\.HandleFunc\s*\(\s*['"]([^'"]+)['"]""")

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

        for m in self.IMPORT_SINGLE_RE.finditer(content):
            imports.append(m.group(1))

        for m in self.IMPORT_BLOCK_RE.finditer(content):
            block = m.group(1)
            for line in block.splitlines():
                line = line.strip()
                if line and not line.startswith("//"):
                    pkg_match = re.search(r"""['"]([^'"]+)['"]""", line)
                    if pkg_match:
                        imports.append(pkg_match.group(1))

        for m in self.STRUCT_RE.finditer(content):
            name = m.group(1)
            body = m.group(2)
            fields: list[str] = []
            for f_line in body.splitlines():
                f_line = f_line.strip()
                if f_line and not f_line.startswith("//"):
                    parts = f_line.split()
                    if parts:
                        fields.append(parts[0])

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
                    kind="go_struct",
                    file_path=relative_path,
                    fields=fields,
                    line=line_no,
                )
            )

        for m in self.INTERFACE_RE.finditer(content):
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

        for m in self.FUNC_RE.finditer(content):
            receiver = m.group(1)
            fn_name = m.group(2)
            params = m.group(3)
            full_name = f"{receiver}.{fn_name}" if receiver else fn_name
            sym_type = SymbolType.METHOD if receiver else SymbolType.FUNCTION
            line_no = content[:m.start()].count("\n") + 1

            symbols.append(
                SymbolNode(
                    id=f"{relative_path}::{full_name}",
                    name=full_name,
                    symbol_type=sym_type,
                    file_path=relative_path,
                    line_start=line_no,
                    line_end=line_no,
                    signature=f"({params})",
                )
            )

        for m in self.GIN_ROUTE_RE.finditer(content):
            method = m.group(1).upper()
            route_path = m.group(2)
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

        for m in self.HTTP_ROUTE_RE.finditer(content):
            route_path = m.group(1)
            line_no = content[:m.start()].count("\n") + 1
            routes.append(
                RouteNode(
                    method="ANY",
                    path=route_path,
                    file_path=relative_path,
                    line=line_no,
                )
            )

        return imports, symbols, routes, models
