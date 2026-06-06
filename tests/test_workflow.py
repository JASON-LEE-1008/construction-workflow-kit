import json
from pathlib import Path

import pytest

from construction_workflow_kit.cli import main
from construction_workflow_kit.validation import render_validation_summary, validate_project
from construction_workflow_kit.workflow import (
    analyze_project,
    build_action_register,
    build_project_summary,
    build_report,
    load_project,
    write_report,
)


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
    assert "## Review Dashboard" in report
    assert "Cost packages needing follow-up: 1" in report
    assert "variance -$700.00" in report
    assert "Follow up: Issue updated quantity table." in report
    assert "Close technical review for Retaining wall calculation note." in report
    assert "No validation issues were detected." in report


def test_analyze_project_counts_review_metrics() -> None:
    data = {
        "project": {
            "name": "Sample Riverfront Access Road",
            "owner": "Example Public Works Agency",
            "phase": "Design review",
            "prepared_for": "Weekly coordination",
        },
        "cost_items": [
            {"package": "Temporary drainage", "proposed_amount": 12500, "reviewed_amount": 11800},
            {"package": "Formwork", "proposed_amount": 5000, "reviewed_amount": 5000},
        ],
        "meeting_notes": [{"actions": ["Issue updated quantity table", "Confirm bypass"]}],
        "technical_items": [{"title": "Retaining wall calculation note", "status": "pending"}],
    }

    metrics = analyze_project(data)

    assert metrics.cost_item_count == 2
    assert metrics.cost_items_needing_review == 1
    assert metrics.net_variance == -700
    assert metrics.meeting_action_count == 2
    assert metrics.open_technical_items == 1


def test_action_register_respects_variance_threshold() -> None:
    data = {
        "project": {
            "name": "Sample Road",
            "owner": "Example Public Works Agency",
            "phase": "Design review",
            "prepared_for": "Weekly coordination",
        },
        "cost_items": [
            {
                "package": "Small variance package",
                "proposed_amount": 1000,
                "reviewed_amount": 1100,
            },
            {
                "package": "Large variance package",
                "proposed_amount": 1000,
                "reviewed_amount": 8000,
            },
        ],
    }

    actions = build_action_register(data, variance_threshold=500)
    metrics = analyze_project(data, variance_threshold=500)

    assert len(actions) == 1
    assert metrics.cost_items_needing_review == 1
    assert actions[0].priority == "high"
    assert "Large variance package" in actions[0].description


def test_build_project_summary_is_json_serializable() -> None:
    data = {
        "project": {
            "name": "Sample Road",
            "owner": "Example Public Works Agency",
            "phase": "Design review",
            "prepared_for": "Weekly coordination",
        },
        "cost_items": [
            {
                "package": "Drainage",
                "proposed_amount": 12500,
                "reviewed_amount": 11800,
            }
        ],
        "meeting_notes": [{"topic": "Coordination", "actions": ["Issue update"]}],
        "technical_items": [{"title": "Sketch", "status": "open", "owner": "Reviewer"}],
    }

    summary = build_project_summary(data)
    encoded = json.dumps(summary)

    assert "Sample Road" in encoded
    assert summary["metrics"]["net_variance"] == -700
    assert len(summary["actions"]) == 3


def test_validate_project_reports_errors_and_private_data_warnings() -> None:
    data = {
        "project": {"name": "", "owner": "Example Public Works Agency", "phase": "Design"},
        "cost_items": [{"package": "Drainage", "proposed_amount": "bad", "reviewed_amount": -1}],
        "meeting_notes": [{"date": "not-a-date", "actions": "call reviewer"}],
        "technical_items": [{"title": "Confidential retaining wall note", "status": "unknown"}],
    }

    result = validate_project(data)
    summary = render_validation_summary(result)

    assert not result.is_valid
    assert "project.name" in summary
    assert "cost_items[0].proposed_amount" in summary
    assert "may contain private or sensitive project data" in summary


def test_load_project_rejects_missing_project_section(tmp_path: Path) -> None:
    input_file = tmp_path / "invalid.json"
    input_file.write_text('{"cost_items": []}', encoding="utf-8")

    with pytest.raises(ValueError, match="project"):
        load_project(input_file)


def test_write_report_creates_parent_directories(tmp_path: Path) -> None:
    output_file = tmp_path / "nested" / "report.md"

    write_report("# Draft\n", output_file)

    assert output_file.read_text(encoding="utf-8") == "# Draft\n"


def test_cli_validate_only_returns_success_for_valid_input(tmp_path: Path, capsys) -> None:
    input_file = tmp_path / "project.json"
    input_file.write_text(
        """
        {
          "project": {
            "name": "Sample Road",
            "owner": "Example Public Works Agency",
            "phase": "Design review",
            "prepared_for": "Weekly review"
          },
          "cost_items": []
        }
        """,
        encoding="utf-8",
    )

    exit_code = main([str(input_file), "--validate-only"])

    assert exit_code == 0
    assert "no issues found" in capsys.readouterr().out


def test_cli_validate_only_returns_failure_for_invalid_input(tmp_path: Path, capsys) -> None:
    input_file = tmp_path / "project.json"
    input_file.write_text(
        """
        {
          "project": {
            "name": "",
            "owner": "Example Public Works Agency",
            "phase": "Design review"
          }
        }
        """,
        encoding="utf-8",
    )

    exit_code = main([str(input_file), "--validate-only"])

    assert exit_code == 1
    assert "project.name" in capsys.readouterr().out


def test_cli_writes_json_summary(tmp_path: Path) -> None:
    input_file = tmp_path / "project.json"
    summary_file = tmp_path / "summary.json"
    input_file.write_text(
        """
        {
          "project": {
            "name": "Sample Road",
            "owner": "Example Public Works Agency",
            "phase": "Design review",
            "prepared_for": "Weekly review"
          },
          "cost_items": [
            {
              "package": "Drainage",
              "proposed_amount": 1000,
              "reviewed_amount": 1300
            }
          ]
        }
        """,
        encoding="utf-8",
    )

    exit_code = main(
        [
            str(input_file),
            "--validate-only",
            "--summary-output",
            str(summary_file),
            "--variance-threshold",
            "100",
        ]
    )

    assert exit_code == 0
    summary = json.loads(summary_file.read_text(encoding="utf-8"))
    assert summary["variance_threshold"] == 100
    assert summary["actions"][0]["category"] == "cost"
