#!/usr/bin/env python3
"""Create Quarto copies from course sources, with opt-in browser execution.

Original files are never modified. Generated pages use Quarto Live with
Pyodide for Python and WebR for R only when enabled in
``browser-executable.toml``. Other notebooks become non-executing HTML pages
with their source code preserved.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import tomllib
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
OUTPUT = ROOT / "generated-live"
MANIFEST = OUTPUT / "manifest.json"
BROWSER_CONFIG = ROOT / "browser-executable.toml"
SOURCE_SUFFIXES = {".qmd", ".Rmd", ".rmd", ".ipynb"}


def local_dataset_references(code: str) -> list[str]:
    """Find conventional local data paths that cannot run unchanged in WASM."""
    references = re.findall(
        r"(?<![\w/])(?:(?:\.\./)|(?:\.?/))?(?:data|datasets)/[^\"'`\s,)}]+",
        code,
        flags=re.IGNORECASE,
    )
    return sorted(set(references))


def split_front_matter(text: str) -> tuple[dict, str]:
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return {}, text
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() in {"---", "..."}:
            raw = "".join(lines[1:index])
            return yaml.safe_load(raw) or {}, "".join(lines[index + 1 :])
    return {}, text


def rewrite_asset_references(text: str, source: Path, destination: Path) -> str:
    """Point local notebook/lesson assets at their published content paths."""

    def resolve(reference: str) -> str:
        if (
            not reference
            or reference.startswith(("#", "/", "data:"))
            or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*://", reference)
        ):
            return reference
        candidate = (source.parent / reference.split("#", 1)[0].split("?", 1)[0]).resolve()
        try:
            candidate.relative_to(ROOT)
        except ValueError:
            return reference
        if not candidate.is_file():
            return reference
        suffix = reference[len(reference.split("#", 1)[0].split("?", 1)[0]) :]
        return Path(os.path.relpath(candidate, destination.parent)).as_posix() + suffix

    text = re.sub(
        r"(!\[[^\]]*\]\()([^)]*)(\))",
        lambda match: match.group(1) + resolve(match.group(2)) + match.group(3),
        text,
    )
    return re.sub(
        r"((?:src|href)=[\"'])([^\"']+)([\"'])",
        lambda match: match.group(1) + resolve(match.group(2)) + match.group(3),
        text,
    )


def live_header(metadata: dict, destination: Path) -> str:
    metadata = dict(metadata)
    metadata["engine"] = "knitr"
    metadata["format"] = {
        "live-html": {
            "css": "../" * len(destination.relative_to(ROOT).parent.parts) + "styles.css"
        }
    }
    dumped = yaml.safe_dump(metadata, sort_keys=False, allow_unicode=True).strip()
    extension = "../" * len(destination.relative_to(ROOT).parent.parts)
    include = f"{{{{< include {extension}_extensions/r-wasm/live/_knitr.qmd >}}}}"
    return f"---\n{dumped}\n---\n\n{include}\n\n"


def static_header(metadata: dict) -> str:
    """Create a non-executing HTML page while preserving notebook source."""
    metadata = dict(metadata)
    metadata["format"] = "html"
    metadata["execute"] = {"enabled": False}
    dumped = yaml.safe_dump(metadata, sort_keys=False, allow_unicode=True).strip()
    return f"---\n{dumped}\n---\n\n"


def suspicious_constructs(code: str, language: str) -> list[str]:
    warnings: list[str] = []
    if language == "python":
        checks = {
            "shell or notebook magic": r"(?m)^\s*[!%]",
            "subprocess/system command": r"\b(subprocess|os\.system|os\.popen)\b",
            "GPU library": r"\b(torch|tensorflow|cupy|jax)\b",
            "local absolute path": r"(?<![\w])(?:/home/|/mnt/|[A-Za-z]:\\)",
        }
    else:
        checks = {
            "system command": r"\b(system|system2|shell)\s*\(",
            "local absolute path": r"(?:/home/|/mnt/|[A-Za-z]:\\)",
            "native or external service package": r"\blibrary\s*\(\s*(sf|rJava|odbc|RPostgres|RMySQL)\b",
        }
    for description, pattern in checks.items():
        if re.search(pattern, code, flags=re.IGNORECASE):
            warnings.append(description)
    return warnings


def convert_markdown_source(source: Path, destination: Path) -> tuple[bool, list[str]]:
    text = source.read_text(encoding="utf-8")
    metadata, body = split_front_matter(text)
    converted = 0
    warnings: list[str] = []

    def replace(match: re.Match[str]) -> str:
        nonlocal converted
        fence, language, options = match.groups()
        converted += 1
        runtime = "pyodide" if language.lower() == "python" else "webr"
        return f"{fence}{{{runtime}{options or ''}}}"

    pattern = re.compile(r"(?m)^(\s*`{3,})\{(python|r)(\s+[^}]*)?\}\s*$", re.IGNORECASE)
    converted_body = pattern.sub(replace, body)
    if converted == 0:
        return False, []

    converted_body = rewrite_asset_references(converted_body, source, destination)

    for match in re.finditer(
        r"(?ms)^\s*`{3,}\{(pyodide|webr)[^}]*\}\s*\n(.*?)^\s*`{3,}\s*$",
        converted_body,
    ):
        language = "python" if match.group(1) == "pyodide" else "r"
        for warning in suspicious_constructs(match.group(2), language):
            warnings.append(f"{source.relative_to(ROOT)}: {warning}")
        for reference in local_dataset_references(match.group(2)):
            warnings.append(
                f"{source.relative_to(ROOT)}: browser copy references local dataset "
                f"'{reference}' (load it with fetch/pyfetch instead; see DATASETS.md)"
            )

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(live_header(metadata, destination) + converted_body, encoding="utf-8")
    return True, warnings


def notebook_language(notebook: dict) -> str | None:
    metadata = notebook.get("metadata", {})
    candidates = [
        metadata.get("kernelspec", {}).get("language"),
        metadata.get("language_info", {}).get("name"),
    ]
    for language in candidates:
        if language and language.lower() in {"python", "r"}:
            return language.lower()
    return None


def notebook_title(notebook: dict, source: Path) -> str:
    quarto = notebook.get("metadata", {}).get("quarto", {})
    if quarto.get("title"):
        return str(quarto["title"])
    first_heading = None
    for cell in notebook.get("cells", []):
        if cell.get("cell_type") == "markdown":
            match = re.search(r"(?m)^#\s+(.+?)\s*$", "".join(cell.get("source", [])))
            if match:
                first_heading = match.group(1).strip()
                break

    # Several of the course notebooks share a generic heading. Use the file
    # name in that case so the generated navigation remains distinguishable.
    generic_headings = {"ubds 2026: basic python"}
    if first_heading and first_heading.casefold() not in generic_headings:
        return first_heading

    stem = source.stem.replace("-", " ").replace("_", " ").strip()
    if re.fullmatch(r"day\s+\d+", stem, flags=re.IGNORECASE):
        return f"{stem.title()} — Basic Python"
    if stem.casefold() == "intro to pandas matplotlib":
        return "Intro to Pandas and Matplotlib"
    if stem.casefold() == "querying gff":
        return "Querying GFF"
    return stem.title() or "Notebook"


def convert_notebook(
    source: Path, destination: Path, browser_executable: bool
) -> tuple[bool, list[str]]:
    notebook = json.loads(source.read_text(encoding="utf-8"))
    language = notebook_language(notebook)
    if language not in {"python", "r"}:
        return False, [f"{source.relative_to(ROOT)}: unsupported or missing kernel language"]

    runtime = ("pyodide" if language == "python" else "webr") if browser_executable else language
    body: list[str] = []
    warnings: list[str] = []
    code_cells = 0
    for cell in notebook.get("cells", []):
        source_text = "".join(cell.get("source", [])).rstrip()
        if cell.get("cell_type") == "markdown":
            body.extend([rewrite_asset_references(source_text, source, destination), ""])
        elif cell.get("cell_type") == "code":
            code_cells += 1
            if not source_text:
                cell_language = "Python" if language == "python" else "R"
                body.extend(
                    [
                        f"> **Exercise:** write your answer in this editable {cell_language} cell.",
                        "",
                    ]
                )
            fence = f"```{{{runtime}}}" if browser_executable else f"```{runtime}"
            body.extend([fence, source_text, "```", ""])
            if browser_executable:
                for warning in suspicious_constructs(source_text, language):
                    warnings.append(f"{source.relative_to(ROOT)} cell {code_cells}: {warning}")
                for reference in local_dataset_references(source_text):
                    warnings.append(
                        f"{source.relative_to(ROOT)} cell {code_cells}: browser copy references "
                        f"local dataset '{reference}' (load it with fetch/pyfetch instead; "
                        "see DATASETS.md)"
                    )
        elif source_text:
            body.extend(["```text", source_text, "```", ""])

    if code_cells == 0:
        return False, []
    metadata = {"title": notebook_title(notebook, source)}
    destination.parent.mkdir(parents=True, exist_ok=True)
    header = live_header(metadata, destination) if browser_executable else static_header(metadata)
    destination.write_text(header + "\n".join(body), encoding="utf-8")
    return True, warnings


def browser_execution_config() -> dict:
    if not BROWSER_CONFIG.is_file():
        return {"default": False, "include": [], "exclude": []}
    with BROWSER_CONFIG.open("rb") as handle:
        config = tomllib.load(handle)
    return {
        "default": bool(config.get("default", False)),
        "include": {str(path).replace("\\", "/") for path in config.get("include", [])},
        "exclude": {str(path).replace("\\", "/") for path in config.get("exclude", [])},
    }


def is_browser_executable(source: Path, config: dict) -> bool:
    relative = source.relative_to(ROOT).as_posix()
    if relative in config["exclude"]:
        return False
    if relative in config["include"]:
        return True
    return config["default"]


def main() -> int:
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir(parents=True)

    mapping: dict[str, str] = {}
    warnings: list[str] = []
    execution_config = browser_execution_config()
    browser_pages = 0
    for source in sorted(CONTENT.rglob("*")):
        if not source.is_file() or source.suffix not in SOURCE_SUFFIXES:
            continue
        if any(part.startswith((".", "_")) for part in source.relative_to(CONTENT).parts):
            continue
        relative = source.relative_to(ROOT)
        destination = OUTPUT / relative.with_suffix(".qmd")
        try:
            if source.suffix == ".ipynb":
                enabled = is_browser_executable(source, execution_config)
                created, file_warnings = convert_notebook(
                    source, destination, enabled
                )
                if created and enabled:
                    browser_pages += 1
            else:
                created, file_warnings = convert_markdown_source(source, destination)
                if created:
                    browser_pages += 1
        except Exception as error:  # report one bad source without stopping every page
            created = False
            file_warnings = [f"{relative}: conversion failed: {error}"]
        warnings.extend(file_warnings)
        if created:
            mapping[relative.as_posix()] = destination.relative_to(ROOT).as_posix()

    MANIFEST.write_text(
        json.dumps({"pages": mapping, "warnings": warnings}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Generated {len(mapping)} pages; {browser_pages} are browser-executable.")
    if warnings:
        print(f"Reported {len(warnings)} compatibility warnings in {MANIFEST.relative_to(ROOT)}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
