"""Unit tests for the delta cache manager."""

from __future__ import annotations

import time
from pathlib import Path
from specify_cli.architecture.cache import CacheManager


def test_delta_cache_change_detection(tmp_path: Path) -> None:
    cache_mgr = CacheManager(tmp_path)
    cache = cache_mgr.load()

    # Create 3 files
    f1 = tmp_path / "a.py"
    f2 = tmp_path / "b.py"
    f3 = tmp_path / "c.py"
    f1.write_text("print('a')", encoding="utf-8")
    f2.write_text("print('b')", encoding="utf-8")
    f3.write_text("print('c')", encoding="utf-8")

    # Initial scan -> all 3 are added
    added, modified, deleted = cache_mgr.detect_changes([f1, f2, f3], cache)
    assert len(added) == 3
    assert len(modified) == 0
    assert len(deleted) == 0

    # Populate cache
    for f in (f1, f2, f3):
        sha, mtime, size = CacheManager.get_file_metadata(f)
        rel = f.name
        cache.file_hashes[rel] = sha
        cache.file_mtimes[rel] = mtime
    cache_mgr.save(cache)

    # Second scan with no modifications -> 0 changes
    added, modified, deleted = cache_mgr.detect_changes([f1, f2, f3], cache)
    assert len(added) == 0
    assert len(modified) == 0
    assert len(deleted) == 0

    # Modify 1 file
    time.sleep(0.01)  # Ensure mtime increments
    f2.write_text("print('b modified')", encoding="utf-8")

    added, modified, deleted = cache_mgr.detect_changes([f1, f2, f3], cache)
    assert len(added) == 0
    assert len(modified) == 1
    assert modified[0] == f2
    assert len(deleted) == 0

    # Delete 1 file
    f3.unlink()
    added, modified, deleted = cache_mgr.detect_changes([f1, f2], cache)
    assert len(deleted) == 1
    assert deleted[0] == "c.py"
