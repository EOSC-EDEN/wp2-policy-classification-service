POLICY_SUFFIXES = [
    'act',
    'addendum',
    'agreement',
    'amendment',
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

policy_suffix_regex = r'(?i)\b(' + r'|'.join([p  for p in POLICY_SUFFIXES if not p.endswith('y')]) + r')s?\b|' +\
r'\b(' + r'|'.join([p[:-1]  for p in POLICY_SUFFIXES if p.endswith('y')]) + r')(y|ies)\b'

suffix_regex_rule = {
    "TEXT": {"REGEX": policy_suffix_regex}
}

uppercase_org_acronym = {
    "label": "ACR",
    "pattern": [{"TEXT": {"REGEX": r"^[A-Z\-\\]{2,8}$"}}]
}

up_to_three_nouns_not_suffix = {
    "POS": {"IN": ["ADJ", "NOUN", "PROPN","CCONJ"]},
    "LOWER": {"NOT_IN": POLICY_SUFFIXES},
    "OP": "{1,5}", # apple and banana and carot
    "IS_UPPER": False
}

up_to_three_nouns_not_suffix_optional = {
    "POS": {"IN": ["ADJ", "NOUN", "PROPN","CCONJ"]},
    "LOWER": {"NOT_IN": POLICY_SUFFIXES},
    "OP": "{0,5}", # apple and banana and carot
    "IS_UPPER": False
}

end_with_noun_not_suffix = {
        "POS": {"IN": ["NOUN", "PROPN"]},  # CCONJ bewusst ausgeschlossen
        "LOWER": {"NOT_IN": POLICY_SUFFIXES},
        "IS_UPPER": False
    }


policy_patterns = [
    {
      "label": "POLICY",
     "id": "1_suffix_and_suffix_for_some_adj_nouns",
      "pattern":
          # e.g. guidelines and policy for data reuse
          [
              suffix_regex_rule,
                {"LOWER": {"IN": ["and", "&"]}},
              suffix_regex_rule,
              {"LOWER": {"IN":["of","for","on","to","in"]}},
               {"LOWER": {"IN":["the"]},"OP": "?"},
            # Optional descriptive noun(s) or proper noun(s),
            up_to_three_nouns_not_suffix_optional,
            end_with_noun_not_suffix
          ]
    },
    {
      "label": "POLICY",
      "id": "2_suffix_and_suffix",
      "pattern":
        # terms and conditions
          [
              suffix_regex_rule,
                {"LOWER": {"IN": ["and", "&"]}},
              suffix_regex_rule
          ]
    },
    {
        "label": "POLICY",
        "id": "3_noun_adj_suffix_and_suffix",
        "pattern": [
            # data policy and rules
            {"POS": {"IN": ["ADJ", "NOUN", "PROPN"]}, "OP": "?","IS_UPPER": False},
            suffix_regex_rule,
            {"LOWER": {"IN": ["and", "&"]}},
            suffix_regex_rule
        ]
    },
    {
        "label": "POLICY",
        "id": "4_some_noun_adj_suffix",
        "pattern": [
            up_to_three_nouns_not_suffix_optional,
            end_with_noun_not_suffix,
            suffix_regex_rule
        ]
    },
    {
        "label": "POLICY",
        "id": "5_adj_suffix_some_noun_or_adj",
        "pattern": [
            # e.g. general
            {"POS": "ADJ", "OP": "?"},
            suffix_regex_rule,
            # Optional 'of'
            {"LOWER": {"IN":["of","for","on","to","in"]}},
            # Optional descriptive noun(s) or proper noun(s)
            up_to_three_nouns_not_suffix_optional,
            end_with_noun_not_suffix
        ]
    },
    {
        "label": "POLICY",
        "id": "6_suffix_for_some_noun_adj",
        "pattern": [
            suffix_regex_rule,   # Head-Noun
            {"LOWER": {"IN":["of","for","on","to","in"]}},
            {"LOWER": {"IN":["the"]},"OP": "?"},      # Optional Präposition (kann erweitert werden)
            up_to_three_nouns_not_suffix_optional,
            end_with_noun_not_suffix
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