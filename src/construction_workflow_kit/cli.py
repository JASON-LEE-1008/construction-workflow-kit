from __future__ import annotations

import argparse
from pathlib import Path

from construction_workflow_kit.workflow import build_report, load_project, write_report


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
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    project = load_project(args.input)
    report = build_report(project)

    if args.output:
        write_report(report, args.output)
        print(f"Wrote report draft to {args.output}")
        return 0

    print(report)
    return 0
