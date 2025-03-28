# Variables
PYTHON := python3
VENV_NAME := venv
VENV_ACTIVATE := $(VENV_NAME)/bin/activate
PYTHON_VERSION := 3.9
PACKAGE_NAME := herpai-lib
GITHUB_USERNAME := openbiocure
GITHUB_REPO := herpai-lib

# OS specific commands
ifeq ($(OS),Windows_NT)
	VENV_ACTIVATE := $(VENV_NAME)/Scripts/activate
	PYTHON := python
endif

# Colors for terminal output
BLUE := \033[0;34m
GREEN := \033[0;32m
RED := \033[0;31m
YELLOW := \033[0;33m
NC := \033[0m # No Color

.PHONY: all clean test lint format help venv install dev-install build publish publish-github publish-test publish-pypi

# Default target
all: help

help:
	@echo "$(BLUE)Available commands:$(NC)"
	@echo "$(GREEN)make venv$(NC) - Create virtual environment"
	@echo "$(GREEN)make install$(NC) - Install package"
	@echo "$(GREEN)make dev-install$(NC) - Install package with development dependencies"
	@echo "$(GREEN)make test$(NC) - Run tests"
	@echo "$(GREEN)make lint$(NC) - Run linting"
	@echo "$(GREEN)make format$(NC) - Format code"
	@echo "$(GREEN)make clean$(NC) - Clean up build artifacts and virtual environment"

venv:
	@echo "$(BLUE)Creating virtual environment...$(NC)"
	$(PYTHON) -m venv $(VENV_NAME)
	@echo "$(GREEN)Virtual environment created.$(NC)"
	@echo "$(YELLOW)To activate, run: source $(VENV_ACTIVATE)$(NC)"

install: venv
	@echo "$(BLUE)Installing package...$(NC)"
	. $(VENV_ACTIVATE) && pip install -e .
	@echo "$(GREEN)Installation complete.$(NC)"

dev-install: venv
	@echo "$(BLUE)Installing package with development dependencies...$(NC)"
	. $(VENV_ACTIVATE) && pip install -e ".[dev]"
	@echo "$(GREEN)Development installation complete.$(NC)"

test:
	@echo "$(BLUE)Running tests...$(NC)"
	. $(VENV_ACTIVATE) && pytest tests/ -v --cov=src --cov-report=term-missing

lint:
	@echo "$(BLUE)Running linters...$(NC)"
	. $(VENV_ACTIVATE) && flake8 src tests
	. $(VENV_ACTIVATE) && mypy src tests
	. $(VENV_ACTIVATE) && black --check src tests
	. $(VENV_ACTIVATE) && isort --check-only src tests

format:
	@echo "$(BLUE)Formatting code...$(NC)"
	. $(VENV_ACTIVATE) && black src tests
	. $(VENV_ACTIVATE) && isort src tests

clean:
	@echo "$(BLUE)Cleaning up...$(NC)"
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf $(VENV_NAME)/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf .mypy_cache/
	rm -rf __pycache__/
	rm -rf src/__pycache__/
	rm -rf tests/__pycache__/
	@echo "$(GREEN)Cleanup complete.$(NC)"

# Check if virtual environment exists
check-venv:
	@if [ ! -d "$(VENV_NAME)" ]; then \
		echo "$(RED)Virtual environment not found. Creating one...$(NC)"; \
		$(MAKE) venv; \
	fi

# Initialize development environment
init: dev-install
	@echo "$(BLUE)Setting up pre-commit hooks...$(NC)"
	. $(VENV_ACTIVATE) && pre-commit install
	@echo "$(GREEN)Development environment initialized.$(NC)"

# Run all quality checks
check: lint test
	@echo "$(GREEN)All checks passed!$(NC)"

build:
	@echo "$(BLUE)Building package...$(NC)"
	. $(VENV_ACTIVATE) && pip install --upgrade build
	. $(VENV_ACTIVATE) && python -m build
	@echo "$(GREEN)Package built successfully.$(NC)"

publish-github: build
	@echo "$(BLUE)Publishing to GitHub Packages...$(NC)"
	. $(VENV_ACTIVATE) && pip install --upgrade twine
	. $(VENV_ACTIVATE) && python -m twine upload --repository github dist/*
	@echo "$(GREEN)Package published to GitHub Packages.$(NC)"

publish-test: build
	@echo "$(BLUE)Publishing to TestPyPI...$(NC)"
	. $(VENV_ACTIVATE) && pip install --upgrade twine
	. $(VENV_ACTIVATE) && python -m twine upload --repository testpypi dist/*
	@echo "$(GREEN)Package published to TestPyPI.$(NC)"

publish-pypi: build
	@echo "$(BLUE)Publishing to PyPI...$(NC)"
	. $(VENV_ACTIVATE) && pip install --upgrade twine
	. $(VENV_ACTIVATE) && python -m twine upload dist/*
	@echo "$(GREEN)Package published to PyPI.$(NC)"