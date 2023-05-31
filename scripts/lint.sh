#!/usr/bin/env bash

set -e
set -x

mypy src
ruff src tests
black src tests --check
