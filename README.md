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
- Validate input quality before generating a report.
- Show a review dashboard with cost, meeting, and technical review counts.
- Produce an action register with priority, category, source, and description.
- Write a machine-readable JSON summary for automation and release checks.
- Filter cost follow-up items with a configurable variance threshold.
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

Validate an input file without generating a report:

```bash
python -m construction_workflow_kit examples/sample_project.json --validate-only
```

Treat warnings as failures when preparing release examples or reviewing
contributions:

```bash
python -m construction_workflow_kit examples/sample_project.json --validate-only --strict
```

Generate both a Markdown report and a JSON summary:

```bash
python -m construction_workflow_kit examples/sample_project.json \
  --output examples/sample_project_report.md \
  --summary-output examples/sample_project_summary.json
```

Ignore cost variances at or below a selected amount when building the action
register:

```bash
python -m construction_workflow_kit examples/sample_project.json \
  --variance-threshold 500 \
  --output examples/sample_project_report.md
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

## Review Dashboard
- Cost packages reviewed: 2
- Cost packages needing follow-up: 1
- Net cost variance: -$700.00

## Cost Review
- Temporary drainage: proposed $12,500.00, reviewed $11,800.00, variance -$700.00 (needs review).

## Action Register
- [medium] cost: Confirm variance of -$700.00 for Temporary drainage. (Temporary drainage)

## Validation Notes
- No validation issues were detected.
```

## Project structure

```text
.
|-- .github/
|   |-- ISSUE_TEMPLATE/
|   |-- workflows/
|   `-- pull_request_template.md
|-- docs/
|-- examples/
|-- src/
|-- tests/
|-- CHANGELOG.md
|-- CONTRIBUTING.md
|-- LICENSE
|-- README.md
|-- SECURITY.md
`-- pyproject.toml
```

## Tests and checks

```bash
python -m pytest -q
python -m ruff check .
python -m ruff format --check .
python -m build
python -m twine check dist/*
```

See [docs/release-checklist.md](docs/release-checklist.md) before tagging or
publishing a release.

## Future work

- Add richer cost review rules and configurable variance thresholds.
- Add templates for weekly reports, issue summaries, and meeting minutes.
- Add optional AI-assisted drafting while keeping non-AI deterministic output.
- Add import support for CSV or spreadsheet-derived data.
- Add more examples for different construction management workflows.

## Contributing

Contributions are welcome when they keep the project practical, public, and
safe. See [CONTRIBUTING.md](CONTRIBUTING.md).

Do not add confidential client names, private company names, real project
identifiers, personal contact details, or live contract values. Use clearly fake
example data.

## License

This project is released under the MIT License. See [LICENSE](LICENSE).
