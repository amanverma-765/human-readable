# Readable

**Deterministic Psycholinguistic Readability Verifier & Agent Skill**

Grounded in the empirical cognitive science findings of **Clark, Martin, and Mahowald (2026)** (*"Why is AI-generated language so hard to understand?"*, arXiv:2610.29162), `readable` is a zero-dependency linter and coding agent skill that enforces human-readable prose by eliminating unnatural syntactic compression and the "Claudish" AI dialect.

---

## The Problem: Why AI Text Exhausts Human Readers

Modern frontier LLMs undergo post-training with Reinforcement Learning with Verifiable Rewards (RLVR) under token length penalties. While this optimizes models for mathematical reasoning and code correctness, it strips the communicative pressures that naturally evolved human language.

As a result, LLMs systematically overuse constructions that overload human working memory and force cognitive re-parsing:
1. **Selectional Restriction Violations:** Inanimate subjects paired with animate verbs (*"the check forgot bytes"*, *"the conversation eats its own tail"*), triggering a **P600 ERP brainwave** response indicating mental repair costs.
2. **Stacked Noun Compounds:** Sequences of 3+ nouns in modifier chains (*"reader-patience budget"*, *"brokerage money market funds"*), forcing hierarchical bracketing ambiguity ($[A\ [B\ C]]$ vs $[[A\ B]\ C]$).
3. **Reduced Object Relatives:** Dropping optional function words like *"that"* (*"the code we wrote"* vs *"the code that we wrote"*), violating **Uniform Information Density (UID)** and causing garden-path reading latency.
4. **Ad-Hoc Denominal Verbs:** Coercing nouns into verbs (*"calendar it"*, *"footnote it"*), requiring syntactic category disambiguation.
5. **Excessive Dependency Length:** Distant subject-verb separation (>8 intermediate words) and sentence sprawl (>30 words), depleting working memory under **Dependency Locality Theory (DLT)**.
6. **Claudish Cliches:** Stereotypical, low-frequency AI mannerisms (*"delve"*, *"verified red"*, *"quietly eating its own"*).

---

## Features

* **Zero External Dependencies:** Built 100% on the Python standard library. Runs out-of-the-box on Python 3.8+ with no heavy ML weights or external parsers.
* **Instant & Deterministic:** Audits text in $<10\text{ms}$, making it ideal for real-time agent loops, pre-commit hooks, and CI/CD pipelines.
* **Actionable Suggestions:** Provides line and column locations, cognitive rationale, and automated rewrite suggestions.
* **Agent Skill Ready:** Ships with `.agents/skills/human-readable/SKILL.md` for seamless activation in Antigravity, Claude Code, OpenCode, and Cursor.

---

## Installation & Setup

### Option 1: Single-Command via `npx` (Universal Agent Skills)

The fastest way to install into 70+ coding agents (Claude Code, Cursor, Antigravity, OpenCode, Copilot, Codex) using the open [skills CLI](https://skills.sh):

```bash
# Install to current project
npx skills add amanverma-765/readable --skill human-readable

# Or install globally across all agents
npx skills add -g amanverma-765/readable --skill human-readable
```

Or install directly from GitHub using `npx`:
```bash
# Install to current workspace (.agents/skills/ and skills/)
npx github:amanverma-765/readable install

# Or install globally to all detected agents (Claude Code, Antigravity, Cursor, OpenCode)
npx github:amanverma-765/readable install --global
```

### Option 2: Python Package (Local or CI)

```bash
# Clone and install locally
git clone https://github.com/your-org/readable.git
cd readable
pip install -e .
```

Or run directly without installation:
```bash
python3 -m readable <files|string>
# or via npx:
npx human-readable <files|string>
```

---

## CLI Usage

### Check an Inline String
```bash
python3 -m readable -s "Your instinct is right; the convoluted sentence you are currently reading is quietly eating its own reader-patience budget — footnote it."
```

**Output:**
```
Line 1:25 [selectional-restriction] (ERROR)
  "the convoluted sentence you are currently reading is quietly eating"
  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  Why: Selectional restriction violation: Inanimate subject 'sentence' paired with animate agency verb 'eating'
  Cognitive Cost: Triggers a P600 ERP brainwave response indicating syntactic reanalysis and semantic repair (Kim & Osterhout 2005, Kuperberg 2007).
  Suggestion: Rephrase to attribute action to human authors (e.g. 'The developer omitted...'), or use a functional predicate (e.g. 'The sentence does not handle...', 'fails to...', 'is designed to...')

Line 1:40 [reduced-relative] (WARNING)
  "sentence you are"
  ^^^^^^^^^^^^^^^^
  Why: Reduced object relative clause omitting 'that': 'sentence you are'
  Cognitive Cost: Reduced ORCs create non-canonical order without overt marking, depleting human working memory and triggering garden-path regressions (Staub 2010).
  Suggestion: Insert overt relativizer 'that': 'sentence that you are'

Line 1:78 [claudish-jargon] (WARNING)
  "quietly eating its own"
  ^^^^^^^^^^^^^^^^^^^^^^
  Why: Overused AI dialect marker / cliche: 'quietly eating its own'
  Cognitive Cost: High surprisal and low communicative value; creates reader fatigue and signals artificial dialect (Juzek & Ward 2025, Clark et al. 2026).
  Suggestion: Overused AI metaphor violating selectional restrictions and natural register. Rewrite using direct, plain, natural phrasing.

Line 1:101 [stacked-nouns] (WARNING)
  "reader-patience budget"
  ^^^^^^^^^^^^^^^^^^^^^^
  Why: Stacked noun compound (3 nouns modifying each other): 'reader-patience budget'
  Cognitive Cost: Forces hierarchical bracketing ambiguity ([A [B C]] vs [[A B] C]) and causes eye-fixation reading regressions (Cooper 1980, Staub et al. 2007).
  Suggestion: Unpack the compound into a prepositional phrase, e.g., 'budget for/of reader-patience'

Line 1:126 [denominal-verb] (WARNING)
  "footnote it"
  ^^^^^^^^^^^
  Why: Ad-hoc denominal verb conversion: 'footnote it'
  Cognitive Cost: Forces syntactic category disambiguation, triggering late-stage syntactic re-parsing (Thierry et al. 2008, Federmeier et al. 2000).
  Suggestion: Replace with standard verbal phrase: 'add a footnote to'

Readable Summary: 5 violation(s) found (1 error(s), 4 warning(s)).
```

### Check Markdown Files & Directories
```bash
# Check single file
python3 -m readable docs/explanation.md

# Check directory recursively
python3 -m readable docs/

# Read from standard input
git diff main | python3 -m readable -
```

### Strict Mode for CI / Quality Gates
```bash
# Return exit code 1 on ANY violation (errors or warnings)
python3 -m readable --strict docs/
```

### GitHub Actions Annotations
```bash
python3 -m readable --format github docs/
```

---

## Agent Skill Integration

This repository includes the skill definition in:
- `.agents/skills/human-readable/SKILL.md`
- `skills/human-readable/SKILL.md`

### How Coding Agents Use It:
1. When generating explanations, pull request bodies, or technical documentation, the agent loads the `human-readable` skill.
2. The agent follows the positive target patterns (explicit *"that"*, unpacked nouns, human agency alignment).
3. Before returning control to the user, the agent invokes `python3 -m readable --strict` on its proposed output.
4. If violations are detected, the agent applies the suggested rewrites until the output is clean.

---

## License

MIT
