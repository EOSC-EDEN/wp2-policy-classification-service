import re

import requests
from bs4 import BeautifulSoup
from readability import Document
import spacy
import json
import os

import policy_classifier.data.rules as rules
from spacy.util import compile_infix_regex

from readability import Document


class PolicyDetector:
    def __init__(self):
        def term_to_pattern(law_name):
            return [{"LOWER": token} for token in law_name.lower().split()]

        self.nlp = spacy.load("en_core_web_sm")

        infixes = list(self.nlp.Defaults.infixes)

        # Remove hyphen splitting between letters/numbers
        infixes = [
            x for x in infixes
            if not any(h in x for h in ["-", "–", "—", "--", "---", "——"])
        ]

        # Compile new regex
        infix_re = compile_infix_regex(tuple(infixes))

        # Apply tokenizer change
        self.nlp.tokenizer.infix_finditer = infix_re.finditer

        org_ruler = self.nlp.add_pipe("entity_ruler", before='ner', config={"overwrite_ents": True, "validate": True},
                                      name="org_ruler")
        org_acronym_ruler = self.nlp.add_pipe("entity_ruler", before='ner',
                                              config={"overwrite_ents": False, "validate": True},
                                              name="org_acronym_ruler")
        policy_ruler = self.nlp.add_pipe("entity_ruler", before='ner',
                                         config={"overwrite_ents": False, "validate": True},
                                         name="policy_ruler")
        org_list = self._load_org_names()
        org_patterns = [{"label": "ORG", "pattern": term_to_pattern(org)} for org in org_list]
        rules.org_patterns.extend(org_patterns)

        policy_ruler.add_patterns(rules.policy_patterns)
        org_ruler.add_patterns(rules.org_patterns)
        org_acronym_ruler.add_patterns([rules.uppercase_org_acronym])

    # load a list of org names found at re3data
    def _load_org_names(self):
        org_list = []
        par_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        org_path = os.path.join(par_path, "data", "re3data_names.json")
        with open(org_path, encoding="utf-8") as f:
            org_list = json.load(f)
        return org_list

    #classify
    def classify(self, text, in_link_url = None, in_link_text = None):
        doc_headings = []
        doc_text = str(text)
        #check if is html:
        if re.search(r"</?[a-z][^>]*>", text, re.I):
            web_doc = Document(text)
            cleaned_html = web_doc.summary().replace('\n', ' ')
            cleaned_html = re.sub(r"\s+", " ", cleaned_html)
            soup = BeautifulSoup(cleaned_html, 'html.parser')
            doc_headings = [h.get_text(strip=True) for h in soup.find_all(["h1", "h2", "h3", "h4"])]
            doc_text = soup.get_text()
            nlp_doc = self.nlp(doc_text)
            policy_ents = {}
            for ent in nlp_doc.ents:
                if ent.label_=='POLICY':
                    if ent.text.lower() not in policy_ents:
                        policy_ents[ent.text.lower()] = 1
                    else:
                        policy_ents[ent.text.lower()] += 1
            print(policy_ents)
        #print(doc_text)

res = requests.get("https://pangaea.de/about/privacypolicy.php")
p = PolicyDetector()

p.classify(res.text)
