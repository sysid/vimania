#!/usr/bin/env bash

TARGET_DIR="$(pipenv --where)/pythonx"
SOURCE_DIR="$(pipenv --venv)/lib/python3.9/site-packages/"

pushd "$PROJ_DIR" || exit 1
rsync -avu --exclude '__pycache__' --exclude '_virtualenv*' --exclude '_distutils_hack' --exclude '_pytest' "$SOURCE_DIR" "$TARGET_DIR"
popd || exit 1