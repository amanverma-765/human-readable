"""Base classes and types for readable verification rules."""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Diagnostic:
    """Represents a readability violation flagged by a rule."""
    rule_id: str
    message: str
    line_number: int
    column: int
    matched_text: str
    cognitive_cost: str
    suggestion: str
    severity: str = "warning"  # "error" | "warning"

    def format(self, style: str = "human") -> str:
        """Format the diagnostic for human readability or machine consumption."""
        if style == "github":
            return (
                f"::{self.severity} line={self.line_number},col={self.column},"
                f"title=[{self.rule_id}]::{self.message} | "
                f"Cognitive Cost: {self.cognitive_cost} | Suggestion: {self.suggestion}"
            )
        if style == "json":
            import json
            return json.dumps({
                "rule_id": self.rule_id,
                "message": self.message,
                "line": self.line_number,
                "column": self.column,
                "matched_text": self.matched_text,
                "cognitive_cost": self.cognitive_cost,
                "suggestion": self.suggestion,
                "severity": self.severity,
            })
        # Default human format
        underline = "^" * max(1, len(self.matched_text))
        return (
            f"Line {self.line_number}:{self.column} [{self.rule_id}] ({self.severity.upper()})\n"
            f"  \"{self.matched_text}\"\n"
            f"  {underline}\n"
            f"  Why: {self.message}\n"
            f"  Cognitive Cost: {self.cognitive_cost}\n"
            f"  Suggestion: {self.suggestion}"
        )


class Rule:
    """Base interface for all readability rules."""
    rule_id: str = "base-rule"
    description: str = ""
    severity: str = "warning"

    def check(self, text: str, line_offset: int = 1) -> List[Diagnostic]:
        """Analyze text and return any detected diagnostics.
        
        Args:
            text: The full text or section to analyze.
            line_offset: 1-indexed line offset for reporting.
        """
        raise NotImplementedError
