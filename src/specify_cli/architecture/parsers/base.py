"""Abstract base class for language parsers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from ..models import ModelNode, RouteNode, SymbolNode


class BaseLanguageParser(ABC):
    """Base parser interface for extracting AST and architectural symbols."""

    language: str
    extensions: set[str] = set()

    def can_parse(self, path: Path) -> bool:
        """Check if parser handles this file extension."""
        return path.suffix.lower() in self.extensions

    @abstractmethod
    def parse(
        self,
        path: Path,
        relative_path: str,
        content: str,
    ) -> tuple[list[str], list[SymbolNode], list[RouteNode], list[ModelNode]]:
        """Parse source code content and extract architectural nodes.

        Returns:
            Tuple of (imports, symbols, routes, models)
        """
        raise NotImplementedError
