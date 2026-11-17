"""Rule 1: Stacked Noun Compound Detector.

Detects sequences of 3 or more consecutive nouns in modifier relationships
(e.g., 'reader-patience budget', 'brokerage money market funds').
"""

import re
from typing import List
from readable.rules.base import Rule, Diagnostic
from readable.lexicon import DETERMINERS, PREPOSITIONS, CONJUNCTIONS


# Common non-noun words to exclude from noun chains
EXCLUDED_NON_NOUNS = {
    # Pronouns & determiners
    "it", "this", "that", "these", "those", "they", "them", "he", "she", "we", "us",
    "i", "you", "my", "your", "his", "her", "its", "our", "their", "all", "each",
    "every", "some", "any", "no", "both", "few", "many", "several",
    # Common adjectives that do not act as nominal heads
    "new", "old", "good", "bad", "great", "small", "large", "big", "high", "low",
    "long", "short", "different", "same", "able", "recent", "early", "late", "important",
    "major", "hard", "easy", "clear", "simple", "complex", "possible", "substantive",
    "unfixed", "pre-existing", "existing", "dry-run", "lazy-intermediate",
    # Auxiliary & common verbs
    "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
    "do", "does", "did", "can", "could", "will", "would", "shall", "should", "may", "might", "must",
    # Adverbs
    "not", "very", "too", "also", "just", "only", "even", "more", "most", "less",
    "now", "then", "here", "there", "quietly", "honestly", "really", "primarily",
}

# Suffixes strongly indicative of nouns
NOUN_SUFFIXES = (
    "tion", "sion", "ment", "ity", "ence", "ance", "er", "or", "ist",
    "ism", "ship", "ness", "age", "hood", "ure", "fund", "funds", "cord",
    "cords", "item", "items", "file", "files", "path", "paths", "room",
    "rooms", "time", "times", "class", "classes", "park", "district",
    "budget", "market", "policy", "code", "line", "lines", "tag", "tags",
    "list", "lists", "fallback", "hook", "hooks", "hookup", "reinstall",
    "reinstalls", "shutdown", "requirement", "requirements", "movie",
    "soundtrack", "generator", "option", "options", "patience", "reader",
    "service", "district", "handling", "prevention", "point", "points",
    "label", "labels", "mapping", "mappings", "error", "message",
)

# Known common nouns
KNOWN_NOUNS = {
    "brokerage", "money", "market", "funds", "fund", "reader", "patience",
    "budget", "class", "time", "shutdown", "requirement", "requirements",
    "park", "district", "classes", "horror", "movie", "soundtrack", "generator",
    "dotfile", "backup", "path", "handling", "prevention", "reinstall", "reinstalls",
    "community", "service", "honor", "cord", "summer", "school", "cell", "phone",
    "policy", "error", "message", "string", "literals", "literal", "tag",
    "instance", "lookup", "behavior", "git", "hook", "hooks", "branch",
    "test", "tests", "data", "system", "user", "agent", "model", "prompt",
    "token", "tokens", "database", "server", "cache", "network", "client",
    "hardware", "software", "memory", "storage", "file", "directory", "folder",
}


def is_candidate_noun(word: str) -> bool:
    """Heuristic check if a word is functioning as a noun in a compound."""
    w = word.lower().strip(",.:;!?'\"()[]{}")
    if not w or len(w) < 2:
        return False
    if w in EXCLUDED_NON_NOUNS or w in DETERMINERS or w in PREPOSITIONS or w in CONJUNCTIONS:
        return False
    if w in KNOWN_NOUNS:
        return True
    if any(w.endswith(sfx) for sfx in NOUN_SUFFIXES):
        return True
    # If it contains hyphens (e.g. class-time, reader-patience), test constituent parts
    if "-" in w:
        subparts = [p for p in w.split("-") if p]
        return any(is_candidate_noun(p) for p in subparts)
    return False


class StackedNounsRule(Rule):
    """Flags 3 or more consecutive nouns acting in a modifier chain."""
    rule_id = "stacked-nouns"
    description = "Sequences of 3 or more nouns in a modifier relationship."
    severity = "warning"

    def check(self, text: str, line_offset: int = 1) -> List[Diagnostic]:
        diagnostics = []
        lines = text.splitlines()

        for idx, line in enumerate(lines):
            line_no = line_offset + idx
            # Tokenize into words while keeping hyphenated compounds intact
            # We skip code blocks or lines starting with ``` or #
            if line.strip().startswith(("```", "#", "http://", "https://")):
                continue

            # Split line into tokens with position tracking
            tokens_with_spans = [
                (m.group(), m.start(), m.end())
                for m in re.finditer(r"[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*", line)
            ]

            i = 0
            while i < len(tokens_with_spans):
                token, start, end = tokens_with_spans[i]

                # Check if this token starts a noun sequence
                if is_candidate_noun(token):
                    chain = [tokens_with_spans[i]]
                    j = i + 1
                    while j < len(tokens_with_spans):
                        next_token, n_start, n_end = tokens_with_spans[j]
                        # Verify tokens are contiguous (only whitespace or single hyphen between them)
                        gap = line[chain[-1][2]:n_start]
                        if not re.match(r"^\s*$", gap):
                            break
                        if is_candidate_noun(next_token):
                            chain.append(tokens_with_spans[j])
                            j += 1
                        else:
                            break

                    # Count how many noun heads/stems are in the chain
                    # Expand hyphenated words: e.g. 'reader-patience' counts as 2 nouns
                    total_nouns = sum(len(c[0].split("-")) if "-" in c[0] else 1 for c in chain)

                    if total_nouns >= 3:
                        matched_str = line[chain[0][1]:chain[-1][2]]
                        # Construct a suggestion
                        words = [c[0] for c in chain]
                        suggestion = (
                            f"Unpack the compound into a prepositional phrase, e.g., "
                            f"'{words[-1]} for/of {' '.join(words[:-1])}'"
                        )
                        diagnostics.append(
                            Diagnostic(
                                rule_id=self.rule_id,
                                message=f"Stacked noun compound ({total_nouns} nouns modifying each other): '{matched_str}'",
                                line_number=line_no,
                                column=chain[0][1] + 1,
                                matched_text=matched_str,
                                cognitive_cost="Forces hierarchical bracketing ambiguity ([A [B C]] vs [[A B] C]) and causes eye-fixation reading regressions (Cooper 1980, Staub et al. 2007).",
                                suggestion=suggestion,
                                severity=self.severity,
                            )
                        )
                        i = j
                        continue
                i += 1

        return diagnostics
