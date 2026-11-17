"""Integration tests for readable CLI."""

import json
import subprocess
import sys
import unittest
from pathlib import Path


class TestReadableCLI(unittest.TestCase):

    def run_cli(self, *args, stdin_data=None):
        cmd = [sys.executable, "-m", "readable"] + list(args)
        proc = subprocess.run(
            cmd,
            input=stdin_data,
            capture_output=True,
            text=True,
        )
        return proc

    def test_clean_string_returns_zero(self):
        res = self.run_cli("-s", "We found three clean bugs in the parser and fixed them.")
        self.assertEqual(res.returncode, 0)
        self.assertIn("Clean!", res.stdout)

    def test_violation_string_returns_one(self):
        res = self.run_cli("-s", "The script forgot to clean up its temp files.")
        self.assertEqual(res.returncode, 1)
        self.assertIn("[selectional-restriction]", res.stdout)

    def test_json_format(self):
        res = self.run_cli("-s", "Calendar it right away.", "--format", "json")
        self.assertEqual(res.returncode, 0)  # Warning only, without --strict
        data = json.loads(res.stdout)
        self.assertIsInstance(data, list)
        self.assertTrue(len(data) > 0)
        self.assertEqual(data[0]["rule_id"], "denominal-verb")

    def test_strict_mode_fails_on_warning(self):
        res = self.run_cli("-s", "Calendar it right away.", "--strict")
        self.assertEqual(res.returncode, 1)

    def test_github_format(self):
        res = self.run_cli("-s", "Let us delve into this topic.", "--format", "github")
        self.assertIn("::warning line=1,col=", res.stdout)
        self.assertIn("title=[claudish-jargon]", res.stdout)

    def test_rule_filtering(self):
        # Text has both stacked nouns and claudish jargon
        text = "Let us delve into our reader patience budget."
        # Enable only stacked-nouns
        res = self.run_cli("-s", text, "--rule", "stacked-nouns")
        self.assertIn("[stacked-nouns]", res.stdout)
        self.assertNotIn("[claudish-jargon]", res.stdout)

    def test_node_cli_installer(self):
        import tempfile
        import os
        cli_js = Path(__file__).parent.parent / "bin" / "cli.js"
        with tempfile.TemporaryDirectory() as tmpdir:
            res = subprocess.run(
                ["node", str(cli_js), "install"],
                cwd=tmpdir,
                capture_output=True,
                text=True,
            )
            self.assertEqual(res.returncode, 0)
            self.assertIn("Successfully installed", res.stdout)
            agent_dest = Path(tmpdir) / ".agents" / "skills" / "human-readable" / "SKILL.md"
            skill_dest = Path(tmpdir) / "skills" / "human-readable" / "SKILL.md"
            self.assertTrue(agent_dest.exists())
            self.assertTrue(skill_dest.exists())

    def test_node_cli_verify(self):
        cli_js = Path(__file__).parent.parent / "bin" / "cli.js"
        res = subprocess.run(
            ["node", str(cli_js), "-s", "We wrote three clean tests."],
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("Clean!", res.stdout)


if __name__ == "__main__":
    unittest.main()
