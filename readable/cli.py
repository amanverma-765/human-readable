"""Command-line interface for readable verification."""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from readable.checker import ReadabilityChecker
from readable.rules import ALL_RULES
from readable.rules.base import Diagnostic


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="readable",
        description="Deterministic psycholinguistic readability verifier for coding agents and human text.",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="Files or directories to check. Use '-' to read from standard input.",
    )
    parser.add_argument(
        "-s", "--string",
        type=str,
        help="Check inline text string directly.",
    )
    parser.add_argument(
        "--format",
        choices=["human", "json", "github"],
        default="human",
        help="Output format (default: human).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors (exit code 1 on any violation).",
    )
    parser.add_argument(
        "--rule",
        action="append",
        help="Enable only specified rule IDs (can be repeated).",
    )
    parser.add_argument(
        "--ignore-rule",
        action="append",
        help="Ignore specified rule IDs (can be repeated).",
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Suppress output when clean; only display violations.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0",
    )
    return parser


def main(args: Optional[List[str]] = None) -> int:
    parser = create_parser()
    opts = parser.parse_args(args)

    # Filter rules
    selected_rules = ALL_RULES
    if opts.rule:
        selected_rules = [r for r in selected_rules if r.rule_id in opts.rule]
    if opts.ignore_rule:
        selected_rules = [r for r in selected_rules if r.rule_id not in opts.ignore_rule]

    checker = ReadabilityChecker(rules=selected_rules)
    all_diagnostics: List[Diagnostic] = []

    # 1. Inline string check
    if opts.string is not None:
        diagnostics = checker.check_text(opts.string, filename="<string>")
        all_diagnostics.extend(diagnostics)

    # 2. Stdin check
    elif opts.paths and opts.paths[0] == "-":
        stdin_text = sys.stdin.read()
        diagnostics = checker.check_text(stdin_text, filename="<stdin>")
        all_diagnostics.extend(diagnostics)

    # 3. File paths check
    elif opts.paths:
        for p in opts.paths:
            path = Path(p)
            if not path.exists():
                sys.stderr.write(f"Error: Path '{p}' does not exist.\n")
                return 2

            files_to_check = [path] if path.is_file() else list(path.glob("**/*.md")) + list(path.glob("**/*.txt"))
            for file_path in files_to_check:
                try:
                    file_diags = checker.check_file(str(file_path))
                    for d in file_diags:
                        d.message = f"{file_path}:{d.line_number}:{d.column} {d.message}"
                    all_diagnostics.extend(file_diags)
                except Exception as e:
                    sys.stderr.write(f"Error reading '{file_path}': {e}\n")
                    return 2
    else:
        parser.print_help()
        return 0

    # Output formatting
    if opts.format == "json":
        import json
        print(json.dumps([
            {
                "rule_id": d.rule_id,
                "message": d.message,
                "line": d.line_number,
                "column": d.column,
                "matched_text": d.matched_text,
                "cognitive_cost": d.cognitive_cost,
                "suggestion": d.suggestion,
                "severity": d.severity,
            }
            for d in all_diagnostics
        ], indent=2))
    elif opts.format == "github":
        for d in all_diagnostics:
            print(d.format("github"))
    else:  # human format
        if all_diagnostics:
            for d in all_diagnostics:
                print(d.format("human"))
                print()
            error_count = sum(1 for d in all_diagnostics if d.severity == "error")
            warn_count = sum(1 for d in all_diagnostics if d.severity == "warning")
            print(f"Readable Summary: {len(all_diagnostics)} violation(s) found ({error_count} error(s), {warn_count} warning(s)).")
        elif not opts.quiet:
            print("Readable: All text passed psycholinguistic readability checks. Clean!")

    if opts.strict and all_diagnostics:
        return 1
    error_count = sum(1 for d in all_diagnostics if d.severity == "error")
    if error_count > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
