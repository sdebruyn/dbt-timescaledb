#!/usr/bin/env bash

set -ex

echo "Build started on `date`"
cd ..

python -V
python -m pip install --upgrade pip
python -m pip install --upgrade --user wheel
python -m pip install --user pdm
python -m pdm install -x --no-default --no-editable -G docs
python -m pdm run mkdocs build
