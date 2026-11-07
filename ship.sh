#!/usr/bin/env bash
# One-command deploy from this Mac:  ./ship.sh
#   1. runs the tests and stops if they fail
#   2. pushes mobile-first to GitHub
#   3. copies that commit into /home/deploy/sarathi on the server and runs ./deploy.sh
#   4. checks the live site answers and serves the new CSS fingerprint
# Stops at the first problem. Nothing on the server is touched until the tests pass and the push works.
set -euo pipefail

SERVER="${SERVER:-deploy@50.6.226.244}"
REMOTE_DIR="${REMOTE_DIR:-/home/deploy/sarathi}"
BRANCH="mobile-first"
SITE="${SITE:-https://sarathi.dhirajmakam.com}"

cd "$(dirname "$0")"

echo "== 1. Checking the local branch"
[ "$(git rev-parse --abbrev-ref HEAD)" = "$BRANCH" ] || { echo "Switch to $BRANCH first." >&2; exit 1; }
if [ -n "$(git status --porcelain)" ]; then
  echo "There are uncommitted changes. Commit them first so the server gets the same code:" >&2
  git status --short >&2; exit 1
fi

echo "== 2. Running the tests"
./run-tests.sh || { echo "Tests failed; see tests/last-report.txt. Nothing was deployed." >&2; exit 1; }

echo "== 3. Pushing $BRANCH to GitHub"
git push origin "$BRANCH"
COMMIT="$(git rev-parse --short HEAD)"

echo "== 4. Copying $COMMIT to the server and deploying"
# The server copy is a plain folder (not a git clone). We stream this commit's files into it;
# files that are not in git (server/model-int8.pt) are left alone.
ssh -o BatchMode=yes "$SERVER" "test -w '$REMOTE_DIR' && test -w '$REMOTE_DIR/assets'" \
  || { echo "$REMOTE_DIR on the server is not writable by the deploy user (see CLAUDE.md)." >&2; exit 1; }
git archive --format=tar HEAD | ssh -o BatchMode=yes "$SERVER" \
  "set -e; cd '$REMOTE_DIR'; tar -x -f -; echo '$COMMIT' > .deployed-commit; ./deploy.sh"

echo "== 5. Checking the live site"
code="$(curl -s -o /dev/null -w '%{http_code}' "$SITE/")"
echo "$SITE/ answered $code"
[ "$code" = 200 ] || { echo "The site did not answer 200." >&2; exit 1; }
curl -s "$SITE/" | grep -o 'app\.css?v=[0-9a-f]*' | head -1 | sed 's/^/Live stylesheet: /'
echo "Deployed $COMMIT."
