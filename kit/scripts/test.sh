#!/bin/bash
# Ensure all deps (including vector search) are installed, then run tests

export PYTHONPATH=src
python -m pytest "$@"
