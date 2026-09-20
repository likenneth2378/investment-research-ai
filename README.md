# Investment Research AI

**Evidence-first research workspace for investment materials.**

Investment Research AI is a working prototype for turning long investment materials into a smaller, source-linked research surface. It is designed to reduce how much an analyst has to read while preserving a path back to the original evidence.

It does **not** try to make an investment decision automatically.

## Why this project exists

A recurring failure in LLM-assisted research is that compression can silently strengthen the evidence.

Example:

> Source: 公司称目前涉及 11 项核心专利。  
> Bad compression: 公司拥有 11 项核心专利。

The second sentence sounds only slightly different, but it removes the attribution layer and makes a company-reported statement look like an independently verified fact.

This project treats that kind of failure as a product-design problem rather than just a prompt problem.

## Development timeline

- **June 2026 — project start.** The project began as an attempt to turn recurring problems from real investment-research work into a more reliable AI-assisted workflow, especially around attribution, evidence preservation and human review.
- **June–August 2026 — prototype and problem discovery.** Early work focused on claim extraction, source linking, failure cases and the boundary between AI assistance and analyst judgment.
- **Early September 2026 — repository consolidation.** The local prototype was organized into a runnable GitHub project with BYOK, structured extraction, synthetic demo materials and a review interface.
- **September 2026 — full-workflow iteration and public release preparation.** Long-document testing led to the current Snapshot / Research Matrix / Flags workflow, deterministic evidence checks, bounded Vision, actionable diligence Flags and a print-oriented follow-up checklist.

The GitHub repository reflects the point at which the local work was consolidated for versioned development; it is not the start date of the project itself.

## Current product

The current Web UI is built around three primary views:

- **Snapshot** — a short, investor-prioritized summary and core numbers
- **Research Matrix** — a top-down Domain → Topic research hierarchy with analyst review state and source pointers
- **Flags** — material, unresolved and actionable research questions that can be cleared or marked for follow-up by the analyst
- **Evidence on demand** — raw source text and provenance expand directly inside Matrix / Flags instead of occupying a separate top-level view

The current workflow is:

```text
Raw materials
    ↓
Local parsing
    ↓
Page / section triage
    ↓
Relevant content only
    ↓
High-value fact extraction
    ↓
Deterministic evidence checks
    ↓
Topic aggregation
    ↓
Snapshot + Research Matrix
    ↓
Issue-only semantic verification
    ↓
Analyst review state
    ↓
Research Flags + evidence on demand
```

## What is implemented

- TXT / PDF / DOCX / PPTX ingestion
- model page / section triage for long materials; shorter decks go directly to text-first extraction
- structured fact extraction with source text and attribution
- provenance by page, slide, paragraph or line range
- deterministic checks for source location and unsupported numbers, with punctuation/line-break tolerance and date canonicalization (e.g. 2021年5月 = 2021.05)
- topic aggregation instead of one-card-per-claim output
- investor-priority ordering for Snapshot items, full-text Core Number cards, atomic metric prompts, company-first numbers and at most two technical metrics
- stable top-down Matrix hierarchy: company overview → commercialization & competition → financials → team & organization → product & technology → IP, with two default topics per domain and primary-home de-duplication
- canonical domain/topic organization so related commercial, market and competition facts stay together
- compact Matrix defaults that show a few core topics per domain while preserving the full underlying topic set for drill-down
- explicit team/organization coverage and more granular IP topics such as authorization status and co-development / ownership
- session-level analyst review state: unreviewed / cleared / follow-up, with optional notes
- separation between AI evidence status and human workflow status; clearing a topic never turns an unverified claim into a verified fact
- raw source text kept as a safety layer but surfaced only on demand inside Matrix / Flags
- deterministic consistency check so material caveats already exposed in Summary / Matrix cannot silently fail to become a Research Flag
- separate handling for projections, marketing claims, application scenarios and customer references
- bounded optional vision analysis for image-heavy pages
- risk-based issue-only semantic verification: Flags, multi-fact synthesis, projections/marketing and other high-risk outputs are checked; ordinary single-fact evidence-pass rows skip the extra model pass
- Research Flags governed by a Material + Unresolved + Actionable contract
- Flag coverage for unresolved customer/order status, concentration/dependencies, finance/forecast assumptions, production/delivery, IP/legal status, team/governance, regulatory/compliance and competition claims when the supplied facts make those questions material
- silence alone does not create a Flag; generic missing-information checklists are intentionally avoided
- resolved timeline changes and explicit forecast revisions stay in Matrix instead of creating false-positive Flags
- explicit protection against residual arithmetic across overlapping / undefined categories
- session-level result caching
- representative five-unit smoke testing with partial-scope Flag guards, so sample absence is not treated as document-wide non-disclosure
- model triage only for 41+ material units; ordinary decks go directly to text-first extraction
- Vision capped at two high-value pages and gated by text sufficiency / relationship-heavy layouts
- per-stage latency diagnostics
- JSON export plus a print-oriented due-diligence follow-up checklist PDF containing open Research Flags and Matrix topics manually marked for follow-up
- synthetic Demo mode with the same three-view workspace as Live
- Chinese / English workspace mode: UI labels and generated Snapshot / Matrix / Flags can switch to English while internal taxonomy and evidence enums remain stable; raw source evidence stays in its original language

## Design principles

**Reduce reading before adding features.**  
A traceable system can still fail if the analyst has to read the same amount of material again. Evidence is a safety layer, not the default reading interface.

**Faithfulness is different from truth.**  
The system can check whether a summary faithfully reflects the supplied material. It cannot prove that a company-provided statement is objectively true without external diligence evidence. Evidence-anchor warnings are kept separate from Research Flags: a parser/matcher warning is not automatically an investment diligence question.

**Matrix is knowledge; Flags are unanswered questions.**  
The Matrix stores material information the workflow currently knows. A Flag is created only when a material question remains unresolved and there is a concrete next diligence action. A resolved revision, an ordinary timeline update, or a merely unverified statement is not a Flag by itself. The printable diligence checklist then turns those open questions, plus analyst-marked Matrix follow-ups, into a field-ready review sheet rather than another narrative report.

**Human judgment stays with the analyst.**  
The system surfaces facts, provenance, projections, company-reported claims and review-worthy inconsistencies. Analysts can mark a topic or flag as reviewed / no current objection, or as requiring follow-up. This workflow state is separate from evidence status and does not convert an unverified company claim into an independently verified fact.

**Application scenario is not business traction.**  
A statement that a technology “can be used in finance” is not treated as evidence of financial-industry customers, deployment, contracts or revenue.

## Failure cases that shaped the design

A few examples are kept deliberately as regression targets:

1. **Attribution stripping**  
   “公司称拥有 11 项核心专利” must not become “公司拥有 11 项核心专利”.

2. **Historical fact vs. projection**  
   A completed-period revenue figure must not be classified as a forecast simply because it appears in a financial section.

3. **Timeline vs. conflict**  
   “27 projects in March” and “30 projects in June” may describe normal progress rather than contradictory claims.

4. **Application scenario vs. actual business**  
   “The technology can be used in financial risk control” must not become “the company has a financial-services business”.

5. **Material caveat loss during synthesis**  
   A short summary must not hide qualifiers that materially change the interpretation of a headline fact, such as cooperation status or patents that are not yet authorized.

6. **Superseded forecast shown as current**  
   When management explicitly revises a forecast or target, the current-state summary should reflect the updated value rather than keep the older version as the headline.

7. **Resolved revision promoted to a Flag**  
   A clear update such as 3.0 → 3.2 should update Matrix state, not create a research task merely because a revision occurred.

8. **Overlapping categories treated as arithmetic residual**  
   “11 total, 5 co-developed, 3 pending” must not become “3 independently owned and granted” unless the source establishes that the categories are mutually exclusive.

More cases and design responses are documented in [docs/failure-cases.md](docs/failure-cases.md).

## Demo

Demo mode uses only synthetic diligence materials and requires no API key.

```bash
py -m streamlit run app.py
```

Then choose **Demo** in the Web UI.

The Demo is intentionally synthetic so the repository can demonstrate provenance, projections, version changes and evidence review without publishing confidential investment materials.

## Live mode

The Web UI is the primary current interface.

```bash
pip install -r requirements.txt
py -m streamlit run app.py
```

Windows users can also run:

```text
run_app.bat
```

Live mode uses BYOK (Bring Your Own Key). The API key is entered at runtime and is not written into project files.

Supported providers in the current prototype:

- DeepSeek
- OpenAI
- OpenRouter

The older `main.py` path remains as a simple CLI/demo baseline; active product development is centered on `app.py`.

## Current benchmark direction

The project is no longer evaluated by “how many claims were extracted”.

The useful questions are:

- How much material does the analyst still need to read?
- Were important facts missed?
- Was attribution preserved?
- Were dates, numbers and projection status preserved?
- How many false-positive Flags were generated?
- How long did each pipeline stage take?
- How much did repeated analysis cost?

A recent internal smoke test showed that semantic verification was the slowest stage, so the verifier was redesigned to return only problematic items instead of regenerating the entire research output.

## Current limitations

This is still a working prototype.

Current priorities include:

- a larger human-labeled regression / golden set
- better entity and metric normalization across multiple documents
- stronger evaluation of missed high-value facts
- better handling of complex tables and visual-only evidence
- persistent caching beyond the current session
- further latency and cost reduction
- optional second-model review for a small set of high-risk final facts

The project intentionally does **not** claim to provide autonomous investment advice, valuation, or objective truth verification.

## Project structure

```text
investment-research-ai/
├── app.py                 # Current Streamlit product
├── main.py                # Earlier CLI/demo baseline
├── requirements.txt
├── run_app.bat
├── examples/              # Synthetic example materials
├── demo/                  # Synthetic demo fixtures
├── docs/
│   └── failure-cases.md
└── output/
```

## Privacy and repository policy

Real investment materials, client documents, uploaded research files and API keys should never be committed to this repository.

The public demo should use synthetic or explicitly publishable materials only.
