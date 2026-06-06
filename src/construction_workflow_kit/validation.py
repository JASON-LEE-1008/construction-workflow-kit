from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import date
from typing import Any, Literal

Severity = Literal["error", "warning"]

_PRIVATE_DATA_PATTERNS = (
    re.compile(r"\bconfidential\b", re.IGNORECASE),
    re.compile(r"\binternal project\b", re.IGNORECASE),
    re.compile(r"\bdo not share\b", re.IGNORECASE),
    re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
)

_TECHNICAL_STATUSES = {
    "accepted",
    "accepted for draft reporting",
    "closed",
    "needs review",
    "open",
    "pending",
    "resolved",
}


@dataclass(frozen=True)
class ValidationIssue:
    severity: Severity
    path: str
    message: str


@dataclass(frozen=True)
class ValidationResult:
    issues: tuple[ValidationIssue, ...]

    @property
    def errors(self) -> tuple[ValidationIssue, ...]:
        return tuple(issue for issue in self.issues if issue.severity == "error")

    @property
    def warnings(self) -> tuple[ValidationIssue, ...]:
        return tuple(issue for issue in self.issues if issue.severity == "warning")

    @property
    def is_valid(self) -> bool:
        return not self.errors


def validate_project(data: Mapping[str, Any]) -> ValidationResult:
    issues: list[ValidationIssue] = []

    _validate_project_section(data.get("project"), issues)
    _validate_cost_items(data.get("cost_items", []), issues)
    _validate_meeting_notes(data.get("meeting_notes", []), issues)
    _validate_technical_items(data.get("technical_items", []), issues)
    _check_private_data_markers(data, issues)

    return ValidationResult(tuple(issues))


def render_validation_summary(result: ValidationResult) -> str:
    if not result.issues:
        return "Validation completed: no issues found."

    lines = [
        f"Validation completed: {len(result.errors)} error(s), {len(result.warnings)} warning(s)."
    ]
    for issue in result.issues:
        lines.append(f"- {issue.severity.upper()} {issue.path}: {issue.message}")
    return "\n".join(lines)


def _validate_project_section(value: Any, issues: list[ValidationIssue]) -> None:
    if not isinstance(value, Mapping):
        _add(issues, "error", "project", "must be an object.")
        return

    for field in ("name", "owner", "phase"):
        if not _present_text(value.get(field)):
            _add(issues, "error", f"project.{field}", "is required.")

    if not _present_text(value.get("prepared_for")):
        _add(issues, "warning", "project.prepared_for", "is recommended for report context.")


def _validate_cost_items(value: Any, issues: list[ValidationIssue]) -> None:
    if value is None:
        return
    if not isinstance(value, list):
        _add(issues, "error", "cost_items", "must be a list when provided.")
        return

    for index, item in enumerate(value):
        path = f"cost_items[{index}]"
        if not isinstance(item, Mapping):
            _add(issues, "error", path, "must be an object.")
            continue

        if not _present_text(item.get("package")):
            _add(issues, "warning", f"{path}.package", "is recommended.")

        for field in ("proposed_amount", "reviewed_amount"):
            amount = item.get(field)
            if amount is None:
                _add(issues, "warning", f"{path}.{field}", "is recommended.")
                continue
            if not _is_number(amount):
                _add(issues, "error", f"{path}.{field}", "must be a number.")
            elif float(amount) < 0:
                _add(issues, "error", f"{path}.{field}", "must not be negative.")


def _validate_meeting_notes(value: Any, issues: list[ValidationIssue]) -> None:
    if value is None:
        return
    if not isinstance(value, list):
        _add(issues, "error", "meeting_notes", "must be a list when provided.")
        return

    for index, item in enumerate(value):
        path = f"meeting_notes[{index}]"
        if not isinstance(item, Mapping):
            _add(issues, "error", path, "must be an object.")
            continue

        note_date = item.get("date")
        if not _present_text(note_date):
            _add(issues, "warning", f"{path}.date", "is recommended.")
        elif not _is_iso_date(str(note_date)):
            _add(issues, "warning", f"{path}.date", "should use YYYY-MM-DD format.")

        if not _present_text(item.get("topic")):
            _add(issues, "warning", f"{path}.topic", "is recommended.")

        for field in ("decisions", "actions"):
            if field in item and not _is_list_of_text(item[field]):
                _add(issues, "warning", f"{path}.{field}", "should be a list of text values.")


def _validate_technical_items(value: Any, issues: list[ValidationIssue]) -> None:
    if value is None:
        return
    if not isinstance(value, list):
        _add(issues, "error", "technical_items", "must be a list when provided.")
        return

    for index, item in enumerate(value):
        path = f"technical_items[{index}]"
        if not isinstance(item, Mapping):
            _add(issues, "error", path, "must be an object.")
            continue

        if not _present_text(item.get("title")):
            _add(issues, "warning", f"{path}.title", "is recommended.")
        if not _present_text(item.get("owner")):
            _add(issues, "warning", f"{path}.owner", "is recommended.")

        status = item.get("status")
        if not _present_text(status):
            _add(issues, "warning", f"{path}.status", "is recommended.")
        elif str(status).strip().lower() not in _TECHNICAL_STATUSES:
            _add(issues, "warning", f"{path}.status", "is not a recognized status.")


def _check_private_data_markers(data: Mapping[str, Any], issues: list[ValidationIssue]) -> None:
    for path, text in _walk_text(data):
        for pattern in _PRIVATE_DATA_PATTERNS:
            if pattern.search(text):
                _add(
                    issues,
                    "warning",
                    path,
                    "may contain private or sensitive project data.",
                )
                break


def _walk_text(value: Any, path: str = "$") -> Iterable[tuple[str, str]]:
    if isinstance(value, Mapping):
        for key, child in value.items():
            yield from _walk_text(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk_text(child, f"{path}[{index}]")
    elif isinstance(value, str):
        yield path, value


def _present_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_list_of_text(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) and item.strip() for item in value)


def _is_number(value: Any) -> bool:
    return isinstance(value, int | float) and not isinstance(value, bool)


def _is_iso_date(value: str) -> bool:
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def _add(issues: list[ValidationIssue], severity: Severity, path: str, message: str) -> None:
    issues.append(ValidationIssue(severity, path, message))
