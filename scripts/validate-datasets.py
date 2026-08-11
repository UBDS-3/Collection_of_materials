#!/usr/bin/env python3
"""Reject datasets that are too large to sensibly publish or load in a browser.

Datasets may live in the shared ``datasets/`` directory or in a ``data/``
directory beside a lesson. Limits are intentionally conservative because a
Quarto Live session downloads data into the reader's browser.
"""

from __future__ import annotations

import os
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MAX_FILE_MB = 20
DEFAULT_MAX_TOTAL_MB = 100
IGNORED_NAMES = {".gitkeep", ".DS_Store", "README.md"}


def limit_bytes(variable: str, default_mb: int) -> int:
    """Read a positive integer MiB limit from the environment."""
    raw = os.environ.get(variable, str(default_mb))
    try:
        megabytes = int(raw)
    except ValueError as error:
        raise SystemExit(f"{variable} must be a positive whole number of MiB; got {raw!r}.") from error
    if megabytes <= 0:
        raise SystemExit(f"{variable} must be a positive whole number of MiB; got {raw!r}.")
    return megabytes * 1024 * 1024


def dataset_files() -> list[Path]:
    roots = [ROOT / "datasets"]
    roots.extend(path for path in (ROOT / "content").rglob("data") if path.is_dir())
    files: list[Path] = []
    for directory in roots:
        if not directory.is_dir():
            continue
        files.extend(
            path for path in directory.rglob("*") if path.is_file() and path.name not in IGNORED_NAMES
        )
    return sorted(set(files))


def main() -> int:
    max_file = limit_bytes("DATASET_MAX_FILE_MB", DEFAULT_MAX_FILE_MB)
    max_total = limit_bytes("DATASET_MAX_TOTAL_MB", DEFAULT_MAX_TOTAL_MB)
    files = dataset_files()
    oversized = [path for path in files if path.stat().st_size > max_file]
    total = sum(path.stat().st_size for path in files)

    if oversized or total > max_total:
        print("Dataset validation failed:")
        for path in oversized:
            size_mib = path.stat().st_size / 1024 / 1024
            print(f"- {path.relative_to(ROOT)} is {size_mib:.1f} MiB (limit: {max_file / 1024 / 1024:.0f} MiB)")
        if total > max_total:
            print(
                f"- all datasets total {total / 1024 / 1024:.1f} MiB "
                f"(limit: {max_total / 1024 / 1024:.0f} MiB)"
            )
        print("Use a smaller teaching extract, or host large data externally and download it at runtime.")
        return 1

    print(
        f"Dataset validation passed: {len(files)} file(s), {total / 1024 / 1024:.1f} MiB "
        f"(per-file limit {max_file / 1024 / 1024:.0f} MiB)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
