#!/bin/sh

pyflakes rdfdb/*.py
MYPYPATH=stubs mypy --check-untyped-defs rdfdb/*.py
