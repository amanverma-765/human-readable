"""Unit tests verifying readability rules against paper Table 2 and Figure 1 examples."""

import unittest
from readable.checker import ReadabilityChecker
from readable.rules.stacked_nouns import StackedNounsRule
from readable.rules.selectional_restrictions import SelectionalRestrictionsRule
from readable.rules.reduced_relatives import ReducedRelativesRule
from readable.rules.denominal_verbs import DenominalVerbsRule
from readable.rules.dependency_distance import DependencyDistanceRule
from readable.rules.claudish_jargon import ClaudishJargonRule


class TestReadabilityRules(unittest.TestCase):

    def setUp(self):
        self.checker = ReadabilityChecker()

    def test_motivating_example_all_five_violations(self):
        """The motivating example sentence embodies 5 distinct psycholinguistic violations."""
        text = (
            "Your instinct is right; the convoluted sentence you are currently reading "
            "is quietly eating its own reader-patience budget — footnote it."
        )
        diags = self.checker.check_text(text)
        rule_ids = {d.rule_id for d in diags}
        
        self.assertIn("selectional-restriction", rule_ids)
        self.assertIn("reduced-relative", rule_ids)
        self.assertIn("claudish-jargon", rule_ids)
        self.assertIn("stacked-nouns", rule_ids)
        self.assertIn("denominal-verb", rule_ids)

    def test_stacked_nouns_from_paper(self):
        rule = StackedNounsRule()
        
        # Table 2: Opus 5
        diags = rule.check("Online banks or brokerage money market funds are standard options.")
        self.assertTrue(any("brokerage money market funds" in d.matched_text for d in diags))

        # Table 2: Kimi
        diags = rule.check("Policy 1's class-time shutdown requirement directly addresses this.")
        self.assertTrue(len(diags) > 0)

        # Table 2: GLM-5
        diags = rule.check("Summer park district classes are popular.")
        self.assertTrue(len(diags) > 0)

        # Figure 1: Sonnet 5
        diags = rule.check("You installed a horror movie soundtrack generator in your skull.")
        self.assertTrue(len(diags) > 0)

    def test_selectional_restrictions_from_paper(self):
        rule = SelectionalRestrictionsRule()

        # Table 2: Sol (GPT-5.6)
        diags = rule.check("Sometimes chaos expects you to remember it independently.")
        self.assertTrue(any("chaos expects" in d.matched_text.lower() for d in diags))

        # Table 2: Opus 5.5
        diags = rule.check("These are the exact skills the worksheet hoped to teach.")
        self.assertTrue(any("worksheet hoped" in d.matched_text.lower() for d in diags))

        # Table 2: Fable 5
        diags = rule.check("The docstring promises they are skipped.")
        self.assertTrue(any("docstring promises" in d.matched_text.lower() for d in diags))

        # Figure 1: Opus 5
        diags = rule.check("The whole conversation is eating its own tail.")
        self.assertTrue(any("conversation is eating" in d.matched_text.lower() for d in diags))

    def test_reduced_relatives_from_paper(self):
        rule = ReducedRelativesRule()

        # Table 2: Kimi
        diags = rule.check("That's leave the job you hate money.")
        self.assertTrue(any("job you hate" in d.matched_text for d in diags))

        # Table 2: Opus 5.5
        diags = rule.check("The others check behaviour the old code never reached.")
        self.assertTrue(any("behaviour the old code" in d.matched_text or "code never reached" in d.matched_text for d in diags))

        # Epistemic complement clause omitting 'that'
        diags = rule.check("The engineer was sure the door was locked.")
        self.assertTrue(any("sure the door was locked" in d.matched_text for d in diags))

        # Purpose clause omitting 'that'
        diags = rule.check("He spoke slowly so we could follow along.")
        self.assertTrue(any("so we could" in d.matched_text for d in diags))

    def test_denominal_verbs_from_paper(self):
        rule = DenominalVerbsRule()

        # Figure 1: Fable 5
        diags = rule.check("So yes — calendar it right away.")
        self.assertTrue(any("calendar it" in d.matched_text for d in diags))

        # Table 2: Sonnet 5
        diags = rule.check("Don't try to get her to categorize movies as speed-runnable or not.")
        self.assertTrue(any("speed-runnable" in d.matched_text for d in diags))

        # Table 2: Fable 5
        diags = rule.check("Backing up a dotfolder was not skipped.")
        self.assertTrue(any("dotfolder" in d.matched_text for d in diags))

    def test_dependency_distance(self):
        rule = DependencyDistanceRule()

        # Table 2: Sonnet 5 center-embedded dependency
        diags = rule.check("The guitar sitting in the corner because you're still deciding teaches you zero chords.")
        self.assertTrue(any("teaches" in d.matched_text for d in diags))

        # Sentence sprawl (>32 words)
        long_sentence = (
            "When we examined the historical performance characteristics across all sixty distributed node clusters "
            "during the multi-region stress experiment without introducing any simulated latency degradation or simulated "
            "packet drops we observed substantial tail latency variance."
        )
        diags = rule.check(long_sentence)
        self.assertTrue(any("Sentence sprawl" in d.message for d in diags))

    def test_claudish_jargon(self):
        rule = ClaudishJargonRule()

        diags = rule.check("Let's delve into the intricacies of this implementation.")
        self.assertTrue(any("delve" in d.matched_text.lower() for d in diags))

        diags = rule.check("It's important to remember that this algorithm scales quadratically.")
        self.assertTrue(any("important to remember" in d.matched_text.lower() for d in diags))

        diags = rule.check("Every behavioral test was verified red against the original source.")
        self.assertTrue(any("verified red" in d.matched_text.lower() for d in diags))

    def test_clean_human_sentences_pass(self):
        clean_text = (
            "We found three bugs in the parser.\n"
            "The developer scheduled the meeting on the calendar.\n"
            "This is the book that the professor wrote.\n"
            "The engineer confirmed that the unit tests pass.\n"
            "We updated the budget for patient care.\n"
        )
        diags = self.checker.check_text(clean_text)
        self.assertEqual(len(diags), 0)


if __name__ == "__main__":
    unittest.main()
