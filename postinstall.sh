#!/usr/bin/env bash
set -euo pipefail

python3 -m pip install --upgrade pip
pip install -r requirements.txt

# Install playwright browsers if missing
python -m playwright install chromium --with-deps || true

pushd frontend
npm install
npm run build
popd

rm -rf static
mkdir -p static
cp -r frontend/dist/* static/
