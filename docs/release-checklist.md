# Release Checklist

Use this checklist before tagging or publishing a release.

## Repository readiness

- Confirm `README.md`, `LICENSE`, `CONTRIBUTING.md`, `CHANGELOG.md`, and
  `SECURITY.md` are present.
- Confirm issue templates and the pull request template are present.
- Confirm examples use synthetic data only.
- Confirm the changelog includes the release version and date.

## Local validation

Run the checks from a clean working tree:

```bash
python -m pip install -e ".[dev]"
python -m ruff check .
python -m ruff format --check .
python -m pytest -q
python -m construction_workflow_kit examples/sample_project.json --validate-only --strict
python -m construction_workflow_kit examples/sample_project.json --summary-output examples/sample_project_summary.json --output examples/sample_project_report.md
python -m build
python -m twine check dist/*
```

## Manual smoke test

```bash
python -m construction_workflow_kit examples/sample_project.json --output examples/sample_project_report.md
```

Confirm the generated Markdown contains:

- project snapshot
- cost review summary
- meeting notes
- technical material register
- action register
- validation notes

## Tagging

For version `0.2.0`, use:

```bash
git tag -a v0.2.0 -m "Release v0.2.0"
git push origin v0.2.0
```

## Package publishing preflight

This project is not yet configured for automatic package publishing. Before any
public package upload, confirm the package name, distribution metadata, built
artifacts, and generated report examples are still appropriate for public reuse.
