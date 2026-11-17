"""Rule 5: Dependency Distance & Sentence Sprawl Detector.

Detects long-distance syntactic dependencies and unpunctuated sentence sprawl
that overload human working memory under Dependency Locality Theory (DLT).
"""

import re
from typing import List
from readable.rules.base import Rule, Diagnostic


class DependencyDistanceRule(Rule):
    """Flags excessive sentence length and long-distance subject-verb dependencies."""
    rule_id = "dependency-distance"
    description = "Excessive syntactic distance between related words or run-on sentence spans."
    severity = "warning"

    MAX_SENTENCE_WORDS = 32
    MAX_UNPUNCTUATED_SPAN = 22

    def __init__(self):
        # Pattern to detect long-distance center embedding:
        # e.g., "The [Noun] [8+ words without comma/semicolon] [Verb]"
        self.center_embedded = re.compile(
            r"\b(?:The|A|An)\s+(?P<subj>[a-zA-Z0-9_-]+)\s+(?P<clause>(?:[a-zA-Z0-9_'\"-]+\s+){8,20})(?P<verb>is|was|are|were|has|had|teaches|provides|creates|leaves|renders|causes|brings)\b",
            re.IGNORECASE
        )

    def check(self, text: str, line_offset: int = 1) -> List[Diagnostic]:
        diagnostics = []
        lines = text.splitlines()

        for idx, line in enumerate(lines):
            line_no = line_offset + idx
            stripped = line.strip()
            if not stripped or stripped.startswith(("```", "#", ">", "-", "*", "1.", "2.", "3.")):
                continue

            # 1. Check center-embedded long-distance dependencies
            for m in self.center_embedded.finditer(line):
                matched = m.group(0)
                subj = m.group("subj")
                verb = m.group("verb")
                intervening_words = len(m.group("clause").split())
                col = m.start() + 1
                diagnostics.append(
                    Diagnostic(
                        rule_id=self.rule_id,
                        message=(
                            f"Long syntactic dependency: Subject '{subj}' is separated from verb '{verb}' "
                            f"by {intervening_words} intervening words in a center-embedded clause."
                        ),
                        line_number=line_no,
                        column=col,
                        matched_text=matched,
                        cognitive_cost="Dependency Locality Theory (Gibson 1998, 2000): human working memory is distance-sensitive; distant discourse referents cause cognitive exhaustion and parsing delays.",
                        suggestion=f"Shorten the intervening modifier or split into two sentences (e.g. '{subj} ... It {verb} ...').",
                        severity=self.severity,
                    )
                )

            # 2. Check for sentence length sprawl
            # Split line into sentences roughly
            sentences = re.split(r"(?<=[.!?])\s+", line)
            for s in sentences:
                words = s.split()
                if len(words) > self.MAX_SENTENCE_WORDS:
                    # Find position of sentence in line
                    start_char = line.find(s)
                    col = start_char + 1 if start_char >= 0 else 1
                    diagnostics.append(
                        Diagnostic(
                            rule_id=self.rule_id,
                            message=f"Sentence sprawl ({len(words)} words in a single sentence).",
                            line_number=line_no,
                            column=col,
                            matched_text=s[:80] + ("..." if len(s) > 80 else ""),
                            cognitive_cost="Sentences >30 words dramatically increase working memory decay and reading comprehension error rates (Futrell et al. 2015, Gibson 2000).",
                            suggestion="Decompose this sentence into 2 or 3 shorter, punchy sentences.",
                            severity=self.severity,
                        )
                    )

        return diagnostics
