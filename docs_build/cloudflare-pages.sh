#!/usr/bin/env bash

set -ex

cd ..
python -m pdm install -x --no-default --no-editable -G docs
python -m pdm run mkdocs build -d ./docs_build/site

curl -sLo ./docs_build/site/t1.js "https://cdn.jsdelivr.net/gh/Swetrix/swetrix-js@latest/dist/swetrix.js"
curl -sLo ./docs_build/site/t1.js.map "https://cdn.jsdelivr.net/gh/Swetrix/swetrix-js@latest/dist/swetrix.js.map"
curl -sLo ./docs_build/site/t2.js "https://umami.debruyn.dev/script.js"
