# Browser-executable notebooks

Browser execution is deliberately opt-in. The build reads
`browser-executable.toml` and only notebooks listed in `include` are converted
to Quarto Live cells backed by Pyodide or WebR.

All other notebooks are still published as ordinary HTML pages with their code
visible, but they do not promise in-browser execution. This is appropriate for
notebooks that depend on local files, native Python packages, external services,
or writing files to disk.

To enable a notebook, add its repository-relative path to `include`, regenerate
the pages, and test it in a browser:

```powershell
python scripts/generate-live-pages.py
python scripts/generate-navigation.py
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/render-local.ps1 generated-live/content/python-basic
```

Start with small, self-contained notebooks. If a notebook imports a package or
dataset that Pyodide does not provide, leave it out of the allowlist until the
code is adapted.

The advanced neural-network notebooks are currently static because they depend
on PyTorch/torchvision, local datasets, or large image trees that are not
browser-compatible in their current form.
