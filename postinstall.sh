#!/usr/bin/env bash
set -euo pipefail

# Install backend dependencies for Render build.
pip install -r requirements.txt

# Optionally build the frontend if needed in the future.
# Uncomment the following lines to produce a static bundle under frontend/dist.
# pushd frontend
# npm install
# npm run build
# popd
