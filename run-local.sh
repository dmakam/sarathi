#!/usr/bin/env bash
# Try Sarathi and the recitation coach on your own computer before deploying.
#   ./run-local.sh        then open http://localhost:8080/practice/2/47/ in Chrome
# Everything installs inside this folder (.venv). No admin rights or Homebrew needed.
# First run: about 2 to 5 minutes and roughly 2 GB of downloads. Later runs start in seconds.
set -euo pipefail
cd "$(dirname "$0")"

command -v python3 >/dev/null || { echo "python3 is missing. On a Mac, run: xcode-select --install"; exit 1; }
command -v git >/dev/null || { echo "git is missing. On a Mac, run: xcode-select --install"; exit 1; }

if [ ! -d .venv ]; then
  echo "== Setting up a private Python environment in .venv"
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
. .venv/bin/activate
if ! python -c "import torch, torchaudio, numpy, imageio_ffmpeg" 2>/dev/null; then
  echo "== Installing the coach's libraries (PyTorch for CPU, about 200 MB)"
  python -m pip install --quiet --upgrade pip
  if [ "$(uname -s)" = "Linux" ]; then
    python -m pip install --quiet torch torchaudio --index-url https://download.pytorch.org/whl/cpu
    python -m pip install --quiet numpy imageio-ffmpeg
  else
    python -m pip install --quiet torch torchaudio numpy imageio-ffmpeg
  fi
fi

if [ ! -f site/index.html ] || [ build/build.py -nt site/index.html ] || [ assets/recite.js -nt site/index.html ]; then
  if [ ! -d src-data ]; then
    echo "== Downloading the public-domain Gita dataset"
    git clone --quiet https://github.com/gita/gita.git src-data
    git -C src-data checkout --quiet c6fce39595445768876ddbb8d1268a9c935e1d2b
  fi
  echo "== Building the site"
  SARATHI_BASE_URL="http://localhost:${PORT:-8080}" python -I build/build.py
fi

echo "== Starting Sarathi"
exec python server/local.py
