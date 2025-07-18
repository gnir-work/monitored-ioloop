# Monitored IO Loop Repository Guide

## Project Overview
This is a Python library that provides production-ready monitored IO loops for Python applications. It wraps asyncio and uvloop event loops to provide monitoring capabilities, helping developers identify performance bottlenecks in their event loop execution.

## Key Features
- Monitor asyncio and uvloop event loops
- Track callback execution times, loop lag, and handle counts
- Minimal performance impact
- Support for FastAPI integration
- Prometheus metrics support

## Repository Structure

### Core Library (`monitored_ioloop/`)
- `__init__.py` - Main package initialization
- `monitored_asyncio.py` - AsyncIO event loop monitoring implementation
- `monitored_uvloop.py` - UVLoop event loop monitoring implementation  
- `monitored_ioloop_base.py` - Base monitoring functionality
- `monitoring.py` - Core monitoring state and data structures
- `exceptions.py` - Custom exceptions
- `formatting_utils.py` - Utility functions for formatting
- `helpers/` - Integration helpers (FastAPI support)
- `py.typed` - Type annotations marker

### Examples (`examples/`)
- `fastapi_with_prometheus/` - FastAPI + Prometheus integration example
- `simple_python_example/` - Basic usage example

### Tests (`tests/`)
- `test_asyncio_profiler.py` - Core asyncio profiler tests
- `helpers/test_fastapi.py` - FastAPI integration tests
- `conftest.py` - Test configuration and fixtures
- `utils.py` - Test utilities

### Performance Testing (`stress_tests/`)
- `locustfile.py` - Load testing with Locust
- `server/` - Test server implementations
- `results/` - Benchmark results and analysis

## Development Environment

### Package Manager
- **uv** (migrated from poetry) - Modern Python package manager
- Configuration in `pyproject.toml`
- Lock file: `uv.lock`

### Python Version
- Requires Python ~3.9

### Dependencies
- **Core**: `wrapt>=1.17.2,<2`
- **Optional**: `uvloop>=0.19.0,<0.20` (for uvloop support)
- **FastAPI**: `fastapi>=0.115.7,<0.116` (for FastAPI integration)

### Development Dependencies
- **Testing**: pytest, pytest-cov, pytest-xdist, pytest-repeat, httpx
- **Code Quality**: mypy, ruff
- **Debugging**: ipython, ipdb
- **Load Testing**: locust, uvicorn, click
- **Examples**: fastapi, prometheus-client

## Common Commands

### Installation
```bash
make install                    # Install all dependencies
```

### Code Quality
```bash
make pre-commit                 # Format + lint (pre-commit hook)
```

### Testing
```bash
make test                       # Run tests with coverage
make test-for-flakiness         # Run tests 10 times to check for flakiness
```
## Code Quality Standards

### Type Checking (mypy.ini)
- Strict typing enabled
- Disallow untyped definitions
- Check for incomplete definitions
- Warn about unused ignores and redundant casts

### Formatting & Linting
- **ruff** for formatting and linting
- **mypy** for static type analysis
- All code must pass both checks

### Testing
- **pytest** with coverage reporting
- Parallel test execution with pytest-xdist
- Repeat testing for flakiness detection

## Key Files to Understand

1. **monitored_ioloop/monitoring.py** - Core monitoring state (`IoLoopMonitorState`)
2. **monitored_ioloop/monitored_asyncio.py** - AsyncIO event loop policy implementation
3. **monitored_ioloop/monitored_uvloop.py** - UVLoop event loop policy implementation
4. **examples/fastapi_with_prometheus/** - Real-world usage example
5. **tests/test_asyncio_profiler.py** - Core functionality tests

## Performance Considerations
- Minimal overhead monitoring implementation
- Benchmarks available in `stress_tests/results/`
- Performance impact is negligible for most use cases

## Release Information
- Current version: 0.0.14
- Published to PyPI as `monitored_ioloop`
- GitHub Actions workflow for CI/CD

## Git Workflow
- Main branch: `main`
- Feature branches start with feature/
- Bug branches start with bugfix/