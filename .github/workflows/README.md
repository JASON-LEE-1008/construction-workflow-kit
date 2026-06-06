# GitHub Workflows

This directory contains GitHub Actions workflows.

The local project checks are:

```bash
python -m ruff check .
python -m ruff format --check .
python -m pytest -q
python -m build
python -m twine check dist/*
```

The `ci.yml` workflow runs the same checks on pushes to `main` and on pull
requests.
