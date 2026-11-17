"""Curated lexical sets and linguistic dictionaries for deterministic readability checking."""

# 1. Inanimate & technical entities frequently used as subjects in AI code/tech discourse
INANIMATE_SUBJECTS = {
    "sentence", "paragraph", "text", "docstring", "comment", "file",
    "script", "program", "code", "function", "method", "class", "module",
    "check", "test", "suite", "assertion", "linter", "compiler", "parser",
    "grammar", "rule", "regex", "pattern", "type", "variable", "value",
    "exception", "error", "patch", "commit", "diff", "branch", "pull request",
    "repository", "repo", "library", "framework", "database", "query",
    "server", "endpoint", "pipeline", "process", "algorithm", "model",
    "policy", "worksheet", "objection", "argument", "premise", "chaos",
    "song", "asymmetry", "system", "lattice", "symbolset", "it", "this",
    "expression", "line", "token", "string", "condition", "loop", "conversation",
}

# 2. Verbs requiring animate volition, conscious experience, perception, or physical agency
ANIMATE_AGENCY_VERBS = {
    # Physical consumption / eating / biting
    "eat", "eats", "eating", "ate", "eaten",
    "swallow", "swallows", "swallowing", "swallowed",
    "bite", "bites", "biting", "bit", "bitten",
    "chew", "chews", "chewing", "chewed",
    "ingest", "ingests", "ingesting", "ingested",
    "digest", "digests", "digesting", "digested",
    "consume", "consumes", "consuming", "consumed",

    # Psychological / cognitive / affective states
    "forget", "forgets", "forgetting", "forgot", "forgotten",
    "expect", "expects", "expecting", "expected",
    "hope", "hopes", "hoping", "hoped",
    "misunderstand", "misunderstands", "misunderstanding", "misunderstood",
    "believe", "believes", "believing", "believed",
    "desire", "desires", "desiring", "desired",
    "worry", "worries", "worrying", "worried",
    "fear", "fears", "fearing", "feared",
    "dream", "dreams", "dreaming", "dreamed", "dreamt",
    "wish", "wishes", "wishing", "wished",
    "regret", "regrets", "regretting", "regretted",
    "feel", "feels", "feeling", "felt",
    "decide", "decides", "deciding", "decided",
    "intend", "intends", "intending", "intended",
    "pretend", "pretends", "pretending", "pretended",

    # Human interpersonal actions
    "promise", "promises", "promising", "promised",
    "ask", "asks", "asking", "asked",
    "tell", "tells", "telling", "told",
    "whisper", "whispers", "whispering", "whispered",
    "apologize", "apologizes", "apologizing", "apologized",
    "scold", "scolds", "scolding", "scolded",
    "beg", "begs", "begging", "begged",
}

# 3. Ad-hoc denominal verbs (nouns inappropriately converted to verbs)
AD_HOC_DENOMINAL_VERBS = {
    "footnote", "footnotes", "footnoting", "footnoted",
    "calendar", "calendars", "calendaring", "calendared",
    "dotfolder", "dotfolders", "dotfoldering", "dotfoldered",
    "speedrun", "speedruns", "speedrunning", "speedrunnable",
    "action", "actions", "actioning", "actioned",
    "agenda", "agendas", "agendaing", "agendaed",
    "packetize", "packetizes", "packetizing", "packetized",
    "solution", "solutions", "solutioning", "solutioned",
    "effort", "efforts", "efforting", "efforted",
    "headquarter", "headquarters", "headquartering", "headquartered",
    "sunset", "sunsets", "sunsetting", "sunsetted",
    "impact", "impacts", "impacting", "impacted",
}

# 4. Words frequently acting as heads in complement clauses where optional "that" is dropped
COMPLEMENT_HEAD_VERBS = {
    "know", "knows", "knew", "known",
    "notice", "notices", "noticed",
    "find", "finds", "found",
    "realize", "realizes", "realized",
    "see", "sees", "saw", "seen",
    "believe", "believes", "believed",
    "conclude", "concludes", "concluded",
    "discover", "discovers", "discovered",
    "state", "states", "stated",
    "confirm", "confirms", "confirmed",
    "verify", "verifies", "verified",
    "ensure", "ensures", "ensured",
    "observe", "observes", "observed",
    "recognize", "recognizes", "recognized",
    "feel", "feels", "felt",
}

COMPLEMENT_HEAD_ADJECTIVES = {
    "sure", "certain", "confident", "aware", "clear", "obvious",
    "evident", "convinced", "positive", "doubtful", "glad", "happy",
    "proud", "afraid", "worried",
}

# 5. Overused Claudish cliches and low-frequency n-gram mannerisms
CLAUDISH_CLICHES = [
    (r"\bquietly eating its own\b", "Overused AI metaphor violating selectional restrictions and natural register."),
    (r"\beating its own tail\b", "Cliche ouroboros idiom overused in AI model explanations."),
    (r"\bverified red\b", "Unattested low-frequency n-gram jargon; use standard 'failing test' or 'verified failure'."),
    (r"\bdelve\b|\bdelving\b", "High-frequency AI marker word rarely used in standard technical prose."),
    (r"\bserves as a testament to\b", "Inflated, formulaic AI boilerplate; use direct phrasing."),
    (r"\ba tapestry of\b|\brich tapestry\b", "Hyperbolic AI metaphor; specify actual components directly."),
    (r"\bbeacon of\b", "Melodramatic AI prose; state the actual virtue directly."),
    (r"\bnavigate the complexities of\b", "Pompous AI filler phrase; prefer 'handle' or 'address'."),
    (r"\bit(?:'s| is) important to remember that\b", "Verbose, patronizing AI padding; state the point directly."),
    (r"\bit is worth noting that\b", "Unnecessary passive throat-clearing; state the fact directly."),
    (r"\bin summary, it can be said that\b", "Stilted essay conclusion boilerplate."),
    (r"\btestament to the fact that\b", "Wordy, inflated AI construct."),
    (r"\bfirst and foremost\b", "Formulaic essay transition marker."),
]

# 6. Stopwords and determiners for syntactic boundary checking
DETERMINERS = {
    "the", "a", "an", "this", "that", "these", "those", "my", "your",
    "his", "her", "its", "our", "their", "any", "all", "every", "some",
    "no", "each", "both",
}

PREPOSITIONS = {
    "in", "on", "at", "to", "for", "with", "by", "from", "about", "into",
    "through", "during", "before", "after", "above", "below", "between",
    "under", "across", "without", "against", "towards", "upon", "within",
    "of", "via",
}

CONJUNCTIONS = {
    "and", "or", "but", "nor", "so", "yet", "for", "because", "although",
    "since", "unless", "while", "whereas",
}

PRONOUNS_SUBJECT = {
    "i", "you", "he", "she", "it", "we", "they", "who", "what",
}

PRONOUNS_OBJECT = {
    "me", "you", "him", "her", "it", "us", "them", "whom",
}
