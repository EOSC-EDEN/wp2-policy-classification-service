# Policy Extraction and Classification Service Specification

# **Abstract**

The Policy Extraction and Classification Service automatically discovers, extracts, and classifies policy-related information from repository or service websites. It identifies policy statements, policy documents, and policy-related metadata embedded in webpages or linked resources.   
Extracted policies are normalized and mapped to a predefined policy ontology in order to enable structured representation, comparison, and automated analysis of repository policies. The service exposes both detected policies and classification results for further processing and integration into metadata registries and monitoring systems.

# **Status of this Document**

This is a working draft

**Rationale**

The described service turns repository policies from heterogeneous human-facing documents into machine-actionable, structured and comparable information that can be consumed by repository registries and discovery services. Ultimately this enables  researchers to discover and reliably compare repositories based not only on their data, metadata or community recommendation, but also on the conditions under which that data can be accessed or re-used, and how it is being preserved.

# **Introduction**

Repositories and research infrastructures publish important operational and governance policies such as data access policies, preservation policies, or licensing policies. These policies are typically described in natural language on repository websites or in linked documentation.  
However, policy descriptions are often heterogeneous, unstructured, and inconsistently labeled, making automated discovery and comparisons difficult.  
This specification defines the requirements for a service implemented as Web API that automatically discovers policy-related content on repository websites, extracts policy statements from webpage text, maps extracted policies to a structured policy ontology and provides structured outputs suitable for registry integration and analysis.  
The specification aims to enable reproducible policy discovery and standardized representation of repository policy information.

# **Scope**

This specification covers:

* Discovery of policy-related pages on repository websites  
* Extraction of policy statements and terms from webpage text  
* Identification and tagging of policy entities and phrases  
* Mapping of extracted policies to a predefined policy ontology  
* Presentation and export of detected policies  
* Overall classification of policy coverage using the hierarchical classification of the policy ontology

This specification does not define:

* the internal NLP or machine learning algorithms used for policy detection  
* a specific ontology implementation which is subject of another specification

# **Conformance**

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 of  [RFC2119](https://www.rfc-editor.org/info/rfc2119/) ([RFC8174](https://www.rfc-editor.org/info/rfc8174/)) when, and only when, they appear in all capitals, as shown here.

# **Core-Preservation Processes**

The Policy Extraction and Classification Service operates on the public web presence of repositories and archives, i.e outside the TDA boundary, and turns published policy prose into structured records. It does not itself perform any preservation process. Its relevance to the CPP framework is indirect, but practical. Several CPPs can only be carried-out, if a written policy exists and is known. This service makes it possible to automatically establish which policies a repository publishes, what kind of policy each one is, and what it covers.

* **CPP-020 Rights Management**: An archive has to establish what it and its users are allowed to do with the available data. This information is held in an institution's own published policies. This service produces a machine-actionable record of the policies content, just as CPP-020 asks for. 

* **CPP-017 Disposal**: Supports disposal and retention scheduling. CPP-017 requires the TDA to have a disposal policy covering Objects, derivative Files and related metadata. The service can be used to find and label retention and disposal policies, governing aspects related to CPP-017

* **CPP-029 Ingest**: Supports pre-deposit conformance checking. Ingest procedures/requirements are (ideally) formalised in a repositories’ policies. This service translates the policies and hence the procedures/requirements into a machine-actionable, structured and standardised form.

* **CPP-025 Enabling Access**: CPP-025 notes that access can be enforced by policy. This service detects access, open access and embargo policies. Embargo policies ensure (amongst other) proper rights management as described in CPP-020.

* **CPP-024 Enabling Discovery** produces input for catalogue discovery services. CPP-024 requires discovery to handle varied access policies as defined by the data owner, including those, where different datasets carry different access conditions. Structured policy records let a catalogue carry that information directly, instead of having to link to a page the user has to read.

#   **Normative Requirements**

## **Requirement Group 1 \- Policy Page Discovery**

**1.1 Policy Page Identification**  
{{ PCS-REQ-1-1-001 }} The service SHALL identify candidate policy pages based on link titles, URLs, or headings.  
{{ PCS-REQ-1-1-002 }} The service SHOULD detect pages containing policy-related keywords such as “policy”, “guidelines”, “rules”, or “terms”.

**A.2 Linked Policy Documents**  
{{ PCS-REQ-1-2-001 }} The service SHALL detect links to external policy documents such as (PDFs) or separate webpages (see B.2).  
{{ PCS-REQ-1-2-002 }} The service SHOULD extract text from linked documents when feasible (see B.2).

## **Requirement Group 2 \- Policy Webpage Acquisition**

**2.1 Webpage Retrieval**  
{{ PCS-REQ-2-1-001 }} The service SHALL retrieve webpage content from a given repository URL.  
{{ PCS-REQ-2-1-002 }} The service SHALL support retrieval of HTML content via HTTP or HTTPS.  
{{ PCS-REQ-2-1-003 }} The service SHALL follow redirects when retrieving webpages.

**2.2 Content Extraction**  
{{ PCS-REQ-2-2-001 }} The service SHALL remove boilerplate elements such as navigation menus, headers, and footers.  
{{ PCS-REQ-2-2-002 }} The service SHALL extract the main textual content of webpages.  
{{ PCS-REQ-2-2-003 }} The service SHOULD preserve document structure including headings and paragraphs.

## **Requirement Group 3 \- Policy Entity Extraction**

**3.1 Policy Entity Recognition**  
{{ PCS-REQ-3-1-001 }} The service SHALL detect policy-related terms using linguistic patterns (NLP), rule-based extraction, or machine learning approaches.  
{{ PCS-REQ-3-1-002 }} The service SHALL identify policy entities such as policy names, policy categories, and related organizational entities.  
{{ PCS-REQ-3-1-003 }} The service SHALL identify activity or event types covered by these policy terms such as ‘access’, ’modify’, ideally based on PREMIS or ODRL terms.  
{{ PCS-REQ-3-1-004 }} The service SHOULD detect compound policy expressions (e.g., “data access policy”, “preservation policy”).

## **Requirement Group 4 \- Ontology Mapping**

**4.1 Ontology Integration**  
{{ PCS-REQ-4-1-001 }} The service SHALL map detected policy entities to a predefined Policy Ontology or to existing preservation activity or event vocabularies such as PREMIS or ODRL.  
{{ PCS-REQ-4-1-002 }} The service SHALL classify extracted policy mentions according to these ontology concepts.  
{{ PCS-REQ-4-1-003 }} The service SHALL identify an appropriate, higher-level main category that characterizes the type of policy based on the  e.g. using hierarchies (if present) stored in the ontology or appropriate selected terms.

## **Requirement Group 5 \- Result Presentation and Export**

**5.1 Result Representation**  
{{ PCS-REQ-5-1-001 }} The service SHALL represent extracted policies in a machine-readable format.  
{{ PCS-REQ-5-1-002 }} The service SHOULD support export formats such as JSON or JSON-LD.

# **Non-normative Guidance**

Policy descriptions are often expressed in natural language and may not explicitly use the term “policy”. Implementations therefore need to be flexible and use extraction approaches combining linguistic patterns, dictionaries and machine learning methods.

# **References**

* spaCy Natural Language Processing Library ([https://spacy.io/](https://spacy.io/))  
* JSON-LD 1.1 \- W3C

