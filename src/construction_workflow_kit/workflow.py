from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from construction_workflow_kit.validation import ValidationResult, validate_project

ProjectData = Mapping[str, Any]
_OPEN_TECHNICAL_STATUSES = {"pending", "needs review", "open"}


@dataclass(frozen=True)
class ProjectMetrics:
    cost_item_count: int
    total_proposed: float
    total_reviewed: float
    net_variance: float
    cost_items_needing_review: int
    meeting_action_count: int
    open_technical_items: int


@dataclass(frozen=True)
class ActionItem:
    category: str
    priority: str
    source: str
    description: str


def load_project(path: str | Path) -> ProjectData:
    input_path = Path(path)
    with input_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError("Project input must be a JSON object.")
    if "project" not in data:
        raise ValueError("Project input must include a 'project' section.")
    return data


def build_report(data: ProjectData, *, variance_threshold: float = 0.0) -> str:
    project = _as_mapping(data.get("project", {}))
    cost_items = _as_list(data.get("cost_items", []))
    meeting_notes = _as_list(data.get("meeting_notes", []))
    technical_items = _as_list(data.get("technical_items", []))
    metrics = analyze_project(data, variance_threshold=variance_threshold)
    validation = validate_project(data)

    lines = [
        f"# {project.get('name', 'Unnamed Project')} - Report Draft",
        "",
        "## Project Snapshot",
        f"- Owner: {project.get('owner', 'Not specified')}",
        f"- Phase: {project.get('phase', 'Not specified')}",
        f"- Prepared for: {project.get('prepared_for', 'Internal review')}",
        "",
        "## Review Dashboard",
        *_build_dashboard(metrics, validation),
        "",
        "## Cost Review",
        *_build_cost_review(cost_items, variance_threshold=variance_threshold),
        "",
        "## Meeting Notes",
        *_build_meeting_summary(meeting_notes),
        "",
        "## Technical Material Register",
        *_build_technical_summary(technical_items),
        "",
        "## Action Register",
        *_build_action_register_lines(
            build_action_register(data, variance_threshold=variance_threshold)
        ),
        "",
        "## Validation Notes",
        *_build_validation_notes(validation),
    ]
    return "\n".join(lines).rstrip() + "\n"


def analyze_project(data: ProjectData, *, variance_threshold: float = 0.0) -> ProjectMetrics:
    cost_items = _as_list(data.get("cost_items", []))
    meeting_notes = _as_list(data.get("meeting_notes", []))
    technical_items = _as_list(data.get("technical_items", []))

    total_proposed = 0.0
    total_reviewed = 0.0
    cost_items_needing_review = 0

    for item in cost_items:
        record = _as_mapping(item)
        proposed = _as_number(record.get("proposed_amount", 0))
        reviewed = _as_number(record.get("reviewed_amount", proposed))
        total_proposed += proposed
        total_reviewed += reviewed
        if abs(reviewed - proposed) > variance_threshold:
            cost_items_needing_review += 1

    meeting_action_count = 0
    for note in meeting_notes:
        record = _as_mapping(note)
        meeting_action_count += len(_as_str_list(record.get("actions", [])))

    open_technical_items = 0
    for item in technical_items:
        record = _as_mapping(item)
        if str(record.get("status", "")).strip().lower() in _OPEN_TECHNICAL_STATUSES:
            open_technical_items += 1

    return ProjectMetrics(
        cost_item_count=len(cost_items),
        total_proposed=total_proposed,
        total_reviewed=total_reviewed,
        net_variance=total_reviewed - total_proposed,
        cost_items_needing_review=cost_items_needing_review,
        meeting_action_count=meeting_action_count,
        open_technical_items=open_technical_items,
    )


def build_action_register(
    data: ProjectData,
    *,
    variance_threshold: float = 0.0,
) -> list[ActionItem]:
    actions: list[ActionItem] = []
    cost_items = _as_list(data.get("cost_items", []))
    meeting_notes = _as_list(data.get("meeting_notes", []))
    technical_items = _as_list(data.get("technical_items", []))

    for item in cost_items:
        record = _as_mapping(item)
        package = str(record.get("package", "an unspecified cost package"))
        proposed = _as_number(record.get("proposed_amount", 0))
        reviewed = _as_number(record.get("reviewed_amount", proposed))
        variance = reviewed - proposed
        if abs(variance) > variance_threshold:
            actions.append(
                ActionItem(
                    category="cost",
                    priority=_cost_priority(abs(variance), variance_threshold),
                    source=package,
                    description=f"Confirm variance of {_money(variance)} for {package}.",
                )
            )

    for note in meeting_notes:
        record = _as_mapping(note)
        topic = str(record.get("topic", "General coordination"))
        for action in _as_str_list(record.get("actions", [])):
            actions.append(
                ActionItem(
                    category="meeting",
                    priority="medium",
                    source=topic,
                    description=f"Follow up: {action}.",
                )
            )

    for item in technical_items:
        record = _as_mapping(item)
        status = str(record.get("status", "")).strip().lower()
        if status in _OPEN_TECHNICAL_STATUSES:
            title = str(record.get("title", "untitled material"))
            actions.append(
                ActionItem(
                    category="technical",
                    priority="high" if status == "needs review" else "medium",
                    source=title,
                    description=f"Close technical review for {title}.",
                )
            )

    return actions


def build_project_summary(
    data: ProjectData,
    *,
    variance_threshold: float = 0.0,
) -> dict[str, Any]:
    project = _as_mapping(data.get("project", {}))
    validation = validate_project(data)
    return {
        "project": {
            "name": project.get("name", "Unnamed Project"),
            "owner": project.get("owner", "Not specified"),
            "phase": project.get("phase", "Not specified"),
            "prepared_for": project.get("prepared_for", "Internal review"),
        },
        "variance_threshold": variance_threshold,
        "metrics": asdict(analyze_project(data, variance_threshold=variance_threshold)),
        "validation": {
            "errors": [asdict(issue) for issue in validation.errors],
            "warnings": [asdict(issue) for issue in validation.warnings],
        },
        "actions": [
            asdict(action)
            for action in build_action_register(data, variance_threshold=variance_threshold)
        ],
    }


def write_report(report: str, path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")


def write_json_summary(summary: Mapping[str, Any], path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


def _build_dashboard(metrics: ProjectMetrics, validation: ValidationResult) -> list[str]:
    validation_count = f"{len(validation.errors)} error(s), {len(validation.warnings)} warning(s)"
    return [
        f"- Cost packages reviewed: {metrics.cost_item_count}",
        f"- Cost packages needing follow-up: {metrics.cost_items_needing_review}",
        f"- Net cost variance: {_money(metrics.net_variance)}",
        f"- Meeting follow-up actions: {metrics.meeting_action_count}",
        f"- Open technical review items: {metrics.open_technical_items}",
        f"- Validation issues: {validation_count}",
    ]


def _build_cost_review(items: list[Any], *, variance_threshold: float) -> list[str]:
    if not items:
        return ["- No cost items were provided."]

    lines = []
    total_proposed = 0.0
    total_reviewed = 0.0

    for item in items:
        record = _as_mapping(item)
        proposed = _as_number(record.get("proposed_amount", 0))
        reviewed = _as_number(record.get("reviewed_amount", proposed))
        total_proposed += proposed
        total_reviewed += reviewed
        variance = reviewed - proposed
        status = "needs review" if abs(variance) > variance_threshold else "aligned"
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


def _build_action_register_lines(actions: list[ActionItem]) -> list[str]:
    if not actions:
        return ["- No immediate actions were generated from the input."]
    return [
        f"- [{action.priority}] {action.category}: {action.description} ({action.source})"
        for action in actions
    ]


def _build_validation_notes(validation: ValidationResult) -> list[str]:
    if not validation.issues:
        return ["- No validation issues were detected."]

    lines = []
    for issue in validation.issues:
        lines.append(f"- {issue.severity.upper()} {issue.path}: {issue.message}")
    return lines


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


def _as_number(value: Any) -> float:
    if isinstance(value, bool):
        return 0.0
    if isinstance(value, int | float):
        return float(value)
    return 0.0


def _cost_priority(variance: float, threshold: float) -> str:
    high_threshold = max(threshold * 2, 5000.0)
    if variance >= high_threshold:
        return "high"
    if variance > threshold:
        return "medium"
    return "low"
