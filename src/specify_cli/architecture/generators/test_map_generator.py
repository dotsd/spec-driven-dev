"""Generates .specify/memory/architecture/test-map.md."""

from __future__ import annotations

import re
from ..models import FileNode


class TestMapGenerator:
    """Generates mapping between source components and their test suites."""

    def generate(self, files: dict[str, FileNode]) -> str:
        test_files: list[str] = []
        source_files: list[str] = []

        for fpath in files.keys():
            if self._is_test_file(fpath):
                test_files.append(fpath)
            else:
                source_files.append(fpath)

        # Map source files to test files
        mapping: dict[str, list[str]] = {}
        for tf in test_files:
            stem = self._clean_test_stem(tf)
            for sf in source_files:
                if stem and stem in sf.lower():
                    mapping.setdefault(sf, []).append(tf)

        lines = [
            "# Test Suite Mapping & Verification Coverage",
            "",
            "> [!NOTE]",
            "> Documents test suite structure and maps source modules to their corresponding test files.",
            "",
            f"- **Total Test Files Detected:** {len(test_files)}",
            f"- **Total Source Modules:** {len(source_files)}",
            f"- **Source Modules with Direct Test Coverage:** {len(mapping)}",
            "",
            "## 1. Source to Test Suite Mapping",
            "| Source Module | Associated Test File(s) | Coverage Status |",
            "| :--- | :--- | :--- |",
        ]

        if not source_files:
            lines.append("| *None* | - | - |")
        else:
            for sf in sorted(source_files)[:50]:
                tests = mapping.get(sf, [])
                if tests:
                    tests_str = ", ".join(f"`{t}`" for t in tests[:2])
                    status = "✅ Covered"
                else:
                    tests_str = "*No direct test file match*"
                    status = "⚠️ Untested"
                lines.append(f"| `{sf}` | {tests_str} | {status} |")

        lines.extend([
            "",
            "## 2. Test Files Catalog",
            "",
        ])

        if not test_files:
            lines.append("*No test files detected in repository.*")
        else:
            for tf in sorted(test_files):
                fnode = files.get(tf)
                lines.append(f"- `{tf}` ({fnode.language if fnode else 'test'})")

        lines.append("")
        return "\n".join(lines)

    @staticmethod
    def _is_test_file(path: str) -> bool:
        lower = path.lower()
        return any(
            pattern in lower
            for pattern in (
                "test_",
                "_test.",
                ".test.",
                ".spec.",
                "/tests/",
                "/__tests__/",
                "/test/",
            )
        )

    @staticmethod
    def _clean_test_stem(test_path: str) -> str:
        filename = test_path.split("/")[-1].lower()
        cleaned = re.sub(r"""^(test_|tests_)""", "", filename)
        cleaned = re.sub(r"""(_test|\.test|\.spec)\.[a-z0-9]+$""", "", cleaned)
        cleaned = re.sub(r"""\.[a-z0-9]+$""", "", cleaned)
        return cleaned if len(cleaned) > 2 else ""
