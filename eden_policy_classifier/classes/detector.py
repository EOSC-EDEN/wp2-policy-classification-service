import re

import requests
from bs4 import BeautifulSoup
import spacy
import json
import os

import eden_policy_classifier.data.rules as rules
from spacy.util import compile_infix_regex
from spacy.language import Language

from readability import Document

from rdflib import Graph, Namespace, SKOS, RDFS

import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)

class PolicyDetector:
    logger = logging.getLogger('PolicyDetector')

    def __init__(self):
        self.logger.info(' ---- Initializing PolicyDetector ---- ')
        #self.nlp = spacy.load("en_core_web_md")
        self.nlp = spacy.load("en_core_web_lg")
        self.policy_vocab_dict = {}
        self.policy_actions = {}
        self._set_actions()
        self._set_policy_vocab()

        def term_to_pattern(law_name):
            return [{"LOWER": token} for token in law_name.lower().split()]

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

        BLACKLIST = ["computer code", "source code"]

        @Language.component("remove_bad_policy_matches")
        def remove_bad_policy_matches(doc):
            doc.ents = [
                ent for ent in doc.ents
                if not (
                        ent.label_ == "POLICY"
                        and any(bad in ent.text.lower() for bad in BLACKLIST)
                )
            ]

            return doc

        org_ruler = self.nlp.add_pipe("entity_ruler", before='ner', config={"overwrite_ents": True, "validate": True},
                                      name="org_ruler")
        org_acronym_ruler = self.nlp.add_pipe("entity_ruler", before='ner',
                                              config={"overwrite_ents": False, "validate": True},
                                              name="org_acronym_ruler")
        policy_ruler = self.nlp.add_pipe("entity_ruler", before='ner',
                                         config={"overwrite_ents": False, "validate": True},
                                         name="policy_ruler")
        self.nlp.add_pipe("remove_bad_policy_matches", after="policy_ruler")

        org_list = self._load_org_names()
        org_patterns = [{"label": "ORG", "pattern": term_to_pattern(org)} for org in org_list]
        rules.org_patterns.extend(org_patterns)

        policy_ruler.add_patterns(rules.policy_patterns)
        org_ruler.add_patterns(rules.org_patterns)
        org_acronym_ruler.add_patterns([rules.uppercase_org_acronym])

    def _set_policy_vocab(self):
        #loads policy terms from the PTV vocab
        policy_vocab_ns = "https://w3id.org/ptv/"
        policy_vocab_uri = 'https://raw.githubusercontent.com/EOSC-EDEN/wp2-policy-type-vocabulary/refs/heads/main/code/ptv.ttl'
        policy_dict = {}
        r = requests.get(policy_vocab_uri)
        g = Graph()
        g.parse(data=r.text, format="turtle")
        PTV = Namespace("https://w3id.org/ptv/")
        target_class = PTV.Policy
        subclasses = set(g.transitive_subjects(RDFS.subClassOf, target_class))
        for sc in subclasses:
            label = g.value(subject=sc, predicate=SKOS.prefLabel)
            label = str(label)
            id = str(sc)

            altlabels = list(
                g.objects(subject=sc, predicate=SKOS.altLabel)
            )
            if altlabels:
                for altl in altlabels:
                    suf, act, tar = self._get_policy_components(altl)
                    policy_doc = self.nlp(str(altl))
                    policy_dict[altl.lower()] = {'id':id , 'label': altl, 'suffix':suf, 'actions': act, 'targets':tar, 'doc':policy_doc}
            suf, act, tar = self._get_policy_components(label)
            policy_doc = self.nlp(str(label))
            policy_dict[label.lower()] =  {'id':id , 'label':label,'suffix':suf, 'actions': act, 'targets':tar, 'doc':policy_doc}
        self.policy_vocab_dict = policy_dict
        return policy_dict

    def _load_org_names(self):
        # load a list of org names found at re3data
        org_list = []
        par_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        org_path = os.path.join(par_path, "data", "re3data_names.json")
        with open(org_path, encoding="utf-8") as f:
            org_list = json.load(f)
        return org_list

    def _set_actions(self):
        par_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        act_path = os.path.join(par_path, "data", "activities.json")
        with open(act_path, encoding="utf-8") as f:
            self.policy_actions = json.load(f)

    def _get_policy_components(self, term):
        # returns (suffix, action, target)
        # e.g. data management policy => (policy, manage, data)
        actions = []
        suffix = None
        targets = []
        for t in term.lower().split():
            if t not in rules.STOP_WORDS:
                if t in self.policy_actions or t.strip('s') in self.policy_actions:
                    action_rec = self.policy_actions.get(t) or self.policy_actions.get(t.strip('s'))
                    action = action_rec.get("action")
                    actions.append(action)
                if t in rules.POLICY_SUFFIXES:
                    suffix = t
                if t in rules.POLICY_TARGETS:
                    targets.append(t)

        return suffix, actions, targets

    def _get_best_policy_term(self, term, treshold = 80):
        #print(term)

        candidates = []

        term_doc = self.nlp(term)
        t_suff, t_action, t_target = self._get_policy_components(term)
        #term, t_suff, t_action, t_target)

        for policy, policy_record in self.policy_vocab_dict.items():
            semantic_score = 0
            if term.lower() == policy or (len(term_doc) > 1 and (t_action or t_target) and t_suff):
                semantic_score = (
                        term_doc.similarity(policy_record.get('doc')) * 100
                )
            term_id = policy_record.get('id')

            if semantic_score > treshold:
                candidates.append(
                    {'id': term_id ,'term':policy, 'score': semantic_score, 'activity': t_action}
                )

        if candidates:
            candidates = [c for c in candidates if c.get('score') >= treshold]
            candidates.sort(
                key=lambda x: x.get('score'),
                reverse=True
            )
        else:
            candidates = [{'id': 'owl:Nothing', 'term': 'unknown', 'score': 0, 'activity':t_action}]

        return candidates[0]

    #classify
    def classify(self, text, include_nothing = True):
        #include_nothing : if set to True => would also include results which cannot be mapped to the policy vocabulary
        doc_headings = []
        doc_text = str(text)
        #check if is html:
        if re.search(r"</?[a-z][^>]*>", doc_text, re.I):
            web_doc = Document(doc_text) # boiler plate detection
            boiler_html = web_doc.summary(html_partial=True).replace('\n', ', ')
            raw_html = doc_text.replace('\n', ', ')
            raw_soup = BeautifulSoup(raw_html, 'html.parser')
            boiler_html = re.sub(r"\s+", " ", boiler_html)
            boiler_soup = BeautifulSoup(boiler_html, 'html.parser')
            raw_headings = [h.get_text(strip=True) for h in raw_soup.find_all(["h1", "h2", "h3", "h4"])]
            raw_title = raw_soup.find('title').get_text(strip=True)

            boiler_text = boiler_soup.get_text('; ')
            if raw_headings:# a little boost for headings
                doc_text = raw_title+'. '+', '.join(raw_headings)+'. '+boiler_text
            #print(doc_text)
        nlp_doc = self.nlp(doc_text)

        policy_ents = {}
        for ent in nlp_doc.ents:
            if ent.label_=='POLICY':
                if ent.text.lower() not in policy_ents:
                    policy_ents[ent.text.lower()] = 1
                else:
                    policy_ents[ent.text.lower()] += 1

        #count detected policy entities
        policy_ents = {k: v for k, v in sorted(policy_ents.items(), key=lambda item: item[1],reverse=True)}

        detected_policies = {}

        #classify
        for policy_name, policy_count in policy_ents.items():
            policy_rec = self._get_best_policy_term(policy_name)
            policy_id = policy_rec.get('id')
            policy_score = policy_rec.get('score')
            policy_act = policy_rec.get('activity')
            classified_policy = {
                'term': policy_name,
                #'id': policy_id,
                'score': policy_score,
                'count': policy_count,
                'activity': policy_act
            }
            if policy_id not in detected_policies:
                #suffix, actions, targets = self._get_policy_components(policy_name)
                detected_policies[policy_id] = {
                    'count': policy_count,
                    'entities': [classified_policy]
                }
            else:
                detected_policies[policy_id]['count'] += policy_count
                detected_policies[policy_id]['entities'].append(classified_policy)
        #sort for final output
        #print(json.dumps(detected_policies, indent=4))

        '''detected_policies = dict(
            sorted(detected_policies.items(), key=lambda item: item[1]['count'], reverse=True)
        )'''

        # we don't need this in the output
        detected_policies = dict(
            sorted(
                (
                    (key, value)
                    for key, value in detected_policies.items()
                    if include_nothing or key != "owl:Nothing"
                ),
                key=lambda item: item[1]["count"],
                reverse=True
            )
        )

        return detected_policies