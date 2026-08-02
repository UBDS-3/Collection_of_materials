# Collection of materials

A Quarto-powered teaching-materials repository. It publishes `.qmd`, `.Rmd`,
and `.ipynb` sources as a GitHub Pages website and builds slides as HTML, PDF,
and PowerPoint (`.pptx`). Quarto Live provides browser-executable Python and R
exercises using Pyodide and WebR.

## Repository layout

```text
.
├── _quarto.yml                 # Website configuration and navigation
├── index.qmd                   # Website landing page
├── content/                    # One mixed-format folder per navbar tab
│   ├── r-basic/
│   ├── python-basic/
│   ├── advanced/
│   ├── lectures/
│   ├── research-highlights/
│   └── post-school-materials/
└── .github/workflows/publish.yml
```

Add each file to the appropriate folder below `content/`: `r-basic`,
`python-basic`, `advanced`, `lectures`, `research-highlights`, or
`post-school-materials`. Each folder accepts notebooks, rendered HTML, PDFs,
and PowerPoint decks. Files are rendered or copied automatically and added to
the matching navbar dropdown. Configure sections in `site-navigation.toml`.

Pre-rendered HTML pages and PDF documents are also discovered, copied unchanged
to the published site, and shown inline through automatically generated QMD
wrapper pages linked from the appropriate dropdown.

For navigation, layout, colors, fonts, and reusable card styles, see
[`SITE_CUSTOMIZATION.md`](SITE_CUSTOMIZATION.md).

## Render locally

Install [Quarto](https://quarto.org/docs/get-started/) and then run:

```bash
uv sync
./scripts/render-local.sh
```

Alternatively, activate the environment before invoking Quarto directly:

```bash
source .venv/bin/activate
quarto render
```

If `uv` is unavailable, `python3 -m venv .venv` followed by
`.venv/bin/python -m pip install -r requirements.txt` is equivalent, provided
the operating system's `python3-venv` package is installed.

To build exactly what GitHub Pages will publish:

```bash
./scripts/render-local.sh
```

The site is written to `_site/`. The example slide deck produces:

- `_site/content/lectures/course-slides.html`
- `_site/content/lectures/course-slides.pdf`
- `_site/content/lectures/course-slides.pptx`

Rendering `.Rmd` files requires R plus `knitr` and `rmarkdown`. PDF slides
require a TeX installation; the GitHub Actions workflow installs TinyTeX.

The local render script selects `.venv` and keeps Quarto, Jupyter, and
Matplotlib caches inside the project. The pinned Python packages prevent NumPy
ABI errors such as `AttributeError: _ARRAY_API not found`, which occurs when an
extension compiled for NumPy 1.x is loaded by NumPy 2.x.

### Automatic browser-executable copies

Before rendering, `scripts/generate-live-pages.py` scans all course folders.
It creates non-destructive browser-ready copies of compatible sources:

- Python QMD/Rmd chunks become `{pyodide}` cells.
- R QMD/Rmd chunks become `{webr}` cells.
- Python and R notebook code cells become matching Quarto Live cells.
- Sources with no convertible code keep their normal rendered link.

Generated copies live under ignored `generated-live/`, and the navigation
automatically links to them. Compatibility findings are written to
`generated-live/manifest.json`. Review its `warnings` array when adding new
content: shell commands, native libraries, GPUs, external services, and local
absolute paths may not work in WebAssembly.

Run only the conversion step with:

```bash
uv run python scripts/generate-live-pages.py
```

## Publish on GitHub Pages

1. Create a GitHub repository and push these files to its `main` branch.
2. In **Settings → Pages → Build and deployment**, select **GitHub Actions**.
3. Run the **Publish Quarto website** workflow, or push to `main`.

The workflow builds the site and deploys it without committing generated
HTML, PDF, or PowerPoint files to the repository.

The deployed homepage is expected at
`https://ubds-3.github.io/Collection_of_materials/`. It is a GitHub **Pages**
deployment (not GitHub Packages), and its root `index.html` includes the
browser-executable Python and R cells.

## Adding content

### Quarto page

Copy `content/python-basic/quarto-example.qmd`, change its title and content,
and place it in the folder for the appropriate tab.

### R Markdown page

Copy `content/r-basic/rmarkdown-example.Rmd`. Keep ordinary R Markdown YAML; Quarto
will place the rendered page inside the website.

### Jupyter notebook

Place an `.ipynb` file under the appropriate `content/` category. Commit notebook outputs if the page
should build without re-running its Python cells. To execute notebooks in CI,
add their Python dependencies to the workflow and set `execute: enabled: true`
in `_quarto.yml` or the notebook metadata.

### Slides

Copy `content/lectures/course-slides.qmd`. Its `format` block creates Reveal.js HTML,
PowerPoint, and Beamer PDF from one source. Keep slides broadly compatible
across formats: use headings as slide boundaries and avoid Reveal.js-only
layout features when PowerPoint/PDF parity matters.

### Browser-executable code

Ordinary `{python}` and `{r}` chunks run while the site is built; their web
output is static. For an editable cell with a **Run Code** button, use the
Quarto Live format and browser-runtime cell types:

```yaml
---
engine: knitr
format: live-html
---

{{< include ../_extensions/r-wasm/live/_knitr.qmd >}}
```

Then use a `pyodide` block for Python or a `webr` block for R. See
`content/advanced/live-code.qmd` for complete examples. Browser runtimes cannot use
arbitrary native Python or R packages; packages must have WebAssembly-compatible
builds.
