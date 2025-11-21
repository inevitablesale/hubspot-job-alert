#!/usr/bin/env bash
set -euo pipefail

python3 -m pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright browsers without attempting system-level package installs.
# We install into a project-local directory so the artifacts are present in the
# final deploy image instead of ephemeral /tmp storage.
PLAYWRIGHT_BROWSERS_PATH=${PLAYWRIGHT_BROWSERS_PATH:-$(pwd)/.playwright-browsers}
export PLAYWRIGHT_BROWSERS_PATH
python -m playwright install chromium || true

pushd frontend
npm install
npm run build
popd

rm -rf static
mkdir -p static
cp -r frontend/dist/* static/
