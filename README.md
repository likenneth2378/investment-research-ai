# Investment Research AI

Evidence-first investment research workflow for claim-level traceability and cross-document review.

## Current prototype

The current version reads multiple TXT files, turns non-empty lines into temporary ledger records, attaches deterministic source metadata, saves the ledger as JSON, and generates a simple HTML review page.

Current fields include:

- `claim_id`
- `document_id`
- `source_text`
- `source_line`
- `evidence_status` (currently a test placeholder)

## Why this project exists

The project started from a practical investment-research workflow problem: AI-generated summaries can strengthen or distort claims when source attribution is lost. A representative failure case is turning a statement such as "the company says it owns 11 patents" into "the company owns 11 patents".

The project therefore focuses on keeping claims traceable to source material before moving toward higher-level research output.

## Current status

This repository is an early prototype, not a finished product.

Implemented:

- Multi-file TXT ingestion
- Source document tracking
- Source line tracking
- Deterministic claim IDs
- JSON persistence
- HTML review output

Not yet implemented:

- LLM-based semantic claim extraction
- Attribution extraction and preservation
- Reliable evidence-status classification
- Cross-document claim matching
- Discrepancy / conflict detection
- PDF input
- GUI / drag-and-drop workflow

## Next milestone

The next milestone is to reconnect the LLM semantic layer so that the system extracts genuine claims from context-preserving text chunks while Python continues to manage deterministic provenance fields. After that, the project will move toward cross-document matching and discrepancy flags.

## Design principle

AI handles the research groundwork. Investors keep the judgment.
