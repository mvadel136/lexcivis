# Self-assessment against the ITU AI Readiness Framework 2.0

Dimensions and metric names come from ITU's AI Readiness toolkit (`dimensions.json`, Readiness 2.0, January 2026).
**Status:** *evidence* means LexCivis measures or implements it, *partial* means some of it, and *gap* means it is
missing and has an entry in the gap register (`gaps.yaml`).

| # | Dimension | Metrics addressed | Evidence in LexCivis | Status |
|---|---|---|---|---|
| 1 | Data/Model Marketplace | Dataset Properties, Diligence Metrics, Open Datasets, Privacy and Security, Personal Data Standards, Data Governance, Standards-Compliant Formats, Open-Source Models | Data card and profile of 836 records (`data/DATA_CARD.md`); 94 French/Arabic flags with verdicts; normalized JSONL; library of the 98 attached legal texts and forms with SHA-256 manifest, page text and OCR of 200 scanned pages (`data/documents/`); masking of ID, phone, e-mail, date and name; open models (BGE-M3, BGE reranker) | evidence; G2, G4, G5, G11 open |
| 2 | Generated Content Marketplace | Guardrails, Fake Detection, Regional Customization | Generated text is optional and rejected if it adds or drops a number or falls under 75% grounding; claimed amounts are checked against the record; fake-fee events trigger incident and takedown proposals | evidence |
| 3 | Cross-Domain Correlation Analysis | Integrated Workflow, Domain KPIs, Coverage and Scale | One pipeline across 31 administrations; completeness per administration (47% to 100%); conflicts per administration | partial |
| 4 | Contextualization and Regional Impact | Local Datasets, Indigenous Service Users, Regional Customizations, Cultural Diversity | Local official data; Hassaniya in Arabic and Latin script (seed lexicon); citizen-wording map; French and Arabic interface | partial; G6 open (no native-reviewed test set) |
| 5 | Level of Integration of AI in Workflows | Automation Level, Integration Level, Model Suitability, Quality Improvement | Retrieval and classification are automated, answers are deterministic, and institutional decisions stay human. Measured in `reports/evaluation.json` and `benchmark_v2.json` | evidence |
| 6 | Human Interface | Local Language Models, Interaction Channels, Usability Level, Cultural Sensitivity, Safety Integration | Bilingual right-to-left chat interface; each value carries a numbered source that opens the exact file entry and field, or the page of the attached legal text; held and refused states; keyboard and contrast checks | evidence; G9 (AI disclosure rule) open |
| 7 | Strategy Alignment | Intent Representations, Interoperability Standards, Service Provider Mapping, International Cooperation | Y.3172 ML intent (`ml_intent.yaml`) drives the thresholds and targets; Y.3172 node map; links to Mauritania's National AI Strategy 2025-2029 (objectives 4.4.1, 4.6.1, 4.6.2, 4.8.4) | evidence |
| 8 | Collaboration with AI | Baseline Comparison, Prompting Efficiency | SANAD v1 baseline vs LexCivis on the same staged questions (`examples/baseline_sanad_v1/`); LLM agents vs rule playbook on the same stages | evidence |
| 9 | Impacts of Humans in AI Integration | Expert Intersection, Action Latency | Named human decisions recorded in the ledger (`lexcivis approve`); actions waiting for a human are listed per stage | partial |
| 10 | AI & Policies | Policy Sandbox, Policy Evaluation, Safety Policies, Explainability Metrics, Policy Case Briefs, Audit Metrics, Data Sovereignty | Staged exercise with a simulated timeline and live injection; mandate guard; legal-order rules; human gate; case brief; SHA-256 ledger sealed with Ed25519; transfer rule (law 2017-020 arts. 20–22) | evidence; G7, G8 open |
| 11 | AI for Inclusion | Language Repository, Regional Language Support, Beneficiaries | Hassaniya lexicon and test questions published; Arabic answers from Arabic records | partial; G6 open |
| 12 | Granular Priorities | Regional Priorities, Priority Organization | Least complete administrations ranked; conflicts listed for the owners | partial |
| 13 | Digital Infrastructure | Digital Services, Energy Consumption, Uptime | Runs on one laptop CPU with no GPU (median ~5 s per question); single container (`Dockerfile`) | partial; G10 (verified SMS sender) open |

Factors (Readiness 2.0): **Data** (dims 1, 3, 4) evidence · **Research** (4) partial · **Deployment Support** (4, 6, 10, 12, 13)
evidence/partial · **Standards** (3, 5, 6, 7, 8) evidence · **Open Source and Code** (1, 2, 8) evidence · **Sandbox
Environments** (9, 10, 11) evidence.
