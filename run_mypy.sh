#!/bin/sh

MYPYPATH=stubs mypy --check-untyped-defs rdfdb/*.py
