# GitHub Workflows

This directory is reserved for GitHub Actions workflows.

The local project checks are:

```bash
python -m ruff check .
python -m ruff format --check .
python -m pytest -q
```

A CI workflow can be added after the repository token used for publishing has
permission to create or update GitHub Actions workflow files.
