#!/usr/bin/env python3
"""Generate Quarto navbar dropdowns from configured content directories."""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
QUARTO_CONFIG = ROOT / "_quarto.yml"
NAV_CONFIG = ROOT / "site-navigation.toml"
BEGIN = "      # BEGIN AUTO-GENERATED NAVIGATION"
END = "      # END AUTO-GENERATED NAVIGATION"


def yaml_string(value: str) -> str:
    """JSON strings are also valid YAML strings and handle escaping safely."""
    return json.dumps(value, ensure_ascii=False)


def front_matter(text: str) -> str:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return ""
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() in {"---", "..."}:
            return "\n".join(lines[1:index])
    return ""


def text_metadata(path: Path) -> tuple[str | None, bool]:
    try:
        metadata = front_matter(path.read_text(encoding="utf-8"))
    except UnicodeDecodeError:
        return None, False

    title_match = re.search(r"(?mi)^title\s*:\s*(.+?)\s*$", metadata)
    title = title_match.group(1).strip().strip("\"'") if title_match else None
    hidden = bool(re.search(r"(?mi)^nav\s*:\s*false\s*$", metadata))
    return title, hidden


def html_metadata(path: Path) -> tuple[str | None, bool]:
    """Read a title from a pre-rendered HTML file without parsing its assets."""
    try:
        contents = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None, False
    match = re.search(r"(?is)<title[^>]*>\s*(.*?)\s*</title>", contents)
    if not match:
        match = re.search(r"(?is)<h1[^>]*>\s*(.*?)\s*</h1>", contents)
    if not match:
        return None, False
    title = re.sub(r"<[^>]+>", "", match.group(1))
    return html.unescape(title).strip(), False


def notebook_metadata(path: Path) -> tuple[str | None, bool]:
    try:
        notebook = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None, False

    quarto = notebook.get("metadata", {}).get("quarto", {})
    if quarto.get("nav") is False:
        return None, True
    if quarto.get("title"):
        return str(quarto["title"]), False

    for cell in notebook.get("cells", []):
        if cell.get("cell_type") != "markdown":
            continue
        source = "".join(cell.get("source", []))
        match = re.search(r"(?m)^#\s+(.+?)\s*$", source)
        if match:
            return match.group(1), False
    return None, False


def display_title(path: Path) -> tuple[str, bool]:
    if path.suffix == ".ipynb":
        title, hidden = notebook_metadata(path)
    elif path.suffix.lower() == ".html":
        title, hidden = html_metadata(path)
    elif path.suffix.lower() == ".pdf":
        title, hidden = None, False
    else:
        title, hidden = text_metadata(path)
    fallback = path.stem.replace("-", " ").replace("_", " ").strip().title()
    return title or fallback, hidden


def section_files(section: dict) -> list[tuple[Path, str]]:
    folder = ROOT / section["folder"]
    if not folder.is_dir():
        print(f"warning: navigation folder does not exist: {folder}", file=sys.stderr)
        return []

    iterator = folder.rglob("*") if section.get("recursive", True) else folder.glob("*")
    extensions = set(section.get("extensions", [".qmd", ".Rmd", ".rmd", ".ipynb"]))
    excluded = set(section.get("exclude", []))
    entries: list[tuple[Path, str]] = []

    for path in iterator:
        relative_to_folder = path.relative_to(folder).as_posix()
        if (
            not path.is_file()
            or path.suffix not in extensions
            or path.name.startswith((".", "_"))
            or relative_to_folder in excluded
            or any(part.startswith((".", "_")) for part in path.relative_to(folder).parts[:-1])
        ):
            continue
        title, hidden = display_title(path)
        title = section.get("titles", {}).get(relative_to_folder, title)
        if not hidden:
            entries.append((path, title))

    sort_mode = section.get("sort", "title")
    if sort_mode == "filename":
        entries.sort(key=lambda item: item[0].relative_to(folder).as_posix().casefold())
    elif sort_mode == "modified":
        entries.sort(key=lambda item: item[0].stat().st_mtime, reverse=True)
    else:
        entries.sort(key=lambda item: item[1].casefold())
    return entries


def build_navigation(config: dict) -> str:
    lines = [BEGIN]
    lines.extend(
        [
            f"      - href: {yaml_string(config.get('home_href', 'index.qmd'))}",
            f"        text: {yaml_string(config.get('home_label', 'Home'))}",
        ]
    )

    for section in config.get("section", []):
        entries = section_files(section)
        if not entries:
            continue
        lines.append(f"      - text: {yaml_string(section['label'])}")
        lines.append("        menu:")
        for path, title in entries:
            href = path.relative_to(ROOT).as_posix()
            if section.get("show_format", False) and path.suffix.lower() in {".html", ".pdf"}:
                title = f"{title} ({path.suffix[1:].upper()})"
            lines.append(f"          - href: {yaml_string(href)}")
            lines.append(f"            text: {yaml_string(title)}")

    lines.append(END)
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if navigation is stale")
    args = parser.parse_args()

    config = tomllib.loads(NAV_CONFIG.read_text(encoding="utf-8"))
    current = QUARTO_CONFIG.read_text(encoding="utf-8")
    if BEGIN not in current or END not in current:
        raise SystemExit(f"navigation markers are missing from {QUARTO_CONFIG.name}")

    generated = build_navigation(config)
    updated = re.sub(
        rf"{re.escape(BEGIN)}.*?{re.escape(END)}",
        lambda _match: generated,
        current,
        flags=re.DOTALL,
    )

    if args.check:
        if updated != current:
            print("Navigation is stale. Run scripts/generate-navigation.py.", file=sys.stderr)
            return 1
        print("Navigation is up to date.")
        return 0

    QUARTO_CONFIG.write_text(updated, encoding="utf-8")
    count = sum(len(section_files(section)) for section in config.get("section", []))
    print(f"Generated navigation for {count} content files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
