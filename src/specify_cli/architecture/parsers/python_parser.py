"""Python AST parser extracting classes, functions, routes, models, and ML pipelines."""

from __future__ import annotations

import ast
from pathlib import Path
from .base import BaseLanguageParser
from ..models import ModelNode, RouteNode, SymbolNode, SymbolType


class PythonParser(BaseLanguageParser):
    language = "python"
    extensions = {".py", ".pyw"}

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

        try:
            tree = ast.parse(content, filename=str(path))
        except (SyntaxError, ValueError):
            return imports, symbols, routes, models

        lines = content.splitlines()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                for alias in node.names:
                    imports.append(f"{mod}.{alias.name}" if mod else alias.name)

        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                self._parse_class(node, relative_path, lines, symbols, models)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._parse_function(node, relative_path, lines, symbols, routes)

        return imports, symbols, routes, models

    def _parse_class(
        self,
        node: ast.ClassDef,
        relative_path: str,
        lines: list[str],
        symbols: list[SymbolNode],
        models: list[ModelNode],
    ) -> None:
        base_names: list[str] = []
        for b in node.bases:
            if isinstance(b, ast.Name):
                base_names.append(b.id)
            elif isinstance(b, ast.Attribute):
                base_names.append(b.attr)

        decorators = [self._decorator_name(d) for d in node.decorator_list]
        docstring = ast.get_docstring(node)
        is_model = any(
            b in {"BaseModel", "Model", "DeclarativeBase", "Schema"} for b in base_names
        ) or any(d in {"dataclass", "dataclass()"} for d in decorators)

        fields: list[str] = []
        for item in node.body:
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                fields.append(item.target.id)

        symbol_type = SymbolType.MODEL if is_model else SymbolType.CLASS

        symbol_id = f"{relative_path}::{node.name}"
        symbols.append(
            SymbolNode(
                id=symbol_id,
                name=node.name,
                symbol_type=symbol_type,
                file_path=relative_path,
                line_start=node.lineno,
                line_end=getattr(node, "end_lineno", node.lineno),
                docstring=docstring,
                decorators_or_annotations=decorators,
            )
        )

        if is_model:
            models.append(
                ModelNode(
                    name=node.name,
                    kind="pydantic" if "BaseModel" in base_names else "class_model",
                    file_path=relative_path,
                    fields=fields,
                    line=node.lineno,
                )
            )

        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method_id = f"{relative_path}::{node.name}.{item.name}"
                method_doc = ast.get_docstring(item)
                refs = self._extract_call_references(item)
                symbols.append(
                    SymbolNode(
                        id=method_id,
                        name=f"{node.name}.{item.name}",
                        symbol_type=SymbolType.METHOD,
                        file_path=relative_path,
                        line_start=item.lineno,
                        line_end=getattr(item, "end_lineno", item.lineno),
                        docstring=method_doc,
                        references=refs,
                    )
                )

    def _parse_function(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        relative_path: str,
        lines: list[str],
        symbols: list[SymbolNode],
        routes: list[RouteNode],
    ) -> None:
        decorators = [self._decorator_name(d) for d in node.decorator_list]
        docstring = ast.get_docstring(node)
        refs = self._extract_call_references(node)

        symbol_id = f"{relative_path}::{node.name}"
        symbols.append(
            SymbolNode(
                id=symbol_id,
                name=node.name,
                symbol_type=SymbolType.FUNCTION,
                file_path=relative_path,
                line_start=node.lineno,
                line_end=getattr(node, "end_lineno", node.lineno),
                docstring=docstring,
                decorators_or_annotations=decorators,
                references=refs,
            )
        )

        for d in node.decorator_list:
            route_info = self._extract_route(d)
            if route_info:
                method, path = route_info
                routes.append(
                    RouteNode(
                        method=method,
                        path=path,
                        handler_symbol=symbol_id,
                        file_path=relative_path,
                        line=node.lineno,
                    )
                )

    def _decorator_name(self, d: ast.expr) -> str:
        if isinstance(d, ast.Name):
            return d.id
        elif isinstance(d, ast.Attribute):
            return f"{self._decorator_name(d.value)}.{d.attr}"
        elif isinstance(d, ast.Call):
            return self._decorator_name(d.func)
        return ""

    def _extract_route(self, d: ast.expr) -> tuple[str, str] | None:
        if isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute):
            method = d.func.attr.upper()
            if method in {"GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD", "ROUTE"}:
                if d.args and isinstance(d.args[0], ast.Constant) and isinstance(d.args[0].value, str):
                    return method, d.args[0].value
        return None

    def _extract_call_references(self, node: ast.AST) -> list[str]:
        refs: set[str] = set()
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    refs.add(child.func.id)
                elif isinstance(child.func, ast.Attribute) and isinstance(child.func.value, ast.Name):
                    refs.add(f"{child.func.value.id}.{child.func.attr}")
        return sorted(refs)
