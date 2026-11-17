#!/usr/bin/env bash

set -ex

cd "$(dirname "$0")/.."
python -m uv sync --locked --only-group docs --no-install-project
python -m uv run --no-sync mkdocs build -d ./docs_build/site

curl -sLo ./docs_build/site/t.js "https://umami.debruyn.dev/script.js"
