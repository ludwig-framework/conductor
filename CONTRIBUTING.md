# Contributing to Conductor

We welcome contributions of all kinds: bug fixes, new provider integrations, documentation enhancements, examples, and feedback!

---

## Development Setup

1. **Fork and Clone the Repository**

   ```bash
   git clone https://github.com/ludwig-framework/conductor.git
   cd conductor
   ```

2. **Create a Virtual Environment**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install Dependencies in Editable Mode**

   ```bash
   pip install --upgrade pip
   pip install -e ".[dev]"
   ```

---

## Running Tests

Run the full test suite locally:

```bash
pytest
```

Run tests with verbose output:

```bash
pytest tests/ -v
```

---

## Code Quality and Style

Conductor adheres to PEP 8 standards with formatting and linting powered by [Ruff](https://github.com/astral-sh/ruff) and [Black](https://github.com/psf/black).

Check for lint and code style issues:

```bash
ruff check conductor/ tests/
black --check conductor/ tests/
```

Auto-format code:

```bash
ruff check --fix conductor/ tests/
black conductor/ tests/
```

---

## Pull Request Guidelines

1. **Branch Naming**: Use descriptive branch names (`feat/add-groq-provider`, `fix/memory-ttl-expiry`, `docs/update-readme`).
2. **Commit Messages**: Write clear, imperative commit messages describing what changed and why.
3. **Tests**: When introducing new functionality or fixing a bug, add or update tests in `tests/`.
4. **Documentation**: Update docstrings and relevant guides in `docs/` when changing public interfaces.

Thank you for helping make Conductor better for everyone!
