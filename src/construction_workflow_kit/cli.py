from __future__ import annotations

import argparse
import sys
from pathlib import Path

from construction_workflow_kit.validation import render_validation_summary, validate_project
from construction_workflow_kit.workflow import (
    build_project_summary,
    build_report,
    load_project,
    write_json_summary,
    write_report,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cwkit",
        description=(
            "Create a construction management report draft from a safe, structured JSON input."
        ),
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Path to a project JSON file, such as examples/sample_project.json.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Markdown output path. If omitted, the report is printed to stdout.",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate the input file and exit without generating a report.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat validation warnings as failures.",
    )
    parser.add_argument(
        "--variance-threshold",
        type=_nonnegative_float,
        default=0.0,
        help="Ignore cost variances at or below this amount when creating action items.",
    )
    parser.add_argument(
        "--summary-output",
        type=Path,
        help="Optional JSON summary output path for automation and release checks.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    project = load_project(args.input)
    validation = validate_project(project)
    if args.summary_output:
        summary = build_project_summary(project, variance_threshold=args.variance_threshold)
        write_json_summary(summary, args.summary_output)

    if args.validate_only:
        print(render_validation_summary(validation))
        if args.summary_output:
            print(f"Wrote JSON summary to {args.summary_output}")
        return _validation_exit_code(validation, strict=args.strict)

    validation_exit_code = _validation_exit_code(validation, strict=args.strict)
    if validation_exit_code != 0:
        print(render_validation_summary(validation), file=sys.stderr)
        return validation_exit_code

    report = build_report(project, variance_threshold=args.variance_threshold)

    if args.output:
        write_report(report, args.output)
        print(f"Wrote report draft to {args.output}")
        if args.summary_output:
            print(f"Wrote JSON summary to {args.summary_output}")
        return 0

    print(report)
    if args.summary_output:
        print(f"Wrote JSON summary to {args.summary_output}")
    return 0


def _validation_exit_code(validation, *, strict: bool) -> int:
    if validation.errors:
        return 1
    if strict and validation.warnings:
        return 1
    return 0


def _nonnegative_float(value: str) -> float:
    parsed = float(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be greater than or equal to 0")
    return parsed
