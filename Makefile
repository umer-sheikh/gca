PYTHON ?= python3
VENV ?= .venv
PIP := $(VENV)/bin/pip
PY := $(VENV)/bin/python

.PHONY: venv install install-all test lint run benchmark

venv:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install -U pip wheel setuptools

install: venv
	$(PIP) install -e .[dev]

install-all: venv
	$(PIP) install -e .[dev,remote,audio]

test:
	$(PY) -m pytest

lint:
	$(PY) -m ruff check src tests

run:
	$(PY) -m gulf_climate_agent.cli.run --help

benchmark:
	$(PY) -m gulf_climate_agent.cli.benchmark --help
