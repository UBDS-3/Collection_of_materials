# Site customization guide

The site is deliberately split into content, navigation, and visual styling so
you can change one without rewriting the others.

## Where to change things

| What you want to change | File |
|---|---|
| Dynamic dropdown names, folders, ordering | `site-navigation.toml` |
| Site title, footer, search, fixed links | `_quarto.yml` |
| Colors, fonts, width, spacing, corners, shadows | `styles.css` |
| Homepage content and arrangement | `index.qmd` |
| Which folder patterns are rendered | `_quarto.yml` → `project.render` |
| Individual page title and options | YAML header of that `.qmd`/`.Rmd` file |

## Dynamic navigation tabs

The six course-area menus are generated from their respective `content/`
folders before every local and GitHub Actions render. Configure the sections
in `site-navigation.toml`; do not edit the generated block in `_quarto.yml`.

The recursive glob patterns under `_quarto.yml` → `project.render` render all
supported documents in those folders. You only need to change them when adding
a completely new top-level content folder.

A section looks like this:

```toml
[[section]]
label = "Lectures"
folder = "content/lectures"
recursive = true
sort = "title"
extensions = [".qmd", ".Rmd", ".rmd", ".ipynb", ".html", ".pdf", ".pptx"]
show_format = true
exclude = []

[section.titles]
"technical-filename.pdf" = "Human-friendly title"
```

The displayed link name comes from the document's YAML `title`. For notebooks,
the generator checks `metadata.quarto.title`, then the first Markdown level-one
heading. For static HTML it reads the HTML `<title>`. PDFs and files without
embedded titles use a cleaned-up filename. Set `show_format = true` to append
`(HTML)` or `(PDF)` to static document links.

Use the optional `[section.titles]` table to override a generated name without
renaming the file. Paths in that table are relative to the section folder.

Quarto renders `.qmd`, `.Rmd`, and `.ipynb` sources. Existing `.html`, `.pdf`,
and `.pptx` files are copied unchanged through `project.resources`. The navigation script
also creates ignored QMD wrapper pages under `generated-pages/`, allowing the
files to appear inline inside the main website layout. Never edit those wrapper
pages directly because they are regenerated before every build.

If an HTML export has a companion directory such as `lesson_files/`, keep it
beside the HTML file; the `*_files` resource pattern copies it too.

Embedding an existing HTML preserves JavaScript already present in that HTML.
It does not turn static code listings back into executable cells. Browser-run
cells require source documents using `{pyodide}` or `{webr}`.

## Automatic live-code conversion

`scripts/generate-live-pages.py` converts compatible Python and R cells from
QMD, Rmd, and IPYNB sources without changing the originals. Generated pages
are placed under `generated-live/` and preferred automatically by the navbar.

The conversion is intentionally best-effort. Inspect
`generated-live/manifest.json` after rendering. Its `warnings` array flags
constructs such as shell commands, absolute local paths, GPU libraries, and
packages that commonly need native system services. A page can still require
manual edits even when its syntax was converted successfully.

To keep a document rendered but hide it from navigation, add this to its YAML:

```yaml
nav: false
```

You can also list a path relative to its section folder under `exclude` in
`site-navigation.toml`. Run `python scripts/generate-navigation.py` whenever
you want to inspect the generated `_quarto.yml` without doing a full render.

## Colors and typography

Edit only the variables at the top of `styles.css`. For example:

```css
:root {
  --site-primary: #6f2c91;
  --site-accent: #f3eafa;
  --site-font: Arial, sans-serif;
  --site-content-width: 1050px;
  --site-radius: 0.25rem;
  --site-shadow: none;
}
```

For a font hosted by Google Fonts, add an `@import` at the beginning of
`styles.css`, then place that font name in `--site-font`. A system font is
faster and works offline.

## Cards and highlighted sections

Reusable classes are defined in `styles.css`. Use them in any `.qmd` page:

```markdown
::: {.site-card}
### Notebook title

Short description and [open notebook](content/python-basic/example.ipynb).
:::

::: {.site-highlight}
Important course announcement.
:::
```

To arrange cards responsively:

```markdown
::: {.grid}
::: {.g-col-12 .g-col-md-6 .site-card}
First card
:::
::: {.g-col-12 .g-col-md-6 .site-card}
Second card
:::
:::
```

## Page-local styling

Normal HTML pages receive `styles.css` from `_quarto.yml`. Pages using the
custom `live-html` format name the stylesheet in their own YAML headers. For a
page inside a subdirectory, use the appropriate relative path such as
`../styles.css`.

## Preview changes

```bash
uv sync
./scripts/render-local.sh
uv run python -m http.server 8000 --directory _site
```

Then open `http://localhost:8000/`. Hard-refresh the browser after CSS changes
if it still shows an older cached style.
