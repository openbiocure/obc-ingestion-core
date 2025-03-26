# HerpAI-Lib

[![Makefile CI](https://github.com/openbiocure/HerpAI-Lib/actions/workflows/makefile.yml/badge.svg)](https://github.com/openbiocure/HerpAI-Lib/actions/workflows/makefile.yml)

**HerpAI-Lib** is the foundational core library for the [HerpAI](https://github.com/openbiocure/HerpAI) platform. It provides shared infrastructure components, configuration management, logging utilities, database session handling, and the repository pattern used across HerpAI agents and services.

---

## 📦 Features

- 🧠 Typed configuration with YAML and dataclasses
- 🪵 Standardized structured logging
- 🗃️ SQLAlchemy session and BaseModel setup
- 🧱 Abstract repository pattern (BaseRepository)
- 🧰 Common utility functions and exceptions
- ✅ Compatible with `dotenv` for local environment management

---

## 📁 Folder Structure

```
./
├── configuration/         # Config loaders (AppConfig, AgentConfig)
├── infrastructure/        # Logging and DB setup
│   └── db/
├── repository/            # BaseRepository
├── schemas/               # Pydantic models or shared DTOs
├── utils/                 # Error handling, helpers
├── types.py               # Type aliases and constants
├── cli.py                 # Optional CLI entrypoint
├── __version__.py         # Library version
```

---

## 🚀 Getting Started

```bash
pip install -e .
```

Then in your project:

```python
from infrastructure.logger import get_logger
from configuration.app_config import AppConfig
from infrastructure.db.session import get_session
from repository.base import BaseRepository
```

---

## 🧪 Requirements

- Python 3.9+
- SQLAlchemy
- PyYAML
- python-dotenv

---

## 📝 License

This library is released under the MIT License as part of the OpenBioCure initiative.
