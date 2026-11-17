"""Rule 2: Selectional Restriction Violation Detector.

Detects inanimate or abstract subjects paired with active verbs requiring
animate agency, consciousness, or biological consumption
(e.g., 'the check forgot bytes', 'chaos expects you', 'the conversation is eating its tail').
"""

import re
from typing import List
from readable.rules.base import Rule, Diagnostic
from readable.lexicon import INANIMATE_SUBJECTS, ANIMATE_AGENCY_VERBS


class SelectionalRestrictionsRule(Rule):
    """Flags inanimate subjects with animate verbs (selectional restriction violations)."""
    rule_id = "selectional-restriction"
    description = "Inanimate or abstract subject with an active verb requiring animate agency."
    severity = "error"

    def __init__(self):
        inanim_nouns = "|".join(re.escape(n) for n in sorted(INANIMATE_SUBJECTS, key=len, reverse=True))
        verb_stems = "|".join(re.escape(v) for v in sorted(ANIMATE_AGENCY_VERBS, key=len, reverse=True))

        # Regex to scan for: (determiner) (modifier) Subject + (optional bridge up to 7 words) + Verb
        self.pattern = re.compile(
            rf"\b(?:the|this|that|these|those|a|an|every|each)?\s*(?:[A-Za-z0-9_]+\s+)?"
            rf"(?P<subject>{inanim_nouns}|[A-Za-z0-9_]+(?:\(\)|_test|_check|_script|_fn))\b"
            rf"(?:\s+[A-Za-z0-9_'\"\-]+){{0,7}}\s+(?P<verb>\b(?:{verb_stems})\b)",
            re.IGNORECASE
        )

        # Pattern for coordinating clauses: e.g. "covered X but forgot Y"
        self.coordination_pattern = re.compile(
            rf"\b(?P<subj_phrase>(?:the|this|that|a|an)?\s*(?:[A-Za-z0-9_]+\s+)?(?P<subject>{inanim_nouns}|[A-Za-z0-9_]+(?:\(\)|_test|_check)))\s+"
            rf"[A-Za-z0-9_]+\s+[^.;,]+\b(?:but|and)\s+(?:quietly|also|simply)?\s*(?P<verb>\b(?:{verb_stems})\b)",
            re.IGNORECASE
        )

    def check(self, text: str, line_offset: int = 1) -> List[Diagnostic]:
        diagnostics = []
        lines = text.splitlines()

        for idx, line in enumerate(lines):
            line_no = line_offset + idx
            if line.strip().startswith(("```", "#")):
                continue

            matches = list(self.pattern.finditer(line)) + list(self.coordination_pattern.finditer(line))
            
            # Deduplicate overlapping matches
            seen_spans = set()
            for m in matches:
                span = (m.start(), m.end())
                if span in seen_spans:
                    continue
                seen_spans.add(span)

                subj_raw = m.group("subject").lower().strip("()")
                verb_raw = m.group("verb").lower()

                # Check if subject is recognized as inanimate
                is_inanimate = (
                    subj_raw in INANIMATE_SUBJECTS or
                    subj_raw.endswith(("_test", "_check", "_script", "()", "_fn")) or
                    m.group("subject").endswith("()")
                )

                if is_inanimate and verb_raw in ANIMATE_AGENCY_VERBS:
                    matched_text = m.group(0).strip()
                    suggestion = (
                        f"Rephrase to attribute action to human authors (e.g. 'The developer omitted...'), "
                        f"or use a functional predicate (e.g. 'The {subj_raw} does not handle...', 'fails to...', 'is designed to...')"
                    )
                    diagnostics.append(
                        Diagnostic(
                            rule_id=self.rule_id,
                            message=(
                                f"Selectional restriction violation: Inanimate subject '{m.group('subject')}' "
                                f"paired with animate agency verb '{m.group('verb')}'"
                            ),
                            line_number=line_no,
                            column=m.start() + 1,
                            matched_text=matched_text,
                            cognitive_cost="Triggers a P600 ERP brainwave response indicating syntactic reanalysis and semantic repair (Kim & Osterhout 2005, Kuperberg 2007).",
                            suggestion=suggestion,
                            severity=self.severity,
                        )
                    )

        return diagnostics
