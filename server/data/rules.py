STOP_WORDS = {
                'the', 'a', 'an', 'and', 'or', 'of', 'for', 'to',
                'in', 'on', 'with', 'by', 'from'
            }

POLICY_SUFFIXES = [
    'act', 'acts',
    'addendum', 'addenda',
    'agreement', 'agreements',
    'amendment', 'amendments',
    'charter', 'charters',
    'code','codes',
    'condition', 'conditions',
    'constitution', 'constitutions',
    'contract', 'contracts',
    'declaration', 'declarations',
    'directive', 'directives',
    'guide', 'guides',
    'guideline', 'guidelines',
    'licence', 'licences',
    'license','licenses',
    'manual', 'manuals',
    'note', 'notes',
    'notice', 'notices',
    'plan', 'plans',
    'policy', 'policies',
    'principle', 'principles',
    'regulation', 'regulations',
    'rule', 'rules',
    'statement', 'statements',
    'statute', 'statutes',
    'strategy', 'strategies',
    'term','terms'
]

POLICY_TARGETS = [
    # Information / Knowledge
    "data",
    "information",
    "knowledge",
    "content",
    "document",
    "documents",
    "record",
    "records",
    "metadata",
    "dataset",
    "datasets",
    "research",
    "science",
    "evidence",

    # Digital / Technical
    "software",
    "hardware",
    "system",
    "systems",
    "technology",
    "technologies",
    "platform",
    "application",
    "applications",
    "database",
    "databases",
    "network",
    "networks",
    "service",
    "services",
    "infrastructure",

    # Rights / Legal / Governance
    "rights",
    "right",
    "license",
    "licence",
    "copyright",
    "intellectual property",
    "property",
    "ownership",
    "privacy",
    "confidentiality",
    "consent",
    "permission",
    "permissions",
    "access",
    "authorization",
    "authority",
    "compliance",
    "governance",
    "regulation",
    "law",
    "legal",

    # Ethics / Responsible Research
    "ethics",
    "ethical",
    "research ethics",
    "integrity",
    "responsibility",
    "responsible research",
    "risk",
    "risks",
    "harm",
    "safety",
    "security",

    # People / Organisations
    "person",
    "people",
    "individual",
    "individuals",
    "user",
    "users",
    "researcher",
    "researchers",
    "author",
    "authors",
    "participant",
    "participants",
    "subject",
    "subjects",
    "community",
    "communities",
    "organization",
    "organisation",
    "institution",
    "institutions",

    # Research / Scholarly
    "publication",
    "publications",
    "article",
    "articles",
    "paper",
    "papers",
    "journal",
    "journals",
    "citation",
    "citations",
    "source",
    "sources",
    "repository",
    "repositories",
    "archive",
    "archives"
]

NOT_A_POLICY =[
    'computer code']

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

suffix_lower_rule =  {
    "LOWER": {"IN": POLICY_SUFFIXES},
    "POS": {"IN": ["NOUN", "PROPN"]}
}


uppercase_org_acronym = {
    "label": "ACR",
    "pattern": [{"TEXT": {"REGEX": r"^[A-Z\-\\]{2,8}$"}}]
}

up_to_three_nouns_not_suffix = {
    "POS": {"IN": ["ADJ", "NOUN", "PROPN","CCONJ"]},
    "LOWER": {"NOT_IN": POLICY_SUFFIXES},
    "OP": "{1,5}" # apple and banana and carot
}

up_to_three_nouns_not_suffix_optional = {
    "POS": {"IN": ["ADJ", "NOUN", "PROPN","CCONJ"]},
    "LOWER": {"NOT_IN": POLICY_SUFFIXES},
    "OP": "{0,5}" # apple and banana and carot
}

end_with_noun_not_suffix = {
        "POS": {"IN": ["NOUN", "PROPN"]},  # CCONJ bewusst ausgeschlossen
        "LOWER": {"NOT_IN": POLICY_SUFFIXES}
    }


policy_patterns = [
    {
      "label": "POLICY",
     "id": "1_suffix_and_suffix_for_some_adj_nouns",
      "pattern":
          # e.g. guidelines and policy for data reuse
          [
                suffix_lower_rule,
                {"LOWER": {"IN": ["and", "&"]}},
                suffix_lower_rule,
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
                suffix_lower_rule,
                {"LOWER": {"IN": ["and", "&"]}},
                suffix_lower_rule,
          ]
    },
    {
        "label": "POLICY",
        "id": "3_noun_adj_suffix_and_suffix",
        "pattern": [
            # data policy and rules
            {"POS": {"IN": ["ADJ", "NOUN", "PROPN"]}, "OP": "?","IS_UPPER": False},
            suffix_lower_rule,
            {"LOWER": {"IN": ["and", "&"]}},
            suffix_lower_rule,
        ]
    },
    {
        "label": "POLICY",
        "id": "4_some_noun_adj_suffix",
        "pattern": [
            up_to_three_nouns_not_suffix_optional,
            suffix_lower_rule
        ]
    },
    {
        "label": "POLICY",
        "id": "5_adj_suffix_some_noun_or_adj",
        "pattern": [
            # e.g. general
            {"POS": "ADJ", "OP": "?"},
            suffix_lower_rule,
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
            suffix_lower_rule,
            {"LOWER": {"IN":["of","for","on","to","in"]}},
            {"LOWER": {"IN":["the"]},"OP": "?"},      # Optional
            up_to_three_nouns_not_suffix_optional,
            end_with_noun_not_suffix
        ]
    },
    {
        "label": "POLICY",
        "id": "7_adj_suffix",
        "pattern": [
            {"POS": "ADJ"},
            suffix_lower_rule,
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