# FlowPilot-CLI Makefile

.PHONY: help install install-dev test test-cov lint format clean build publish

help:
	@echo "FlowPilot-CLI - Available Commands:"
	@echo ""
	@echo "  make install      - Install package"
	@echo "  make install-dev  - Install package with dev dependencies"
	@echo "  make test         - Run tests"
	@echo "  make test-cov     - Run tests with coverage"
	@echo "  make lint         - Run linting"
	@echo "  make format       - Format code with black"
	@echo "  make clean        - Clean build artifacts"
	@echo "  make build        - Build package"
	@echo "  make publish      - Publish to PyPI"
	@echo ""

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"
	pip install -r requirements-dev.txt

test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=flowpilot --cov-report=html --cov-report=term

lint:
	flake8 flowpilot/ --max-line-length=100
	mypy flowpilot/ --ignore-missing-imports

format:
	black flowpilot/ tests/ --line-length=100

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

publish: build
	twine upload dist/*

# Development shortcuts
run-example:
	flowpilot run examples/basic.yml

validate-example:
	flowpilot validate examples/basic.yml

init-example:
	flowpilot init my-workflow -t basic
