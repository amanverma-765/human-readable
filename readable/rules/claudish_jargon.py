"""Rule 6: Claudish Jargon & Overused AI Dialect Detector.

Detects stereotypical AI mannerisms, hyper-compressed metaphors,
and unattested low-frequency n-gram clichés (e.g. 'delve', 'quietly eating its own', 'verified red').
"""

import re
from typing import List
from readable.rules.base import Rule, Diagnostic
from readable.lexicon import CLAUDISH_CLICHES


class ClaudishJargonRule(Rule):
    """Flags claudish dialect markers and overused AI boilerplate."""
    rule_id = "claudish-jargon"
    description = "Stereotypical AI mannerisms and uninformative, formulaic padding."
    severity = "warning"

    def __init__(self):
        self.patterns = [(re.compile(pat, re.IGNORECASE), expl) for pat, expl in CLAUDISH_CLICHES]

    def check(self, text: str, line_offset: int = 1) -> List[Diagnostic]:
        diagnostics = []
        lines = text.splitlines()

        for idx, line in enumerate(lines):
            line_no = line_offset + idx
            if line.strip().startswith(("```", "#")):
                continue

            for pattern, explanation in self.patterns:
                for m in pattern.finditer(line):
                    matched_str = m.group(0)
                    col = m.start() + 1
                    diagnostics.append(
                        Diagnostic(
                            rule_id=self.rule_id,
                            message=f"Overused AI dialect marker / cliche: '{matched_str}'",
                            line_number=line_no,
                            column=col,
                            matched_text=matched_str,
                            cognitive_cost="High surprisal and low communicative value; creates reader fatigue and signals artificial dialect (Juzek & Ward 2025, Clark et al. 2026).",
                            suggestion=f"{explanation} Rewrite using direct, plain, natural phrasing.",
                            severity=self.severity,
                        )
                    )

        return diagnostics
