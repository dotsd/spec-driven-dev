"""Parser registry for AST code and functional documents."""

from __future__ import annotations

from .base import BaseLanguageParser
from .python_parser import PythonParser
from .web_parser import WebParser
from .go_parser import GoParser
from .rust_parser import RustParser
from .jvm_parser import JVMParser
from .data_ml_parser import DataMLParser
from .doc_parser import DocumentParser

ALL_PARSERS: list[BaseLanguageParser] = [
    PythonParser(),
    WebParser(),
    GoParser(),
    RustParser(),
    JVMParser(),
    DataMLParser(),
]

__all__ = [
    "BaseLanguageParser",
    "PythonParser",
    "WebParser",
    "GoParser",
    "RustParser",
    "JVMParser",
    "DataMLParser",
    "DocumentParser",
    "ALL_PARSERS",
]
