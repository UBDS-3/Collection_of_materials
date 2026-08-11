# Publishing datasets with teaching material

Small datasets can be committed and served by GitHub Pages alongside the
notebooks that use them.

## Where to put a dataset

Use either layout:

```text
datasets/
  penguins.csv                 # shared by several lessons

content/python-basic/
  practical.ipynb
  data/
    survey.csv                 # used only by this lesson
```

Every file below `datasets/` and every file below a lesson's `data/` directory
is copied unchanged into the published site. `data/` is deliberately ignored by
the navigation generator, so datasets never appear as lesson pages.

For normal Quarto/R Markdown/Jupyter rendering, use a path relative to the
source document, for example `data/survey.csv` for a notebook stored beside the
`data/` directory. This keeps the source reproducible after cloning the
repository.

## Size limits

The build checks every published dataset. The defaults are **20 MiB per file**
and **100 MiB in total**. They keep GitHub Pages builds and browser-based R/Python
sessions responsive; the data must be downloaded into each reader's browser.

To deliberately use different limits in a local build or GitHub Actions, set
`DATASET_MAX_FILE_MB` and/or `DATASET_MAX_TOTAL_MB` to positive whole-number
MiB values. Prefer a sampled or compressed teaching extract when a data file is
larger than the default cap. Do not commit credentials, personal data, or data
that cannot be redistributed.

## Browser-executable notebook copies

The generated Quarto Live copies execute inside WebAssembly, not on the server.
They cannot open a notebook's local `data/survey.csv` path directly. Fetch the
published data over HTTP instead. A reliable pattern is to use the site's
published URL (shown in the browser address bar) plus the file path; for this
repository, a lesson dataset is at:

```text
https://ubds-3.github.io/Collection_of_materials/content/python-basic/data/survey.csv
```

In a Python/Pyodide cell:

```python
import io
import pandas as pd
from pyodide.http import pyfetch

response = await pyfetch(
    "https://ubds-3.github.io/Collection_of_materials/content/python-basic/data/survey.csv"
)
survey = pd.read_csv(io.StringIO(await response.string()))
```

In an R/WebR cell, use the same published URL:

```r
survey <- read.csv(
  "https://ubds-3.github.io/Collection_of_materials/content/python-basic/data/survey.csv"
)
```

Keep the local `data/survey.csv` form for normal notebook rendering if desired,
and use the fetch form in the browser-executable version. The build records a
clear warning in `generated-live/manifest.json` whenever it finds a conventional
`data/...` reference in a live copy.
