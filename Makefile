.PHONY: test test-verbose test-coverage install install-dev clean

# Run tests
test:
	python -m pytest

# Run tests with verbose output
test-verbose:
	python -m pytest -vv

# Run tests with coverage report
test-coverage:
	python -m pytest --cov=claude_agent_environment --cov-report=term-missing

# Install package in development mode
install:
	pip install -e .

# Install package with test dependencies
install-dev:
	pip install -e ".[dev]"

# Clean up generated files
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -f test_*.py