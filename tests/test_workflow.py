from pathlib import Path

import pytest

from construction_workflow_kit.workflow import build_report, load_project, write_report


def test_build_report_includes_cost_variance_and_actions() -> None:
    data = {
        "project": {
            "name": "Sample Riverfront Access Road",
            "owner": "Example Public Works Agency",
            "phase": "Design review",
            "prepared_for": "Weekly coordination",
        },
        "cost_items": [
            {
                "package": "Temporary drainage",
                "proposed_amount": 12500,
                "reviewed_amount": 11800,
            }
        ],
        "meeting_notes": [
            {
                "date": "2026-06-01",
                "topic": "Drainage coordination",
                "decisions": ["Use revised inlet schedule"],
                "actions": ["Issue updated quantity table"],
            }
        ],
        "technical_items": [
            {
                "title": "Retaining wall calculation note",
                "status": "pending",
                "owner": "Design reviewer",
            }
        ],
    }

    report = build_report(data)

    assert "Sample Riverfront Access Road - Report Draft" in report
    assert "variance -$700.00" in report
    assert "Follow up: Issue updated quantity table." in report
    assert "Close technical review for Retaining wall calculation note." in report


def test_load_project_rejects_missing_project_section(tmp_path: Path) -> None:
    input_file = tmp_path / "invalid.json"
    input_file.write_text('{"cost_items": []}', encoding="utf-8")

    with pytest.raises(ValueError, match="project"):
        load_project(input_file)


def test_write_report_creates_parent_directories(tmp_path: Path) -> None:
    output_file = tmp_path / "nested" / "report.md"

    write_report("# Draft\n", output_file)

    assert output_file.read_text(encoding="utf-8") == "# Draft\n"
