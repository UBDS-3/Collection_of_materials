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
from urllib.parse import quote


ROOT = Path(__file__).resolve().parent.parent
QUARTO_CONFIG = ROOT / "_quarto.yml"
NAV_CONFIG = ROOT / "site-navigation.toml"
BEGIN = "      # BEGIN AUTO-GENERATED NAVIGATION"
END = "      # END AUTO-GENERATED NAVIGATION"
GENERATED_DIR = ROOT / "generated-pages"
MANIFEST = GENERATED_DIR / ".manifest.json"
LIVE_MANIFEST = ROOT / "generated-live" / "manifest.json"


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

    first_heading = None
    for cell in notebook.get("cells", []):
        if cell.get("cell_type") != "markdown":
            continue
        source = "".join(cell.get("source", []))
        match = re.search(r"(?m)^#\s+(.+?)\s*$", source)
        if match:
            first_heading = match.group(1).strip()
            break
    if first_heading and first_heading.casefold() not in {"ubds 2026: basic python"}:
        return first_heading, False
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
    stem = path.stem.replace("-", " ").replace("_", " ").strip()
    fallback = stem.title()
    if re.fullmatch(r"day\s+\d+", stem, flags=re.IGNORECASE):
        fallback = f"{fallback} — Basic Python"
    elif stem.casefold() == "intro to pandas matplotlib":
        fallback = "Intro to Pandas and Matplotlib"
    elif stem.casefold() == "querying gff":
        fallback = "Querying GFF"
    return title or fallback, hidden


def clear_previous_generated_pages() -> None:
    """Remove only wrapper files recorded in our previous manifest."""
    if not MANIFEST.is_file():
        return
    try:
        generated = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        generated = []
    for relative in generated:
        candidate = (ROOT / relative).resolve()
        if GENERATED_DIR.resolve() in candidate.parents and candidate.suffix == ".qmd":
            candidate.unlink(missing_ok=True)


def write_embed_page(path: Path, title: str) -> Path:
    """Create a QMD page that embeds a static HTML or PDF resource."""
    source_relative = path.relative_to(ROOT)
    wrapper_relative = Path("generated-pages") / source_relative.parent / (
        f"{path.stem}-{path.suffix[1:].lower()}.qmd"
    )
    wrapper = ROOT / wrapper_relative
    wrapper.parent.mkdir(parents=True, exist_ok=True)

    output_parent = wrapper_relative.parent
    depth = len(output_parent.parts)
    resource_url = "../" * depth + quote(source_relative.as_posix(), safe="/")
    file_type = path.suffix[1:].upper()
    if path.suffix.lower() == ".pdf":
        guidance = "Use the viewer controls to navigate, zoom, or download the PDF."
    elif path.suffix.lower() == ".html":
        guidance = "This is an embedded, previously rendered HTML document."
    else:
        guidance = "PowerPoint files are provided as downloads and open in your presentation application."

    embed = ""
    if path.suffix.lower() in {".pdf", ".html"}:
        embed = (
            f'<iframe class="embedded-document embedded-{path.suffix[1:].lower()}" '
            f'src="{resource_url}" title={yaml_string(title)} loading="lazy"></iframe>'
        )

    wrapper.write_text(
        "\n".join(
            [
                "---",
                f"title: {yaml_string(title)}",
                "format:",
                "  html:",
                "    toc: false",
                "    page-layout: full",
                "---",
                "",
                f"{guidance} [Open or download the original {file_type}]({resource_url}){{target=\"_blank\"}}.",
                "",
                embed,
                "",
            ]
        ),
        encoding="utf-8",
    )
    return wrapper_relative


def section_files(section: dict) -> list[tuple[Path, str, Path]]:
    folder = ROOT / section["folder"]
    if not folder.is_dir():
        print(f"warning: navigation folder does not exist: {folder}", file=sys.stderr)
        return []

    iterator = folder.rglob("*") if section.get("recursive", True) else folder.glob("*")
    extensions = set(section.get("extensions", [".qmd", ".Rmd", ".rmd", ".ipynb"]))
    excluded = set(section.get("exclude", []))
    entries: list[tuple[Path, str, Path]] = []

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
            href = (
                write_embed_page(path, title)
                if path.suffix.lower() in {".html", ".pdf", ".pptx"}
                else path.relative_to(ROOT)
            )
            entries.append((path, title, href))

    sort_mode = section.get("sort", "title")
    if sort_mode == "filename":
        entries.sort(key=lambda item: item[0].relative_to(folder).as_posix().casefold())
    elif sort_mode == "modified":
        entries.sort(key=lambda item: item[0].stat().st_mtime, reverse=True)
    else:
        entries.sort(key=lambda item: item[1].casefold())
    return entries


def build_navigation(config: dict) -> str:
    live_pages: dict[str, str] = {}
    if LIVE_MANIFEST.is_file():
        try:
            live_pages = json.loads(LIVE_MANIFEST.read_text(encoding="utf-8")).get("pages", {})
        except json.JSONDecodeError:
            pass
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
        for link in section.get("links", []):
            lines.append(f"          - href: {yaml_string(link['href'])}")
            lines.append(f"            text: {yaml_string(link['text'])}")
        for path, title, href_path in entries:
            source_href = path.relative_to(ROOT).as_posix()
            href = live_pages.get(source_href, href_path.as_posix())
            if section.get("show_format", False) and path.suffix.lower() in {".html", ".pdf", ".pptx"}:
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
    clear_previous_generated_pages()
    current = QUARTO_CONFIG.read_text(encoding="utf-8")
    if BEGIN not in current or END not in current:
        raise SystemExit(f"navigation markers are missing from {QUARTO_CONFIG.name}")

    generated = build_navigation(config)
    generated_wrappers = sorted(
        path.relative_to(ROOT).as_posix()
        for path in GENERATED_DIR.rglob("*.qmd")
    )
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(generated_wrappers, indent=2) + "\n", encoding="utf-8")
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
