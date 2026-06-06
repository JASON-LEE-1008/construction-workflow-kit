# Usage

Construction Workflow Kit currently accepts a structured JSON file and emits a
Markdown report draft.

## Input sections

- `project`: project name, owner, phase, and report audience
- `cost_items`: proposed and reviewed package amounts
- `meeting_notes`: decisions and follow-up actions
- `technical_items`: status of technical materials or review records

## Command

```bash
python -m construction_workflow_kit examples/sample_project.json --output examples/sample_project_report.md
```

The generated Markdown is a draft. It should be reviewed by a qualified person
before use in any formal construction management workflow.
