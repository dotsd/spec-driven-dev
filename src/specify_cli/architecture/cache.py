"""Delta Hash Cache Manager for sub-second incremental architecture refreshes."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence
from .models import ArchitectureCache

CACHE_DIR_NAME = ".specify/cache"
CACHE_FILE_NAME = "architecture_cache.json"


class CacheManager:
    """Manages file hashes, mtimes, and incremental change detection."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.cache_dir = project_root / CACHE_DIR_NAME
        self.cache_file = self.cache_dir / CACHE_FILE_NAME

    def load(self) -> ArchitectureCache:
        """Load cache from disk, or return empty cache if missing/invalid."""
        if not self.cache_file.exists():
            return ArchitectureCache(
                project_root=str(self.project_root),
                updated_at=datetime.now(timezone.utc).isoformat(),
            )
        try:
            raw = json.loads(self.cache_file.read_text(encoding="utf-8"))
            return ArchitectureCache.model_validate(raw)
        except Exception:
            return ArchitectureCache(
                project_root=str(self.project_root),
                updated_at=datetime.now(timezone.utc).isoformat(),
            )

    def save(self, cache: ArchitectureCache) -> None:
        """Persist cache to disk."""
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        cache.updated_at = datetime.now(timezone.utc).isoformat()
        try:
            self.cache_file.write_text(cache.model_dump_json(indent=2), encoding="utf-8")
        except Exception:
            pass

    @staticmethod
    def get_file_metadata(path: Path) -> tuple[str, float, int]:
        """Compute sha256, mtime, and size of a file."""
        stat = path.stat()
        mtime = stat.st_mtime
        size = stat.st_size
        sha = hashlib.sha256()
        with open(path, "rb") as f:
            while chunk := f.read(65536):
                sha.update(chunk)
        return sha.hexdigest(), mtime, size

    def detect_changes(
        self,
        current_files: Sequence[Path],
        cache: ArchitectureCache,
    ) -> tuple[list[Path], list[Path], list[str]]:
        """Compare current file system state against cache.

        Returns:
            (added_files, modified_files, deleted_file_relpaths)
        """
        added: list[Path] = []
        modified: list[Path] = []
        seen_rel_paths: set[str] = set()

        for path in current_files:
            try:
                rel = str(path.relative_to(self.project_root))
            except ValueError:
                rel = str(path)
            seen_rel_paths.add(rel)

            if rel not in cache.file_hashes:
                added.append(path)
            else:
                # Fast mtime check before hashing
                try:
                    current_mtime = path.stat().st_mtime
                    cached_mtime = cache.file_mtimes.get(rel, 0.0)
                    if abs(current_mtime - cached_mtime) > 1e-4:
                        # Mtime changed, verify content hash
                        new_sha, _, _ = self.get_file_metadata(path)
                        if new_sha != cache.file_hashes.get(rel):
                            modified.append(path)
                except OSError:
                    continue

        deleted: list[str] = [
            rel for rel in cache.file_hashes.keys() if rel not in seen_rel_paths
        ]

        return added, modified, deleted
