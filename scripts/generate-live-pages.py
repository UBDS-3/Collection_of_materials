#!/usr/bin/env python3
"""Create browser-executable Quarto copies from compatible course sources.

Original files are never modified. Generated pages use Quarto Live with
Pyodide for Python and WebR for R. Files without convertible code are skipped.
"""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
OUTPUT = ROOT / "generated-live"
MANIFEST = OUTPUT / "manifest.json"
SOURCE_SUFFIXES = {".qmd", ".Rmd", ".rmd", ".ipynb"}


def split_front_matter(text: str) -> tuple[dict, str]:
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return {}, text
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() in {"---", "..."}:
            raw = "".join(lines[1:index])
            return yaml.safe_load(raw) or {}, "".join(lines[index + 1 :])
    return {}, text


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

    for match in re.finditer(
        r"(?ms)^\s*`{3,}\{(pyodide|webr)[^}]*\}\s*\n(.*?)^\s*`{3,}\s*$",
        converted_body,
    ):
        language = "python" if match.group(1) == "pyodide" else "r"
        for warning in suspicious_constructs(match.group(2), language):
            warnings.append(f"{source.relative_to(ROOT)}: {warning}")

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
    for cell in notebook.get("cells", []):
        if cell.get("cell_type") == "markdown":
            match = re.search(r"(?m)^#\s+(.+?)\s*$", "".join(cell.get("source", [])))
            if match:
                return match.group(1)
    return source.stem.replace("-", " ").replace("_", " ").title()


def convert_notebook(source: Path, destination: Path) -> tuple[bool, list[str]]:
    notebook = json.loads(source.read_text(encoding="utf-8"))
    language = notebook_language(notebook)
    if language not in {"python", "r"}:
        return False, [f"{source.relative_to(ROOT)}: unsupported or missing kernel language"]

    runtime = "pyodide" if language == "python" else "webr"
    body: list[str] = []
    warnings: list[str] = []
    code_cells = 0
    for cell in notebook.get("cells", []):
        source_text = "".join(cell.get("source", [])).rstrip()
        if cell.get("cell_type") == "markdown":
            body.extend([source_text, ""])
        elif cell.get("cell_type") == "code":
            code_cells += 1
            body.extend([f"```{{{runtime}}}", source_text, "```", ""])
            for warning in suspicious_constructs(source_text, language):
                warnings.append(f"{source.relative_to(ROOT)} cell {code_cells}: {warning}")
        elif source_text:
            body.extend(["```text", source_text, "```", ""])

    if code_cells == 0:
        return False, []
    metadata = {"title": notebook_title(notebook, source)}
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(live_header(metadata, destination) + "\n".join(body), encoding="utf-8")
    return True, warnings


def main() -> int:
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir(parents=True)

    mapping: dict[str, str] = {}
    warnings: list[str] = []
    for source in sorted(CONTENT.rglob("*")):
        if not source.is_file() or source.suffix not in SOURCE_SUFFIXES:
            continue
        if any(part.startswith((".", "_")) for part in source.relative_to(CONTENT).parts):
            continue
        relative = source.relative_to(ROOT)
        destination = OUTPUT / relative.with_suffix(".qmd")
        try:
            if source.suffix == ".ipynb":
                created, file_warnings = convert_notebook(source, destination)
            else:
                created, file_warnings = convert_markdown_source(source, destination)
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
    print(f"Generated {len(mapping)} browser-executable pages.")
    if warnings:
        print(f"Reported {len(warnings)} compatibility warnings in {MANIFEST.relative_to(ROOT)}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
