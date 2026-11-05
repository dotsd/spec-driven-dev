"""TypeScript, JavaScript, JSX, TSX, Vue, and Svelte parser."""

from __future__ import annotations

import re
from pathlib import Path
from .base import BaseLanguageParser
from ..models import ModelNode, RouteNode, SymbolNode, SymbolType


class WebParser(BaseLanguageParser):
    language = "typescript_javascript"
    extensions = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".vue", ".svelte"}

    IMPORT_RE = re.compile(
        r"""(?:(?:import|export)\s+(?:(?!import|export)[^;])*?\s+from\s+['"]([^'"]+)['"]"""
        r"""|import\s*\(\s*['"]([^'"]+)['"]\s*\)"""
        r"""|import\s+['"]([^'"]+)['"]"""
        r"""|require\s*\(\s*['"]([^'"]+)['"]\s*\))""",
        re.DOTALL,
    )
    CLASS_RE = re.compile(r"""(?:export\s+)?(?:default\s+)?class\s+([A-Za-z0-9_$]+)(?:\s+extends\s+([A-Za-z0-9_$]+))?(?:\s+implements\s+([A-Za-z0-9_$,\s]+))?""")
    INTERFACE_RE = re.compile(r"""(?:export\s+)?interface\s+([A-Za-z0-9_$]+)""")
    TYPE_RE = re.compile(r"""(?:export\s+)?type\s+([A-Za-z0-9_$]+)\s*=""")
    FUNCTION_RE = re.compile(r"""(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s+([A-Za-z0-9_$]+)\s*\(([^)]*)\)""")
    CONST_FN_RE = re.compile(r"""(?:export\s+)?const\s+([A-Za-z0-9_$]+)\s*=\s*(?:async\s*)?\(([^)]*)\)\s*(?::\s*[^=>]+)?\s*=>""")
    EXPRESS_ROUTE_RE = re.compile(r"""(?:app|router)\.(get|post|put|delete|patch|options)\s*\(\s*['"]([^'"]+)['"]""")
    ZOD_SCHEMA_RE = re.compile(r"""(?:export\s+)?const\s+([A-Za-z0-9_$]+)\s*=\s*z\.object\s*\(""")

    @staticmethod
    def _extract_braced_body(content: str, brace_start: int) -> tuple[str, int] | None:
        if brace_start < 0 or brace_start >= len(content) or content[brace_start] != "{":
            return None
        depth = 0
        in_string: str | None = None
        i = brace_start
        n = len(content)
        while i < n:
            char = content[i]
            if in_string:
                if char == "\\" and i + 1 < n:
                    i += 2
                    continue
                if char == in_string:
                    in_string = None
            else:
                if char in ('"', "'", "`"):
                    in_string = char
                elif char == "/" and i + 1 < n:
                    if content[i + 1] == "/":
                        eol = content.find("\n", i)
                        i = eol if eol != -1 else n
                        continue
                    elif content[i + 1] == "*":
                        end_comment = content.find("*/", i + 2)
                        i = end_comment + 2 if end_comment != -1 else n
                        continue
                elif char == "{":
                    depth += 1
                elif char == "}":
                    depth -= 1
                    if depth == 0:
                        return content[brace_start + 1 : i], i + 1
            i += 1
        return None

    @staticmethod
    def _extract_object_fields(body: str) -> list[str]:
        fields: list[str] = []
        prop_re = re.compile(
            r"""^(?:readonly\s+|public\s+|private\s+|protected\s+)?([A-Za-z0-9_$]+)\s*\??\s*:"""
        )
        for line in body.splitlines():
            line = line.strip()
            if not line or line.startswith("//") or line.startswith("/*") or line.startswith("*"):
                continue
            m = prop_re.match(line)
            if m:
                fname = m.group(1)
                if fname not in fields:
                    fields.append(fname)
            elif ";" in line or ("," in line and not line.startswith("{")):
                for sub in re.split(r"[;,]", line):
                    sub = sub.strip()
                    sm = prop_re.match(sub)
                    if sm:
                        fname = sm.group(1)
                        if fname not in fields:
                            fields.append(fname)
        return fields

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

        for match in self.IMPORT_RE.finditer(content):
            target = match.group(1) or match.group(2) or match.group(3) or match.group(4)
            if target and target not in imports:
                imports.append(target)

        for match in self.CLASS_RE.finditer(content):
            name = match.group(1)
            line_no = content[:match.start()].count("\n") + 1
            symbols.append(
                SymbolNode(
                    id=f"{relative_path}::{name}",
                    name=name,
                    symbol_type=SymbolType.CLASS,
                    file_path=relative_path,
                    line_start=line_no,
                    line_end=line_no,
                )
            )

        for match in self.INTERFACE_RE.finditer(content):
            name = match.group(1)
            line_no = content[:match.start()].count("\n") + 1
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
            brace_pos = content.find("{", match.end())
            if brace_pos != -1:
                body_info = self._extract_braced_body(content, brace_pos)
                if body_info:
                    body_text, _ = body_info
                    fields = self._extract_object_fields(body_text)
                    models.append(
                        ModelNode(
                            name=name,
                            kind="ts_interface",
                            file_path=relative_path,
                            fields=fields,
                            line=line_no,
                        )
                    )

        for match in self.TYPE_RE.finditer(content):
            name = match.group(1)
            line_no = content[:match.start()].count("\n") + 1
            symbols.append(
                SymbolNode(
                    id=f"{relative_path}::{name}",
                    name=name,
                    symbol_type=SymbolType.TYPE,
                    file_path=relative_path,
                    line_start=line_no,
                    line_end=line_no,
                )
            )
            brace_pos = content.find("{", match.end())
            if brace_pos != -1:
                between = content[match.end():brace_pos].strip()
                if not any(stop in between for stop in (";", "class ", "interface ", "function ", "type ")):
                    body_info = self._extract_braced_body(content, brace_pos)
                    if body_info:
                        body_text, _ = body_info
                        fields = self._extract_object_fields(body_text)
                        models.append(
                            ModelNode(
                                name=name,
                                kind="ts_type",
                                file_path=relative_path,
                                fields=fields,
                                line=line_no,
                            )
                        )

        for match in self.FUNCTION_RE.finditer(content):
            name = match.group(1)
            params = match.group(2)
            line_no = content[:match.start()].count("\n") + 1
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

        for match in self.CONST_FN_RE.finditer(content):
            name = match.group(1)
            params = match.group(2)
            line_no = content[:match.start()].count("\n") + 1
            symbols.append(
                SymbolNode(
                    id=f"{relative_path}::{name}",
                    name=name,
                    symbol_type=SymbolType.FUNCTION,
                    file_path=relative_path,
                    line_start=line_no,
                    line_end=line_no,
                    signature=f"({params}) => ...",
                )
            )

        for match in self.EXPRESS_ROUTE_RE.finditer(content):
            method = match.group(1).upper()
            route_path = match.group(2)
            line_no = content[:match.start()].count("\n") + 1
            routes.append(
                RouteNode(
                    method=method,
                    path=route_path,
                    file_path=relative_path,
                    line=line_no,
                )
            )

        if path.stem in {"route", "api"}:
            for method in ("GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"):
                if re.search(rf"""export\s+(?:async\s+)?function\s+{method}\b""", content):
                    routes.append(
                        RouteNode(
                            method=method,
                            path=f"/{relative_path.replace('/route.ts', '').replace('/route.js', '')}",
                            file_path=relative_path,
                            line=1,
                        )
                    )

        for match in self.ZOD_SCHEMA_RE.finditer(content):
            name = match.group(1)
            line_no = content[:match.start()].count("\n") + 1
            brace_pos = content.find("{", match.end())
            if brace_pos != -1:
                body_info = self._extract_braced_body(content, brace_pos)
                if body_info:
                    body_text, _ = body_info
                    fields = self._extract_object_fields(body_text)
                    models.append(
                        ModelNode(
                            name=name,
                            kind="zod_schema",
                            file_path=relative_path,
                            fields=fields,
                            line=line_no,
                        )
                    )

        return imports, symbols, routes, models
