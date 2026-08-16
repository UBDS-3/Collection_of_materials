# Publish new teaching materials

This repository publishes notebooks, lessons, lectures, and supporting datasets
to GitHub Pages. You can submit material entirely through GitHub's browser; a
local clone is not required.

## Add material without cloning

1. Open the repository on GitHub and choose the destination folder under
   `content/`:

   | Material | Folder |
   | --- | --- |
   | R basics | `content/r-basic/` |
   | Python basics | `content/python-basic/` |
   | Advanced lessons | `content/advanced/` |
   | Lectures and slides | `content/lectures/` |
   | Research highlights | `content/research-highlights/` |
   | Other materials | `content/post-school-materials/` |

2. Select **Add file -> Upload files** and upload the source file and any
   supporting images or data.
3. Select **Create a new branch and start a pull request or commit directly to main**.
4. Describe the material, its audience, required packages, and whether it is
   intended to run in the browser.
5. After merge or direct commit, GitHub
   Actions regenerates live pages, rebuilds navigation, renders the site, and
   deploys GitHub Pages.

If you do not have write access, use **Fork this repository** first and open a
pull request from the fork. The same workflow works entirely in the browser.

Supported source formats are `.qmd`, `.Rmd`, `.rmd`, and `.ipynb`. Existing
`.html`, `.pdf`, and `.pptx` files are copied and linked through the site.
Use a clear filename and provide a title:

- QMD/R Markdown: add `title:` to the YAML front matter.
- Jupyter: set `metadata.quarto.title` or start with a Markdown `#` heading.

Submit only material you have permission
to redistribute.

## Prepare a notebook for browser execution

Browser execution is opt-in. A notebook is converted to Quarto Live only after
its repository-relative path is added to `browser-executable.toml` by the
author or a maintainer. Design the notebook for Pyodide (Python) or WebR (R)
from the beginning:

### Use portable code

- Select a Python or R kernel and keep the language consistent.
- Use packages available in Pyodide/WebR; prefer standard-library code and
  common packages such as NumPy, pandas, Matplotlib, and base R.
- Avoid shell commands, `subprocess`, operating-system-specific paths,
  compiled/native packages, GPU libraries, external services, and code that
  writes to a local disk.
- Make cells run in order without hidden state. Keep examples small enough to
  load quickly in a browser.
- Use relative paths in the source notebook for ordinary local rendering, and
  plan a browser-compatible fetch for every dataset.

### Load data over HTTP in browser cells

Browser runtimes cannot reliably open a repository file with a local path such
as `data/example.csv`. Publish small, redistributable data under `data/` or
`datasets/`, then load it from the deployed site.

Python/Pyodide example:

```python
import io
import pandas as pd
from pyodide.http import pyfetch

response = await pyfetch(
    "https://<org>.github.io/<repo>/content/python-basic/data/example.csv"
)
df = pd.read_csv(io.StringIO(await response.string()))
```

R/WebR example:

```r
df <- read.csv(
  "https://<org>.github.io/<repo>/content/r-basic/data/example.csv"
)
```

Replace `<org>`, `<repo>`, and the path with the actual published location.
See [DATASETS.md](DATASETS.md) for the repository's size limits and additional
fetch examples.

### Mark a notebook for browser conversion

Add the repository-relative source path to `browser-executable.toml`:

```toml
include = [
  "content/python-basic/my-lesson.ipynb",
]
```

For QMD or R Markdown, write ordinary source chunks such as ````{python}````
or ````{r}```` in the original file. Do not replace them manually with
`{pyodide}` or `{webr}`; the generator applies that conversion only to the
allowlisted browser copy.

For a Python notebook, the generated copy uses `{pyodide}` cells; for an R
notebook, it uses `{webr}` cells. The original notebook is never modified.
Warnings about unsupported imports, local data paths, or system calls are
recorded in `generated-live/manifest.json` and must be resolved before calling
the notebook browser-executable.

### Check before submitting

Run the generators if you have a local Quarto/Python environment:

```bash
python scripts/generate-live-pages.py
python scripts/generate-navigation.py
```

Then render the generated page and test every **Run Code** cell in a browser.
If you cannot run the checks locally, mention that in the pull request so the
maintainer can test it in CI.

## Additional reference guides

- [Detailed repository guide](README-DETAILS.md)
- [Contributor and browser-upload instructions](CONTRIBUTING.md)
- [Browser execution details](BROWSER_EXECUTION.md)
- [Dataset conventions and limits](DATASETS.md)
