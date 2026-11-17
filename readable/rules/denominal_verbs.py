"""Rule 4: Ad-hoc Denominal Verb Detector.

Detects nouns coerced into verbs in ad-hoc contexts
(e.g., 'calendar it', 'footnote it', 'speed-runnable', 'action the ticket').
"""

import re
from typing import List
from readable.rules.base import Rule, Diagnostic
from readable.lexicon import AD_HOC_DENOMINAL_VERBS


SUGGESTED_REWRITES = {
    "footnote": "add a footnote to",
    "footnotes": "adds a footnote to",
    "footnoting": "adding a footnote to",
    "footnoted": "added a footnote to",
    "calendar": "add to the calendar / schedule",
    "calendars": "adds to the calendar / schedules",
    "calendaring": "adding to the calendar / scheduling",
    "calendared": "added to the calendar / scheduled",
    "action": "take action on / resolve",
    "actions": "takes action on / resolves",
    "actioning": "taking action on",
    "actioned": "took action on",
    "solution": "solve / resolve",
    "packetize": "divide into packets",
    "dotfolder": "hidden dot-directory",
    "speed-runnable": "suitable for viewing at high speed",
    "speedrunnable": "suitable for viewing at high speed",
}


class DenominalVerbsRule(Rule):
    """Flags ad-hoc conversion of nouns into verbs."""
    rule_id = "denominal-verb"
    description = "Ad-hoc conversion of prototypical nouns into verbs."
    severity = "warning"

    def __init__(self):
        verb_stems = "|".join(re.escape(v) for v in sorted(AD_HOC_DENOMINAL_VERBS, key=len, reverse=True))
        
        # 1. Transitive/imperative usage: [verb] [it|this|that|the ...]
        self.transitive_pattern = re.compile(
            rf"\b(?P<verb>{verb_stems})\s+(?P<obj>it|this|that|them|the\s+[A-Za-z0-9_-]+)\b",
            re.IGNORECASE
        )

        # 2. Infinitive usage: "to [verb]"
        self.infinitive_pattern = re.compile(
            rf"\bto\s+(?P<verb>{verb_stems})\b",
            re.IGNORECASE
        )

        # 3. Adjective/participle usage: e.g. "speed-runnable", "dotfolder"
        self.misc_pattern = re.compile(
            r"\b(?P<word>speed-runnable|speedrunnable|dotfolder|dotfolders)\b",
            re.IGNORECASE
        )

    def check(self, text: str, line_offset: int = 1) -> List[Diagnostic]:
        diagnostics = []
        lines = text.splitlines()

        for idx, line in enumerate(lines):
            line_no = line_offset + idx
            if line.strip().startswith(("```", "#")):
                continue

            matches = []
            for m in self.transitive_pattern.finditer(line):
                matches.append((m.start(), m.end(), m.group(0), m.group("verb").lower()))
            for m in self.infinitive_pattern.finditer(line):
                matches.append((m.start(), m.end(), m.group(0), m.group("verb").lower()))
            for m in self.misc_pattern.finditer(line):
                matches.append((m.start(), m.end(), m.group(0), m.group("word").lower()))

            seen = set()
            for start, end, matched_text, key in matches:
                span = (start, end)
                if span in seen:
                    continue
                seen.add(span)

                suggestion = SUGGESTED_REWRITES.get(key, f"use standard verbal phrase instead of '{key}'")

                diagnostics.append(
                    Diagnostic(
                        rule_id=self.rule_id,
                        message=f"Ad-hoc denominal verb conversion: '{matched_text}'",
                        line_number=line_no,
                        column=start + 1,
                        matched_text=matched_text,
                        cognitive_cost="Forces syntactic category disambiguation, triggering late-stage syntactic re-parsing (Thierry et al. 2008, Federmeier et al. 2000).",
                        suggestion=f"Replace with standard verbal phrase: '{suggestion}'",
                        severity=self.severity,
                    )
                )

        return diagnostics
