#!/usr/bin/env bash

set -ex

python -V
python -m pip install --upgrade pip
python -m pip install --upgrade --user wheel
python -m pip install --user pdm
python -m pdm install -x --no-editable -dG docs
python -m pdm run mkdocs build
