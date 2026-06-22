## Policy Classification Service

The Policy Classification Service is designed as a REST service that identifies, parses, and classifies policy documents based on their textual content.
In this context, a *policy* is any document that defines rules, terms, conditions, rights, or obligations governing the use of a resource.
The service uses Named Entity Recognition (NER) combined with domain-specific rules to detect and classify policy-related concepts and terms, such as:

* Terms of Use
* Licensing Conditions
* Access Restrictions
* Usage Rights
* Preservation Policies
* Other policy-relevant statements

By automatically extracting and categorizing policy information from heterogeneous document sources (initially restricted to HTML documents), the service supports the discovery, analysis, and comparison of policies across repositories and services.
The REST API enables automated integration into external systems and workflows, allowing policy documents to be submitted, analyzed, and classified programmatically.
