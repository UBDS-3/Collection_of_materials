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
├── materials/                  # QMD, Rmd, and notebook examples
├── slides/                     # Multi-format slide sources
└── .github/workflows/publish.yml
```

Add teaching content below `materials/` and slides below `slides/`. Supported
documents are rendered automatically, and their titles are added to generated
navbar dropdowns. Configure folder sections and sorting in
`site-navigation.toml`.

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

- `_site/slides/course-slides.html`
- `_site/slides/course-slides.pdf`
- `_site/slides/course-slides.pptx`

Rendering `.Rmd` files requires R plus `knitr` and `rmarkdown`. PDF slides
require a TeX installation; the GitHub Actions workflow installs TinyTeX.

The local render script selects `.venv` and keeps Quarto, Jupyter, and
Matplotlib caches inside the project. The pinned Python packages prevent NumPy
ABI errors such as `AttributeError: _ARRAY_API not found`, which occurs when an
extension compiled for NumPy 1.x is loaded by NumPy 2.x.

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

Copy `materials/quarto-example.qmd`, change its title and content, and add its
path to `_quarto.yml`.

### R Markdown page

Copy `materials/rmarkdown-example.Rmd`. Keep ordinary R Markdown YAML; Quarto
will place the rendered page inside the website.

### Jupyter notebook

Place an `.ipynb` file under `materials/`. Commit notebook outputs if the page
should build without re-running its Python cells. To execute notebooks in CI,
add their Python dependencies to the workflow and set `execute: enabled: true`
in `_quarto.yml` or the notebook metadata.

### Slides

Copy `slides/course-slides.qmd`. Its `format` block creates Reveal.js HTML,
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
`materials/live-code.qmd` for complete examples. Browser runtimes cannot use
arbitrary native Python or R packages; packages must have WebAssembly-compatible
builds.
