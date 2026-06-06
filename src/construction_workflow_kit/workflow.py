from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

ProjectData = Mapping[str, Any]


def load_project(path: str | Path) -> ProjectData:
    input_path = Path(path)
    with input_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError("Project input must be a JSON object.")
    if "project" not in data:
        raise ValueError("Project input must include a 'project' section.")
    return data


def build_report(data: ProjectData) -> str:
    project = _as_mapping(data.get("project", {}))
    cost_items = _as_list(data.get("cost_items", []))
    meeting_notes = _as_list(data.get("meeting_notes", []))
    technical_items = _as_list(data.get("technical_items", []))

    lines = [
        f"# {project.get('name', 'Unnamed Project')} - Report Draft",
        "",
        "## Project Snapshot",
        f"- Owner: {project.get('owner', 'Not specified')}",
        f"- Phase: {project.get('phase', 'Not specified')}",
        f"- Prepared for: {project.get('prepared_for', 'Internal review')}",
        "",
        "## Cost Review",
        *_build_cost_review(cost_items),
        "",
        "## Meeting Notes",
        *_build_meeting_summary(meeting_notes),
        "",
        "## Technical Material Register",
        *_build_technical_summary(technical_items),
        "",
        "## Draft Next Actions",
        *_build_next_actions(cost_items, meeting_notes, technical_items),
    ]
    return "\n".join(lines).rstrip() + "\n"


def write_report(report: str, path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")


def _build_cost_review(items: list[Any]) -> list[str]:
    if not items:
        return ["- No cost items were provided."]

    lines = []
    total_proposed = 0.0
    total_reviewed = 0.0

    for item in items:
        record = _as_mapping(item)
        proposed = float(record.get("proposed_amount", 0))
        reviewed = float(record.get("reviewed_amount", proposed))
        total_proposed += proposed
        total_reviewed += reviewed
        variance = reviewed - proposed
        status = "needs review" if abs(variance) > 0 else "aligned"
        lines.append(
            "- "
            f"{record.get('package', 'Unspecified package')}: "
            f"proposed {_money(proposed)}, reviewed {_money(reviewed)}, "
            f"variance {_money(variance)} ({status})."
        )

    lines.append(
        f"- Total proposed {_money(total_proposed)}; total reviewed {_money(total_reviewed)}; "
        f"net variance {_money(total_reviewed - total_proposed)}."
    )
    return lines


def _build_meeting_summary(notes: list[Any]) -> list[str]:
    if not notes:
        return ["- No meeting notes were provided."]

    lines = []
    for note in notes:
        record = _as_mapping(note)
        decisions = ", ".join(_as_str_list(record.get("decisions", []))) or "none recorded"
        actions = ", ".join(_as_str_list(record.get("actions", []))) or "none recorded"
        lines.append(
            "- "
            f"{record.get('date', 'undated')} {record.get('topic', 'General coordination')}: "
            f"decisions: {decisions}; actions: {actions}."
        )
    return lines


def _build_technical_summary(items: list[Any]) -> list[str]:
    if not items:
        return ["- No technical items were provided."]

    lines = []
    for item in items:
        record = _as_mapping(item)
        lines.append(
            "- "
            f"{record.get('title', 'Untitled material')}: "
            f"{record.get('status', 'status not recorded')} "
            f"({record.get('owner', 'owner not assigned')})."
        )
    return lines


def _build_next_actions(
    cost_items: list[Any],
    meeting_notes: list[Any],
    technical_items: list[Any],
) -> list[str]:
    actions: list[str] = []

    for item in cost_items:
        record = _as_mapping(item)
        proposed = float(record.get("proposed_amount", 0))
        reviewed = float(record.get("reviewed_amount", proposed))
        if proposed != reviewed:
            actions.append(
                f"- Confirm variance for {record.get('package', 'an unspecified cost package')}."
            )

    for note in meeting_notes:
        record = _as_mapping(note)
        for action in _as_str_list(record.get("actions", [])):
            actions.append(f"- Follow up: {action}.")

    for item in technical_items:
        record = _as_mapping(item)
        if str(record.get("status", "")).lower() in {"pending", "needs review", "open"}:
            title = record.get("title", "untitled material")
            actions.append(f"- Close technical review for {title}.")

    return actions or ["- No immediate actions were generated from the input."]


def _money(value: float) -> str:
    sign = "-" if value < 0 else ""
    return f"{sign}${abs(value):,.2f}"


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _as_str_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if str(item).strip()]
