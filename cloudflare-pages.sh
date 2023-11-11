#!/usr/bin/env bash

set -ex

python -V
python -m pip install --upgrade pip
python -m pip install --upgrade --user wheel
python -m pip install --user pdm
python -m pdm sync
python -m pdm run mkdocs build
