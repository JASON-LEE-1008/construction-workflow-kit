# Contributing

This is an early-stage open source project for construction management workflow
helpers. Contributions should stay practical, testable, and safe for public
reuse.

## Useful contributions

- Add tests for report generation behavior.
- Improve example data with clearly fake project names.
- Add small workflow helpers for cost review, meeting notes, or technical
  document registers.
- Improve documentation for repeatable construction management tasks.

## Data safety

Do not add private project names, real client names, internal company names,
contract values from live work, personal contact details, or confidential
technical material. Use synthetic examples such as `Example Public Works Agency`
or `Sample Riverfront Access Road`.

## Local checks

```bash
python -m pytest -q
python -m ruff check .
```

## Pull requests

Keep pull requests focused. Include a short explanation of the workflow problem,
the proposed behavior, and the tests or manual checks used to verify it.
