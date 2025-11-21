#!/usr/bin/env bash
set -euo pipefail

python3 -m pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright browsers without attempting system-level package installs
# Render builds run without sudo, so avoid --with-deps to prevent failures.
PLAYWRIGHT_BROWSERS_PATH=${PLAYWRIGHT_BROWSERS_PATH:-/tmp/playwright-browsers}
export PLAYWRIGHT_BROWSERS_PATH
python -m playwright install chromium || true

pushd frontend
npm install
npm run build
popd

rm -rf static
mkdir -p static
cp -r frontend/dist/* static/
