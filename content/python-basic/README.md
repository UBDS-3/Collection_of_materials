# UBDS^3 2026 Basic-python-2026
Repo for basic Python track of UBDS^3

Basic Python course for UBDS^3 2026, focusing on intro to programming, data types, dataframes, and intro to data science

## Branches

- `main` contains the student-facing course materials.
- `solutions` contains the instructor copy with solved materials.

| Day | Topic |
|-----|-------|
| 1 | Python basics: setup, variables, simple data types, collections, functions, and first OOP ideas |
| 2 | Collections, loops, conditions, functions, NumPy, and BioPython |
| 3 | Writing functions, reading errors, debugging, logging, and organizing code |
| 4 | Pandas, NumPy, data exploration, filtering, groupby, and matplotlib |
| 5 | EDA, statistics, regression, and introductory machine learning |

## Install all practical dependencies with uv

This repository uses one shared `pyproject.toml` and `uv.lock` for all practicals.
Students do not need to install separate day-specific `requirements.txt` files.
Keep `uv.lock` in the repository so everyone gets the same resolved package
versions.

### 1. Install uv

Windows PowerShell:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

macOS with Homebrew:

```bash
brew install uv
```

macOS without Homebrew:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Linux:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

After installing, close and reopen the terminal, then check that `uv` works:

```bash
uv --version
```

### 2. Install everything for the course

From the `Basic-python-2026` folder, run:

```bash
uv sync
```

This creates a local virtual environment in `.venv` and installs Jupyter, BioPython,
NumPy, pandas, matplotlib, SciPy, statsmodels, scikit-learn, seaborn, and pytest.

If a managed lab computer reports a cache permission error, use the repository-local
cache and run the command again:

Windows PowerShell:

```powershell
$env:UV_CACHE_DIR = ".uv-cache"
uv sync
```

macOS/Linux:

```bash
UV_CACHE_DIR=.uv-cache uv sync
```

If you need to recreate or update the lock file, run:

```bash
uv lock
```

### 3. Open the notebooks

Use Jupyter from the uv environment:

```bash
uv run jupyter notebook
```

You can also run tests for the day 3 alignment practical:

```bash
uv run pytest day3/real_alignment/tests
```

If you set `UV_CACHE_DIR` above, keep using the same terminal for these commands.

## Useful uv commands

`uv init` creates a new Python project by adding a `pyproject.toml` file. You do
not need to run it for this repository because the project file is already here.

```bash
uv init
```

`uv add` installs a new package and records it in `pyproject.toml`. Use this if a
new practical needs an extra package.

```bash
uv add package-name
```

For example:

```bash
uv add requests
```

`uv sync` installs everything listed in `pyproject.toml` and `uv.lock` into the
local `.venv` environment.

```bash
uv sync
```

`uv lock` resolves package versions and updates `uv.lock`. Use it after changing
dependencies, then share the updated `uv.lock` with the repository.

```bash
uv lock
```

To run commands inside the uv environment, prefix them with `uv run`:

```bash
uv run python --version
uv run jupyter notebook
```
