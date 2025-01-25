#!/usr/bin/env bash

set -e
set -x

mypy src
ruff check src tests
ruff format src tests --check
