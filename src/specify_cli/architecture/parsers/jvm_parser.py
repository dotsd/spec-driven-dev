"""JVM languages parser (Java, Kotlin, Scala) extracting classes, data classes, interfaces, methods, and Spring routes."""

from __future__ import annotations

import re
from pathlib import Path
from .base import BaseLanguageParser
from ..models import ModelNode, RouteNode, SymbolNode, SymbolType


class JVMParser(BaseLanguageParser):
    language = "jvm"
    extensions = {".java", ".kt", ".kts", ".scala"}

    IMPORT_RE = re.compile(r"""import\s+([A-Za-z0-9_.*]+);?""")
    CLASS_RE = re.compile(r"""(?:public|protected|private)?\s*(?:final|abstract|open)?\s*(?:data\s+)?class\s+([A-Za-z0-9_]+)""")
    INTERFACE_RE = re.compile(r"""(?:public|protected|private)?\s*interface\s+([A-Za-z0-9_]+)""")
    SPRING_ROUTE_RE = re.compile(r"""@(Get|Post|Put|Delete|Patch|Request)Mapping\s*\(\s*(?:value\s*=\s*)?['"]([^'"]+)['"]""")
    METHOD_JAVA_RE = re.compile(r"""(?:public|protected|private)\s+(?:static\s+)?[A-Za-z0-9_<>,\[\]]+\s+([A-Za-z0-9_]+)\s*\(([^)]*)\)""")
    FUN_KT_RE = re.compile(r"""(?:fun|def)\s+([A-Za-z0-9_]+)\s*\(([^)]*)\)""")

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

        for m in self.IMPORT_RE.finditer(content):
            imports.append(m.group(1))

        for m in self.CLASS_RE.finditer(content):
            name = m.group(1)
            line_no = content[:m.start()].count("\n") + 1
            is_entity = "@Entity" in content[:m.start()] or "data class" in m.group(0)
            sym_type = SymbolType.MODEL if is_entity else SymbolType.CLASS

            symbols.append(
                SymbolNode(
                    id=f"{relative_path}::{name}",
                    name=name,
                    symbol_type=sym_type,
                    file_path=relative_path,
                    line_start=line_no,
                    line_end=line_no,
                )
            )

            if is_entity:
                models.append(
                    ModelNode(
                        name=name,
                        kind="jpa_entity" if "@Entity" in content else "kotlin_data_class",
                        file_path=relative_path,
                        fields=[],
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

        for m in self.METHOD_JAVA_RE.finditer(content):
            name = m.group(1)
            params = m.group(2)
            line_no = content[:m.start()].count("\n") + 1
            symbols.append(
                SymbolNode(
                    id=f"{relative_path}::{name}",
                    name=name,
                    symbol_type=SymbolType.METHOD,
                    file_path=relative_path,
                    line_start=line_no,
                    line_end=line_no,
                    signature=f"({params})",
                )
            )

        for m in self.FUN_KT_RE.finditer(content):
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

        for m in self.SPRING_ROUTE_RE.finditer(content):
            raw_method = m.group(1).upper()
            method = "ANY" if raw_method == "REQUEST" else raw_method
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

        return imports, symbols, routes, models
