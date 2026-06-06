# Construction Workflow Kit

Construction Workflow Kit is an early-stage Python project for turning
structured construction management notes into reusable report drafts.

The current version reads a safe JSON input file and produces a Markdown draft
that summarizes cost review items, meeting notes, technical material status,
and follow-up actions.

This project is intentionally small. It does not claim production readiness,
large adoption, external contributors, customer deployments, or automated
professional judgment. It is a public starting point for reducing repetitive
documentation work in construction management.

## Who this helps

This project is intended for construction managers, engineers, reviewers, and
technical staff who repeatedly organize:

- construction cost review notes
- meeting decisions and action items
- technical document status
- report draft sections for weekly or design review workflows

## Why it exists

Construction management often involves repeated manual work: collecting review
notes, comparing proposed and reviewed amounts, turning meeting notes into
action lists, and preparing early report drafts. This project provides a small,
testable tool that turns structured input into a consistent draft while keeping
human review in the workflow.

## Current features

- Generate a Markdown report draft from JSON input.
- Summarize proposed and reviewed cost amounts.
- Highlight cost variances that need follow-up.
- Convert meeting decisions and actions into a readable section.
- Track technical material status and pending review items.
- Use only synthetic example data in the repository.

## Install

Clone the repository and install it in editable mode:

```bash
python -m pip install -e ".[dev]"
```

For CLI-only usage without development tools:

```bash
python -m pip install -e .
```

## Quick start

Generate a Markdown report draft from the included example:

```bash
python -m construction_workflow_kit examples/sample_project.json --output examples/sample_project_report.md
```

The same command is also available after installation:

```bash
cwkit examples/sample_project.json --output examples/sample_project_report.md
```

## Example input

```json
{
  "project": {
    "name": "Sample Riverfront Access Road",
    "owner": "Example Public Works Agency",
    "phase": "Design review",
    "prepared_for": "Weekly coordination review"
  },
  "cost_items": [
    {
      "package": "Temporary drainage",
      "proposed_amount": 12500,
      "reviewed_amount": 11800
    }
  ]
}
```

## Example output

```markdown
# Sample Riverfront Access Road - Report Draft

## Cost Review
- Temporary drainage: proposed $12,500.00, reviewed $11,800.00, variance -$700.00 (needs review).
```

## Project structure

```text
.
├── .github/workflows/      # GitHub Actions workflow for linting and tests
├── docs/                   # Project notes and OSS application draft
├── examples/               # Synthetic example inputs and generated samples
├── src/                    # Python package source code
├── tests/                  # Pytest test suite
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── README.md
└── pyproject.toml
```

## Tests and checks

```bash
python -m pytest -q
python -m ruff check .
```

## Future work

- Add richer cost review rules and configurable variance thresholds.
- Add templates for weekly reports, issue summaries, and meeting minutes.
- Add optional AI-assisted drafting while keeping non-AI deterministic output.
- Add import support for CSV or spreadsheet-derived data.
- Add stronger validation for project input schemas.
- Add more examples for different construction management workflows.

## Contributing

Contributions are welcome when they keep the project practical, public, and
safe. See [CONTRIBUTING.md](CONTRIBUTING.md).

Do not add confidential client names, private company names, real project
identifiers, personal contact details, or live contract values. Use clearly fake
example data.

## License

This project is released under the MIT License. See [LICENSE](LICENSE).
