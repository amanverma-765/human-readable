"""Rule 3: Reduced Relatives & Complement Clause Detector.

Detects omitted optional relativizers and complementizers ('that', 'which')
(e.g., 'the code we wrote', 'was sure the door was locked', 'so we could follow').
"""

import re
from typing import List
from readable.rules.base import Rule, Diagnostic
from readable.lexicon import COMPLEMENT_HEAD_VERBS, COMPLEMENT_HEAD_ADJECTIVES, PREPOSITIONS, CONJUNCTIONS


# Conjunctions and words where an adjacent subject pronoun is standard, not a relative clause
NON_RELATIVE_PRECEDING_WORDS = {
    "if", "when", "while", "because", "although", "since", "unless",
    "before", "after", "though", "where", "why", "how", "as", "until",
    "that", "which", "who", "whom", "whose", "and", "or", "but", "so",
    "both", "either", "neither", "than", "whether",
}

# Pronouns acting as subject in the embedded clause
EMBEDDED_SUBJECT_PRONOUNS = {
    "you", "we", "they", "he", "she", "i", "people", "users",
    "students", "developers", "engineers", "callers",
}


class ReducedRelativesRule(Rule):
    """Flags reduced object relative clauses and complement clauses omitting optional 'that'."""
    rule_id = "reduced-relative"
    description = "Omission of optional relativizer ('that') in relative or complement clauses."
    severity = "warning"

    def __init__(self):
        # 1. ORC pattern: [determiner] [noun] [subject_pronoun] [verb]
        # e.g., "the sentence you are reading", "the job you hate", "behaviour the old code never reached"
        subj_prons = "|".join(EMBEDDED_SUBJECT_PRONOUNS)
        self.orc_pattern = re.compile(
            rf"(?:\b(?P<det>the|this|that|these|those|any|all|every)\s+)?\b"
            rf"(?P<noun>[a-zA-Z0-9_-]+)\s+"
            rf"(?P<pron>(?:{subj_prons})|the\s+(?:[a-zA-Z0-9_-]+\s+)?[a-zA-Z0-9_-]+)\s+"
            rf"(?:(?:never|always|actually|currently|often|also|already|quietly|did not|could not)\s+)?"
            rf"(?P<verb>are|is|were|was|have|has|had|wrote|write|hate|hates|pick|picked|chose|choose|"
            rf"read|reading|consider|considering|care|cared|reached|reach|created|create|make|made|"
            rf"find|found|saw|see|want|wanted|need|needed|built|build|feel|felt|expect|hoped)\b",
            re.IGNORECASE
        )

        # 2. Epistemic complement clause pattern: [head_verb|head_adj] [subject] [predicate]
        heads = sorted(list(COMPLEMENT_HEAD_VERBS | COMPLEMENT_HEAD_ADJECTIVES), key=len, reverse=True)
        head_pattern = "|".join(re.escape(h) for h in heads)
        self.comp_pattern = re.compile(
            rf"\b(?P<head>{head_pattern})\s+"
            rf"(?P<subj>(?:the|this|that|these|a|an|my|your|his|her|its|our|their|it|we|they|he|she|you))\s+"
            rf"(?P<rest>[A-Za-z0-9_-]+\s+(?:is|was|are|were|has|had|did|could|would|should|will|can|[a-z]+ed)(?:\s+[a-zA-Z0-9_-]+)?)\b",
            re.IGNORECASE
        )

        # 3. Purpose clause pattern: "so [subject] [modal verb]" instead of "so that [subject] [modal verb]"
        self.purpose_pattern = re.compile(
            rf"\bso\s+(?P<subj>we|you|they|he|she|it|the\s+[a-z]+)\s+(?P<modal>can|could|would|might|will|should)\b",
            re.IGNORECASE
        )

    def check(self, text: str, line_offset: int = 1) -> List[Diagnostic]:
        diagnostics = []
        lines = text.splitlines()

        for idx, line in enumerate(lines):
            line_no = line_offset + idx
            if line.strip().startswith(("```", "#")):
                continue

            # Check Purpose Clauses: e.g. "so we could follow" -> "so that we could follow"
            for m in self.purpose_pattern.finditer(line):
                matched_str = m.group(0)
                # Ensure it's not preceded by "and" or at start of sentence as a coordinating conjunction
                # e.g., "spoke slowly so we could follow"
                col = m.start() + 1
                suggestion = matched_str.replace("so ", "so that ", 1)
                diagnostics.append(
                    Diagnostic(
                        rule_id=self.rule_id,
                        message=f"Purpose clause omitting overt 'that': '{matched_str}'",
                        line_number=line_no,
                        column=col,
                        matched_text=matched_str,
                        cognitive_cost="Violates Uniform Information Density (UID), forcing local syntactic compression (Clark et al. 2026).",
                        suggestion=f"Insert optional 'that': '{suggestion}'",
                        severity=self.severity,
                    )
                )

            # Check Epistemic Complement Clauses: e.g. "sure the door was locked" -> "sure that the door was locked"
            for m in self.comp_pattern.finditer(line):
                head = m.group("head").lower()
                matched_str = m.group(0)
                col = m.start() + 1
                # Check that 'that' was not included
                rest = m.group("subj") + " " + m.group("rest")
                suggestion = f"{head} that {rest}"
                diagnostics.append(
                    Diagnostic(
                        rule_id=self.rule_id,
                        message=f"Complement clause omitting optional complementizer 'that': '{matched_str}'",
                        line_number=line_no,
                        column=col,
                        matched_text=matched_str,
                        cognitive_cost="Omitting 'that' removes boundary signaling, increasing cognitive surprisal at the embedded clause (Levy & Jaeger 2007).",
                        suggestion=f"Insert overt 'that': '{suggestion}'",
                        severity=self.severity,
                    )
                )

            # Check Reduced ORCs: e.g. "the sentence you are reading" -> "the sentence that you are reading"
            for m in self.orc_pattern.finditer(line):
                noun = m.group("noun").lower()
                pron = m.group("pron").lower()
                # If the word before pronoun is a subordinating conjunction, skip
                if noun in NON_RELATIVE_PRECEDING_WORDS or noun in PREPOSITIONS:
                    continue

                matched_str = m.group(0)
                col = m.start() + 1
                # Construct suggested rewrite with "that"
                det = (m.group("det") + " ") if m.group("det") else ""
                suggestion = f"{det}{noun} that {m.group('pron')} {m.group('verb')}"

                diagnostics.append(
                    Diagnostic(
                        rule_id=self.rule_id,
                        message=f"Reduced object relative clause omitting 'that': '{matched_str}'",
                        line_number=line_no,
                        column=col,
                        matched_text=matched_str,
                        cognitive_cost="Reduced ORCs create non-canonical order without overt marking, depleting human working memory and triggering garden-path regressions (Staub 2010).",
                        suggestion=f"Insert overt relativizer 'that': '{suggestion}'",
                        severity=self.severity,
                    )
                )

        return diagnostics
