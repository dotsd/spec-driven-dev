"""Architecture Engine orchestrating parsing, caching, correlation, and multi-file memory generation."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Sequence

from .cache import CacheManager
from .correlator import TraceabilityCorrelator
from .generators import (
    ApiSurfaceGenerator,
    DependenciesGenerator,
    DomainModelsGenerator,
    OverviewGenerator,
    TestMapGenerator,
    TraceabilityGenerator,
)
from .models import (
    ArchitectureCache,
    ArchitectureSummary,
    FileNode,
)
from .parsers import ALL_PARSERS, DocumentParser
from .settings import (
    load_architecture_settings,
    register_doc_path,
    register_ticket_path,
)

IGNORED_DIRS = {
    ".git",
    ".specify",
    "node_modules",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "dist",
    "build",
    ".next",
    ".nuxt",
    "target",
    "vendor",
    "coverage",
}


class ArchitectureEngine:
    """Orchestrates codebase analysis and category-based architecture memory."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root.resolve()
        self.cache_mgr = CacheManager(self.project_root)
        self.doc_parser = DocumentParser()
        self.correlator = TraceabilityCorrelator()

    def generate(
        self,
        docs_dirs: Sequence[str] | None = None,
        ticket_paths: Sequence[str] | None = None,
        force: bool = False,
    ) -> ArchitectureSummary:
        start_time = time.perf_counter()

        # Update settings with any newly passed paths
        if docs_dirs:
            for d in docs_dirs:
                register_doc_path(self.project_root, d)
        if ticket_paths:
            for t in ticket_paths:
                register_ticket_path(self.project_root, t)

        settings = load_architecture_settings(self.project_root)
        all_docs_dirs: list[str] = list(settings.get("functional_docs_paths", []))
        all_ticket_paths: list[str] = list(settings.get("ticket_paths", []))

        # Load or reset cache
        cache = ArchitectureCache(
            project_root=str(self.project_root),
            updated_at="",
        ) if force else self.cache_mgr.load()

        # 1. Discover all candidate files
        code_files, spec_files, doc_files, ticket_files = self._discover_files(
            all_docs_dirs, all_ticket_paths
        )
        all_candidate_files = code_files + spec_files + doc_files + ticket_files

        # 2. Detect changes
        added, modified, deleted = self.cache_mgr.detect_changes(all_candidate_files, cache)
        reparse_set = set(added) | set(modified)

        # 3. Handle deletions
        for del_rel in deleted:
            cache.files.pop(del_rel, None)
            cache.file_hashes.pop(del_rel, None)
            cache.file_mtimes.pop(del_rel, None)
            cache.requirements = [r for r in cache.requirements if r.source_doc != del_rel]
            cache.tickets = [t for t in cache.tickets if t.source_file != del_rel]

        # 4. Parse changed code files
        for path in code_files:
            if path in reparse_set:
                rel = self._rel_path(path)
                try:
                    content = path.read_text(encoding="utf-8", errors="replace")
                    sha, mtime, size = CacheManager.get_file_metadata(path)
                    fnode = self._parse_code_file(path, rel, content, sha, mtime, size)
                    cache.files[rel] = fnode
                    cache.file_hashes[rel] = sha
                    cache.file_mtimes[rel] = mtime
                except Exception:
                    continue

        # 5. Parse changed spec and functional doc files
        spec_and_doc_files = set(spec_files) | set(doc_files)
        for path in spec_and_doc_files:
            if path in reparse_set:
                rel = self._rel_path(path)
                try:
                    content = path.read_text(encoding="utf-8", errors="replace")
                    sha, mtime, _ = CacheManager.get_file_metadata(path)
                    new_reqs = self.doc_parser.parse_markdown_doc(path, rel, content)
                    # Replace requirements from this document
                    cache.requirements = [r for r in cache.requirements if r.source_doc != rel] + new_reqs
                    cache.file_hashes[rel] = sha
                    cache.file_mtimes[rel] = mtime
                except Exception:
                    continue

        # 6. Parse changed ticket files
        for path in ticket_files:
            if path in reparse_set:
                rel = self._rel_path(path)
                try:
                    content = path.read_text(encoding="utf-8", errors="replace")
                    sha, mtime, _ = CacheManager.get_file_metadata(path)
                    new_tickets = self.doc_parser.parse_ticket_file(path, rel, content)
                    cache.tickets = [t for t in cache.tickets if t.source_file != rel] + new_tickets
                    cache.file_hashes[rel] = sha
                    cache.file_mtimes[rel] = mtime
                except Exception:
                    continue

        # 7. Compute inter-file dependencies
        file_deps = self._resolve_file_dependencies(cache.files)

        # 8. Correlate Requirements & Tickets with Code
        traceability_links = self.correlator.correlate(
            cache.files, cache.requirements, cache.tickets
        )

        # 9. Generate category markdown files
        memory_dir = self.project_root / ".specify/memory/architecture"
        memory_dir.mkdir(parents=True, exist_ok=True)

        overview_md = OverviewGenerator().generate(
            cache.files, file_deps, cache.requirements, cache.tickets
        )
        api_surface_md = ApiSurfaceGenerator().generate(cache.files)
        domain_models_md = DomainModelsGenerator().generate(cache.files)
        traceability_md = TraceabilityGenerator().generate(
            cache.requirements, cache.tickets, traceability_links
        )
        dependencies_md = DependenciesGenerator().generate(cache.files, file_deps)
        test_map_md = TestMapGenerator().generate(cache.files)

        (memory_dir / "overview.md").write_text(overview_md, encoding="utf-8")
        (memory_dir / "api-surface.md").write_text(api_surface_md, encoding="utf-8")
        (memory_dir / "domain-models.md").write_text(domain_models_md, encoding="utf-8")
        (memory_dir / "traceability.md").write_text(traceability_md, encoding="utf-8")
        (memory_dir / "dependencies.md").write_text(dependencies_md, encoding="utf-8")
        (memory_dir / "test-map.md").write_text(test_map_md, encoding="utf-8")

        # Also write root .specify/memory/architecture.md as a pointer / executive overview
        root_arch_md = self.project_root / ".specify/memory/architecture.md"
        root_arch_md.write_text(overview_md, encoding="utf-8")

        # 10. Save cache
        self.cache_mgr.save(cache)

        duration_ms = (time.perf_counter() - start_time) * 1000

        # Build summary
        lang_counts: dict[str, int] = {}
        total_routes = 0
        total_models = 0
        total_symbols = 0
        for f in cache.files.values():
            lang_counts[f.language] = lang_counts.get(f.language, 0) + 1
            total_routes += len(f.routes)
            total_models += len(f.models)
            total_symbols += len(f.symbols)

        return ArchitectureSummary(
            total_files=len(cache.files),
            total_symbols=total_symbols,
            total_routes=total_routes,
            total_models=total_models,
            total_requirements=len(cache.requirements),
            total_tickets=len(cache.tickets),
            languages=lang_counts,
            generated_categories=[
                "overview.md",
                "api-surface.md",
                "domain-models.md",
                "traceability.md",
                "dependencies.md",
                "test-map.md",
            ],
            delta_files_reparsed=len(reparse_set),
            duration_ms=round(duration_ms, 2),
        )

    def _discover_files(
        self,
        custom_docs_dirs: list[str],
        custom_ticket_paths: list[str],
    ) -> tuple[list[Path], list[Path], list[Path], list[Path]]:
        """Find candidate code, spec, doc, and ticket files."""
        code_files: list[Path] = []
        spec_files: list[Path] = []
        doc_files: list[Path] = []
        ticket_files: list[Path] = []

        # Supported code extensions
        code_exts: set[str] = set()
        for p in ALL_PARSERS:
            code_exts.update(p.extensions)

        # Walk project
        for root, dirs, files in self.project_root.walk():
            # Prune ignored directories
            dirs[:] = [d for d in dirs if d not in IGNORED_DIRS and not d.startswith(".")]

            rel_root = root.relative_to(self.project_root)
            rel_root_str = str(rel_root).replace("\\", "/")

            is_specs_dir = rel_root_str.startswith("specs") or "specs/" in rel_root_str
            is_docs_dir = (
                rel_root_str.startswith("docs")
                or rel_root_str.startswith("prd")
                or any(rel_root_str.startswith(cd.rstrip("/")) for cd in custom_docs_dirs)
            )

            for f in files:
                fpath = root / f
                ext = fpath.suffix.lower()

                if ext in code_exts:
                    code_files.append(fpath)
                elif ext == ".md":
                    if is_specs_dir:
                        spec_files.append(fpath)
                    elif is_docs_dir:
                        doc_files.append(fpath)
                elif ext in {".csv", ".json"} and any(
                    term in f.lower() for term in ("jira", "ticket", "issue", "tasks", "stories")
                ):
                    ticket_files.append(fpath)

        # Include any explicit custom doc or ticket paths
        for cdir in custom_docs_dirs:
            p = self.project_root / cdir
            if p.exists() and p.is_dir():
                for item in p.glob("**/*.md"):
                    if item not in doc_files:
                        doc_files.append(item)

        for tpath in custom_ticket_paths:
            p = self.project_root / tpath
            if p.exists() and p.is_file() and p not in ticket_files:
                ticket_files.append(p)

        return code_files, spec_files, doc_files, ticket_files

    def _parse_code_file(
        self,
        path: Path,
        relative_path: str,
        content: str,
        sha: str,
        mtime: float,
        size: int,
    ) -> FileNode:
        matching_parser = next((p for p in ALL_PARSERS if p.can_parse(path)), None)
        if not matching_parser:
            return FileNode(
                path=relative_path,
                language="unknown",
                sha256=sha,
                size_bytes=size,
                line_count=len(content.splitlines()),
                mtime=mtime,
            )

        imports, symbols, routes, models = matching_parser.parse(path, relative_path, content)
        return FileNode(
            path=relative_path,
            language=matching_parser.language,
            sha256=sha,
            size_bytes=size,
            line_count=len(content.splitlines()),
            mtime=mtime,
            imports=imports,
            symbols=[s.id for s in symbols],
            routes=routes,
            models=models,
        )

    def _resolve_file_dependencies(self, files: dict[str, FileNode]) -> dict[str, list[str]]:
        file_deps: dict[str, list[str]] = {}
        # Map stem and file parts to path
        stem_map: dict[str, str] = {}
        for path in files.keys():
            stem = Path(path).stem
            stem_map[stem] = path

        for src_path, fnode in files.items():
            deps: set[str] = set()
            for imp in fnode.imports:
                imp_stem = imp.split(".")[-1].split("/")[-1].replace('"', "").replace("'", "")
                if imp_stem in stem_map and stem_map[imp_stem] != src_path:
                    deps.add(stem_map[imp_stem])
            file_deps[src_path] = sorted(deps)

        return file_deps

    def _rel_path(self, path: Path) -> str:
        try:
            return str(path.relative_to(self.project_root)).replace("\\", "/")
        except ValueError:
            return str(path).replace("\\", "/")
