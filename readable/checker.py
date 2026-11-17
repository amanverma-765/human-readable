"""Core Readability Verification Engine."""

import re
from pathlib import Path
from typing import List, Optional, Sequence, Type

from readable.rules import ALL_RULES, Rule, Diagnostic


class ReadabilityChecker:
    """Verifies that text adheres to human psycholinguistic readability standards."""

    def __init__(self, rules: Optional[Sequence[Type[Rule]]] = None):
        rule_classes = rules if rules is not None else ALL_RULES
        self.rules: List[Rule] = [r() for r in rule_classes]

    def _strip_code_blocks(self, text: str) -> str:
        """Replace code blocks and inline code with spaces to preserve line and column numbering."""
        lines = text.splitlines(keepends=True)
        cleaned_lines = []
        in_code_block = False

        for line in lines:
            stripped = line.strip()
            if stripped.startswith("```"):
                in_code_block = not in_code_block
                cleaned_lines.append("\n")
                continue
            if in_code_block:
                cleaned_lines.append("\n")
            else:
                # Mask inline backtick code spans with equal-length spaces
                masked_line = re.sub(r"`[^`\n]+`", lambda m: " " * len(m.group(0)), line)
                cleaned_lines.append(masked_line)

        return "".join(cleaned_lines)

    def check_text(self, text: str, filename: Optional[str] = None) -> List[Diagnostic]:
        """Check text for readability violations.
        
        Args:
            text: The text string to verify.
            filename: Optional source filename for display.
        """
        # Strip code blocks while keeping line numbers intact
        sanitized_text = self._strip_code_blocks(text)
        diagnostics: List[Diagnostic] = []

        for rule in self.rules:
            diagnostics.extend(rule.check(sanitized_text, line_offset=1))

        # Sort diagnostics by line number, then column
        diagnostics.sort(key=lambda d: (d.line_number, d.column))
        return diagnostics

    def check_file(self, file_path: str) -> List[Diagnostic]:
        """Check a file from disk."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        text = path.read_text(encoding="utf-8", errors="replace")
        return self.check_text(text, filename=str(path))
