"""Readable: Deterministic psycholinguistic readability linter and verifier."""

from readable.checker import ReadabilityChecker
from readable.rules.base import Diagnostic, Rule

__version__ = "0.1.0"
__all__ = ["ReadabilityChecker", "Diagnostic", "Rule", "__version__"]
