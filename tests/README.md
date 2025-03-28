# HerpAI-Lib Tests

This directory contains tests for HerpAI-Lib.

## Running Tests

To run all tests:

```bash
pytest
```

To run a specific test file:

```bash
pytest tests/unit/test_engine.py
```

To run a specific test function:

```bash
pytest tests/unit/test_engine.py::test_engine_singleton
```

## Test Structure

- `unit/` - Unit tests for individual components
- `integration/` - Integration tests combining multiple components
- `mocks/` - Mock implementations used for testing
- `conftest.py` - Shared pytest fixtures
- `test_smoke.py` - Basic smoke tests

## Test Database

Most tests use an in-memory SQLite database for testing, which is created and destroyed during the test. The database is configured automatically by the test fixtures.
