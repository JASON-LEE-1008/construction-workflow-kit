# GitHub Workflows

This directory contains GitHub Actions workflows.

The local project checks are:

```bash
python -m ruff check .
python -m ruff format --check .
python -m pytest -q
```

The `ci.yml` workflow runs the same checks on pushes to `main` and on pull
requests.
