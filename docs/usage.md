# Usage

Construction Workflow Kit currently accepts a structured JSON file and emits a
Markdown report draft. It can also validate the input file before report
generation.

## Input sections

- `project`: project name, owner, phase, and report audience
- `cost_items`: proposed and reviewed package amounts
- `meeting_notes`: decisions and follow-up actions
- `technical_items`: status of technical materials or review records

## Command

```bash
python -m construction_workflow_kit examples/sample_project.json --output examples/sample_project_report.md
```

## Validate input data

```bash
python -m construction_workflow_kit examples/sample_project.json --validate-only
```

Use strict mode when reviewing examples for release:

```bash
python -m construction_workflow_kit examples/sample_project.json --validate-only --strict
```

## JSON summary output

```bash
python -m construction_workflow_kit examples/sample_project.json \
  --summary-output examples/sample_project_summary.json \
  --output examples/sample_project_report.md
```

The JSON summary includes:

- project metadata
- cost, meeting, and technical review metrics
- validation errors and warnings
- prioritized action register items

## Variance threshold

Use `--variance-threshold` to ignore small cost differences when creating action
items:

```bash
python -m construction_workflow_kit examples/sample_project.json \
  --variance-threshold 500 \
  --output examples/sample_project_report.md
```

See [input-schema.md](input-schema.md) for the supported JSON structure.

The generated Markdown is a draft. It should be reviewed by a qualified person
before use in any formal construction management workflow.
