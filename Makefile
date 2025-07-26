# HerpAI-Lib Makefile

# Variables
PYTHON := python3
VENV_NAME := venv
VENV_BIN := $(VENV_NAME)/bin
VENV_ACTIVATE := $(VENV_BIN)/activate
PYTHON_VERSION := 3.9
PACKAGE_NAME := openbiocure_corelib
GITHUB_USERNAME := openbiocure
GITHUB_REPO := HerpAI-Lib

# Test and coverage settings
TESTS_DIR := tests
openbiocure_corelib_DIR := openbiocure_corelib
COVERAGE_OPTIONS := --cov=$(openbiocure_corelib_DIR) --cov-report=term-missing

# OS specific commands
ifeq ($(OS),Windows_NT)
	VENV_BIN := $(VENV_NAME)/Scripts
	VENV_ACTIVATE := $(VENV_BIN)/activate
	PYTHON := python
	# Handle path separators for Windows
	SEP := \\
else
	SEP := /
endif

# Define command prefix to activate virtualenv before running commands
VENV_RUN := . $(VENV_ACTIVATE) &&

# Colors for terminal output
BLUE := \033[0;34m
GREEN := \033[0;32m
RED := \033[0;31m
YELLOW := \033[0;33m
NC := \033[0m # No Color

.PHONY: all clean test lint format help venv install dev-install build publish check init ci ci-test

# Default target
all: help

##@ General
help: ## Display this help message
	@awk 'BEGIN {FS = ":.*##"; printf "$(BLUE)Usage:$(NC)\n  make $(GREEN)<target>$(NC)\n\n$(BLUE)Targets:$(NC)\n"} \
		/^[a-zA-Z0-9_-]+:.*?##/ { printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2 } \
		/^##@/ { printf "\n$(YELLOW)%s$(NC)\n", substr($$0, 5) }' $(MAKEFILE_LIST)

##@ Development Environment
venv: ## Create virtual environment
	@echo "$(BLUE)Creating virtual environment...$(NC)"
	$(PYTHON) -m venv $(VENV_NAME)
	@echo "$(GREEN)Virtual environment created at $(VENV_NAME)/$(NC)"
	@echo "$(YELLOW)To activate, run: source $(VENV_ACTIVATE)$(NC)"

install: check-venv ## Install package in development mode
	@echo "$(BLUE)Installing package...$(NC)"
	$(VENV_RUN) pip install -e .
	@echo "$(GREEN)Installation complete.$(NC)"

dev-install: check-venv ## Install package with development dependencies
	@echo "$(BLUE)Installing package with development dependencies...$(NC)"
	$(VENV_RUN) pip install -e ".[dev]"
	@echo "$(GREEN)Development installation complete.$(NC)"

init: dev-install ## Initialize development environment with pre-commit hooks
	@echo "$(BLUE)Setting up pre-commit hooks...$(NC)"
	$(VENV_RUN) pre-commit install
	@echo "$(GREEN)Development environment initialized.$(NC)"

##@ Testing and Quality
test: check-venv ## Run tests with coverage
	@echo "$(BLUE)Running tests...$(NC)"
	$(VENV_RUN) pytest $(TESTS_DIR) -v $(COVERAGE_OPTIONS)

ci-test: check-venv ## Run tests in CI mode
	@echo "$(BLUE)Running tests in CI mode...$(NC)"
	CI=true $(VENV_RUN) pytest $(TESTS_DIR) -v $(COVERAGE_OPTIONS)

lint: check-venv ## Run code linters (flake8 only)
	@echo "$(BLUE)Running linters...$(NC)"
	$(VENV_RUN) flake8 $(openbiocure_corelib_DIR) $(TESTS_DIR)
	$(VENV_RUN) black --check $(openbiocure_corelib_DIR) $(TESTS_DIR)
	$(VENV_RUN) isort --check-only $(openbiocure_corelib_DIR) $(TESTS_DIR)

lint-full: check-venv ## Run all linters including mypy
	@echo "$(BLUE)Running all linters...$(NC)"
	$(VENV_RUN) flake8 $(openbiocure_corelib_DIR) $(TESTS_DIR)
	$(VENV_RUN) mypy $(openbiocure_corelib_DIR) $(TESTS_DIR)
	$(VENV_RUN) black --check $(openbiocure_corelib_DIR) $(TESTS_DIR)
	$(VENV_RUN) isort --check-only $(openbiocure_corelib_DIR) $(TESTS_DIR)

format: check-venv ## Format code with black and isort
	@echo "$(BLUE)Formatting code...$(NC)"
	$(VENV_RUN) black $(openbiocure_corelib_DIR) $(TESTS_DIR)
	$(VENV_RUN) isort $(openbiocure_corelib_DIR) $(TESTS_DIR)

check: lint test ## Run all quality checks (linting and tests)
	@echo "$(GREEN)All checks passed!$(NC)"

##@ CI Simulation
ci: clean venv dev-install ci-test lint ## Simulate CI environment locally
	@echo "$(GREEN)CI simulation completed!$(NC)"

##@ Building and Publishing
build: check-venv ## Build package distributions
	@echo "$(BLUE)Building package...$(NC)"
	$(VENV_RUN) pip install --upgrade build
	$(VENV_RUN) python -m build
	@echo "$(GREEN)Package built successfully.$(NC)"

publish-github: build ## Publish package to GitHub Packages
	@echo "$(BLUE)Publishing to GitHub Packages...$(NC)"
	$(VENV_RUN) pip install --upgrade twine
	$(VENV_RUN) python -m twine upload --repository github dist/*
	@echo "$(GREEN)Package published to GitHub Packages.$(NC)"

publish-test: build ## Publish package to TestPyPI
	@echo "$(BLUE)Publishing to TestPyPI...$(NC)"
	$(VENV_RUN) pip install --upgrade twine
	$(VENV_RUN) python -m twine upload --repository testpypi dist/*
	@echo "$(GREEN)Package published to TestPyPI.$(NC)"

publish-pypi: build ## Publish package to PyPI
	@echo "$(BLUE)Publishing to PyPI...$(NC)"
	$(VENV_RUN) pip install --upgrade twine
	$(VENV_RUN) python -m twine upload dist/*
	@echo "$(GREEN)Package published to PyPI.$(NC)"

##@ Maintenance
clean: ## Clean up build artifacts and virtual environment
	@echo "$(BLUE)Cleaning up...$(NC)"
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf $(VENV_NAME)/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf .mypy_cache/
	rm -rf __pycache__/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "$(GREEN)Cleanup complete.$(NC)"

# Helper targets
check-venv: ## Check if virtual environment exists, create if it doesn't
	@if [ ! -d "$(VENV_NAME)" ]; then \
		echo "$(RED)Virtual environment not found. Creating one...$(NC)"; \
		$(MAKE) venv; \
	fi
