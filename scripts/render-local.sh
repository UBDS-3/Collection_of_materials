#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$PROJECT_DIR"

if [[ ! -x .venv/bin/python ]]; then
  echo "Missing .venv. Create it and install requirements first:" >&2
  echo "  uv venv .venv" >&2
  echo "  uv pip install --python .venv/bin/python -r requirements.txt" >&2
  exit 1
fi

mkdir -p .cache/ipython .cache/jupyter .cache/matplotlib \
  .local/share/quarto/logs .tmp/jupyter-runtime

export XDG_CACHE_HOME="$PROJECT_DIR/.cache"
export XDG_DATA_HOME="$PROJECT_DIR/.local/share"
export IPYTHONDIR="$PROJECT_DIR/.cache/ipython"
export JUPYTER_CONFIG_DIR="$PROJECT_DIR/.cache/jupyter"
export JUPYTER_RUNTIME_DIR="$PROJECT_DIR/.tmp/jupyter-runtime"
export MPLCONFIGDIR="$PROJECT_DIR/.cache/matplotlib"
export QUARTO_PYTHON="$PROJECT_DIR/.venv/bin/python"

exec quarto render "$@"
