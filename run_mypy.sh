#!/bin/sh

# see light9 for a flake8 alternative
pyflakes rdfdb/*.py
MYPYPATH=stubs mypy --check-untyped-defs rdfdb/*.py
