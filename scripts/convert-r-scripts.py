#!/usr/bin/env python3
"""Convert lesson-oriented R scripts into readable Jupyter notebooks.

The original ``.R`` files are retained. Blocks separated by blank lines become
R code cells; standalone comment blocks become Markdown cells. This keeps the
source available for R users while giving the website a notebook representation
that can be rendered statically or opted into WebR later.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_FOLDER = ROOT / "content" / "r-basic" / "basic-r-2026"

TITLES = {
    "S00-first": "R basics: variables, functions, vectors, and missing values",
    "S01-start-data": "R basics: reading and exploring data",
    "S02-tidy": "R basics: tidy data with dplyr",
    "S03-ggplot": "R basics: visualisation with ggplot2",
    "S04-se": "R basics: SummarizedExperiment",
    "S05-onco": "R basics: oncology data practical",
}


def comment_markdown(lines: list[str]) -> str:
    result: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("##"):
            text = stripped[2:].strip()
            result.append(f"# {text}" if text else "")
        elif stripped.startswith("#"):
            result.append(stripped[1:].lstrip())
        else:
            result.append(stripped)
    return "\n".join(result).strip()


def convert(source: Path, destination: Path, force: bool = False) -> bool:
    if destination.exists() and not force:
        return False

    title = TITLES.get(source.stem, source.stem.replace("-", " ").title())
    cells: list[dict] = [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [f"# {title}\n", "\n", "This lesson was converted from the original R script.\n"],
        }
    ]

    block: list[str] = []

    def flush() -> None:
        nonlocal block
        while block and not block[0].strip():
            block.pop(0)
        while block and not block[-1].strip():
            block.pop()
        if not block:
            return
        if all(not line.strip() or line.lstrip().startswith("#") for line in block):
            markdown = comment_markdown(block)
            if markdown:
                cells.append({"cell_type": "markdown", "metadata": {}, "source": [markdown + "\n"]})
        else:
            source_lines = [line if line.endswith("\n") else line + "\n" for line in block]
            cells.append({"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": source_lines})
        block = []

    for line in source.read_text(encoding="utf-8").splitlines(keepends=True):
        if line.strip():
            block.append(line)
        else:
            flush()
    flush()

    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "R", "language": "R", "name": "ir"},
            "language_info": {"name": "R"},
            "quarto": {"title": title},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    destination.write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--folder", type=Path, default=DEFAULT_FOLDER)
    parser.add_argument("--force", action="store_true", help="overwrite existing notebooks")
    args = parser.parse_args()
    folder = args.folder if args.folder.is_absolute() else ROOT / args.folder
    created = 0
    for source in sorted(folder.glob("S*.R")):
        if convert(source, source.with_suffix(".ipynb"), args.force):
            created += 1
    print(f"Converted {created} R lesson script(s) to notebooks in {folder.relative_to(ROOT)}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
