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

The `Materials` and `Slides` menus are generated from their folders before
every local and GitHub Actions render. Configure the sections in
`site-navigation.toml`; do not edit the generated block in `_quarto.yml`.

The recursive glob patterns under `_quarto.yml` → `project.render` render all
supported documents in those folders. You only need to change them when adding
a completely new top-level content folder.

A section looks like this:

```toml
[[section]]
label = "Lectures"
folder = "lectures"
recursive = true
sort = "title"
extensions = [".qmd", ".Rmd", ".rmd", ".ipynb"]
exclude = []
```

The displayed link name comes from the document's YAML `title`. For notebooks,
the generator checks `metadata.quarto.title`, then the first Markdown level-one
heading, and finally uses a cleaned-up filename.

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

Short description and [open notebook](materials/example.ipynb).
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
