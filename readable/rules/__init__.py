"""Readability verification rules."""

from readable.rules.base import Rule, Diagnostic
from readable.rules.stacked_nouns import StackedNounsRule
from readable.rules.selectional_restrictions import SelectionalRestrictionsRule
from readable.rules.reduced_relatives import ReducedRelativesRule
from readable.rules.denominal_verbs import DenominalVerbsRule
from readable.rules.dependency_distance import DependencyDistanceRule
from readable.rules.claudish_jargon import ClaudishJargonRule

ALL_RULES = [
    SelectionalRestrictionsRule,
    StackedNounsRule,
    ReducedRelativesRule,
    DenominalVerbsRule,
    DependencyDistanceRule,
    ClaudishJargonRule,
]

__all__ = [
    "Rule",
    "Diagnostic",
    "StackedNounsRule",
    "SelectionalRestrictionsRule",
    "ReducedRelativesRule",
    "DenominalVerbsRule",
    "DependencyDistanceRule",
    "ClaudishJargonRule",
    "ALL_RULES",
]
