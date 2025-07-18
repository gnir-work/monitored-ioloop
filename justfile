target_dir := "."
groups := "dev,stress_test,code_quality,examples"

# Install dependencies with optional groups
install groups=groups:
    #!/usr/bin/env bash
    if [ -n "{{groups}}" ]; then
        uv sync --group $(echo {{groups}} | sed 's/,/ --group /g') --all-extras
    else
        uv sync --all-groups --all-extras
    fi

# Format code using ruff
format target_dir=target_dir:
    uv run ruff format {{target_dir}}
    uv run ruff check --fix --unsafe-fixes {{target_dir}}

# Check code formatting (no fixes)
lint-formatters target_dir=target_dir:
    uv run ruff format --check {{target_dir}}
    uv run ruff check {{target_dir}}

# Run static code analysis with mypy
lint-static-code-analysis target_dir=target_dir:
    uv run mypy {{target_dir}}

# Run all linting checks
lint target_dir=target_dir: (lint-formatters target_dir) (lint-static-code-analysis target_dir)

# Format and lint code (pre-commit hook)
pre-commit target_dir=target_dir: (format target_dir) (lint-static-code-analysis target_dir)

# Run tests with coverage
test:
    uv run pytest --cov=monitored_ioloop -n auto tests

# Run tests multiple times to check for flakiness
test-for-flakiness:
    uv run pytest --cov=monitored_ioloop -n auto --count=10