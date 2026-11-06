#!/usr/bin/env bash
# Check every Sarathi feature in a real browser.  Usage:  bash run-tests.sh
# First run downloads a test copy of Chromium (about 150 MB) into the project's .venv.
set -e
cd "$(dirname "$0")"
if [ ! -d .venv ]; then python3 -m venv .venv; fi
. .venv/bin/activate
python -c "import playwright" 2>/dev/null || pip install -q "playwright==1.48.0"
if [ ! -f .venv/.chromium-ok ]; then
  echo "Downloading the test browser (one time, about 150 MB)..."
  PLAYWRIGHT_BROWSERS_PATH="$PWD/.venv/ms-playwright" python -m playwright install chromium && touch .venv/.chromium-ok
fi
export PLAYWRIGHT_BROWSERS_PATH="$PWD/.venv/ms-playwright"
python tests/run_tests.py
