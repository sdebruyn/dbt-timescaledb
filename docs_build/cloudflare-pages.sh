#!/usr/bin/env bash

set -ex

cd ..
python -m pdm install -x --no-default --no-editable -G docs
python -m pdm run mkdocs build -d ./docs_build/site
