POLICY_SUFFIXES = [
    'act',
    'agreement',
    'charter',
    'code',
    'condition',
    'constitution',
    'contract',
    'declaration',
    'directive',
    'guide',
    'guideline',
    'licence',
    'license',
    'manual',
    'note',
    'notice',
    'plan',
    'policy',
    'principle',
    'regulation',
    'rule',
    'statement',
    'statute',
    'strategy',
    'term'
]

ORG_SUFFIXES = [
    "office",
    "department",
    "division",
    "unit",
    "center",
    "centre",
    "institute",
    "agency",
    "authority",
    "committee",
    "board",
    "administration",
    "service",
    "bureau",
    "directorate",
    "commission",
    "organisation",
    "organization",
    "university",
    "college",
    "laboratory",
    "lab"
]

policy_patterns = []

suffix_lemma_rule = {"LEMMA": {"IN":POLICY_SUFFIXES, "IS_UPPER": False}}

suffix_regex_rule = {
    "TEXT": {
        "REGEX": r"(?i)\b(practice|condition|term|rule|agreement|license|licence|notice|principle|guideline|guide|statement|statute|regulation|charter|directive|contract|act|code|constitution|note|manual|declaration)s?\b|\bpolic(y|ies)\b"
    }
}

uppercase_org_acronym = {
    "label": "ACR",
    "pattern": [{"TEXT": {"REGEX": r"^[A-Z\-\\]{2,8}$"}}]
}

up_to_three_nouns_not_suffix = {
    "POS": {"IN": ["NOUN", "PROPN"]},
    "LOWER": {"NOT_IN": POLICY_SUFFIXES},
    "OP": "{1,3}",
    "IS_UPPER": False
}


policy_patterns = [
    {
        "label": "POLICY",
        "id": "1_single_noun_or_adj_suffix",
        "pattern": [
            {"POS": {"IN": ["ADJ","NOUN","PROPN"]},"IS_UPPER": False},
            suffix_regex_rule
        ]
    },
    {
        "label": "POLICY",
        "id": "8_modified_suffix_and nouns",
        "pattern": [
            {"LOWER": {
                "IN": ["best", "common", "good", "fair", "general", "accepted", "standard", "recommended", "basic"]}},
            suffix_regex_rule,
            up_to_three_nouns_not_suffix
        ]
    },
    {
        "label": "POLICY",
        "id": "two_noun_or_adj_suffix",
        "pattern": [
            {"POS": "ADJ", "OP": "?", "IS_UPPER": False},
            up_to_three_nouns_not_suffix,
            suffix_regex_rule
        ]
    },
    {
        "label": "POLICY",
        "id": "3_single_noun_or_adj_and_suffix",
        "pattern":
    # WITH coordination
        [
            {"POS": {"IN": ["ADJ", "NOUN", "PROPN"]}, "OP": "{1,2}", "IS_UPPER": False},
            {"LOWER": {"IN": ["and", "&"]}},
            {"POS": {"IN": ["ADJ", "NOUN", "PROPN"]}},
            suffix_regex_rule
        ]
    },
    {
        "label": "POLICY",
        "id": "4_single_noun_or_adj_of_suffix",
        "pattern": [
            # e.g. general
            {"POS": "ADJ", "OP": "?"},
            # Head noun (policy-related)
            suffix_regex_rule,
            # Optional 'of'
            {"LOWER": {"IN": ["of", "for", "on", "to", "in"]}},
            # Optional descriptive noun(s) or proper noun(s)
            {"POS": {"IN": ["ADJ"]}, "OP": "?"},
            up_to_three_nouns_not_suffix
        ]
    },
    {
        "label": "POLICY",
        "id": "5_single_noun_or_adj_and_of_suffix",
        "pattern":
    # WITH coordination
        [
            suffix_regex_rule,
            {"LOWER": {"IN": ["and", "&"]}},
            suffix_regex_rule,
            {"LOWER": {"IN": ["of", "for", "on", "to", "in"]}},
            {"LOWER": {"IN": ["the"]}, "OP": "?"},
            # Optional descriptive noun(s) or proper noun(s),
            {"POS": {"IN": ["ADJ"]}, "OP": "?"},
            up_to_three_nouns_not_suffix
        ]

    },
    {
        "label": "POLICY",
        "id": "6_suffix_and_suffix",
        "pattern":
            # WITH coordination
            [
                suffix_regex_rule,
                {"LOWER": {"IN": ["and", "&"]}},
                suffix_regex_rule
            ]
    },
    {
        "label": "POLICY",
        "id": "7_modifier_suffix_and_suffix",
        "pattern": [
            {"POS": {"IN": ["ADJ", "NOUN", "PROPN"]}, "OP": "?", "IS_UPPER": False},
            suffix_regex_rule,
            {"LOWER": {"IN": ["and", "&"]}},
            suffix_regex_rule
        ]
    },
    {
        "label": "POLICY",
        "id": "8_policy_with_for_phrase",
        "pattern": [
            suffix_regex_rule,  # Head-Noun
            {"LOWER": {"IN": ["for", "of"]}},  # Optional Präposition (kann erweitert werden)
            {"POS": {"IN": ["NOUN", "PROPN"]}, "OP": "+"},  # Mindestens ein Nomen
            {"LOWER": "of", "OP": "?"},  # Optionales 'of'
            {"POS": {"IN": ["NOUN", "PROPN"]}, "OP": "*"}  # Weitere Nomen
        ]
    }

]

org_patterns = [
    {
        "label": "ORG",
        "id": "org_with_suffix",
        "pattern": [
            up_to_three_nouns_not_suffix,
            {"LOWER": {"IN": ORG_SUFFIXES}}
        ]
    },
    {
        "label": "ORG",
        "id": "org_head_of_name",
        "pattern": [
            {"LOWER": {"IN": ORG_SUFFIXES}},
            {"LOWER": "of"},
            up_to_three_nouns_not_suffix
        ]
    }
]