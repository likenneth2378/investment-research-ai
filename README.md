# Investment Research AI

Evidence-first investment research workflow for claim-level traceability and cross-document review.

## Current prototype

The current version reads multiple TXT files, groups source text into context-preserving chunks, attaches deterministic source metadata, saves the ledger as JSON, and generates a simple HTML review page.

Current fields include:

- `claim_id`
- `document_id`
- `source_text`
- `source_line_start`
- `source_line_end`
- `evidence_status` (currently a test placeholder until the LLM layer is restored)

## Why this project exists

The project started from a practical investment-research workflow problem: AI-generated summaries can strengthen or distort claims when source attribution is lost. A representative failure case is turning a statement such as "the company says it owns 11 patents" into "the company owns 11 patents".

The project therefore focuses on keeping claims traceable to source material before moving toward higher-level research output.

## Current status

This repository is an early prototype, not a finished product.

Implemented:

- Multi-file TXT ingestion
- Relative project paths
- Source document tracking
- Source line-range tracking
- Deterministic claim IDs
- Context-preserving chunk baseline
- JSON persistence
- HTML review output

Not yet implemented:

- LLM-based semantic claim extraction from chunks
- Attribution extraction and preservation
- Reliable evidence-status classification
- Cross-document claim matching
- Discrepancy / conflict detection
- PDF input
- GUI / drag-and-drop workflow

## Setup

This project uses a bring-your-own-key (BYOK) setup. Each user supplies their own OpenRouter API key; no shared project API key is included in the repository.

1. Clone or download the repository.
2. Install the Python dependency:

```bash
pip install openai
```

3. Copy `.env.example` to `.env` and replace the placeholder with your own OpenRouter API key:

```text
OPENROUTER_API_KEY=your_api_key_here
```

4. Make the key available as an environment variable before running the program. The current prototype reads it with:

```python
os.getenv("OPENROUTER_API_KEY")
```

5. Run:

```bash
python main.py
```

The local `.env` file is ignored by Git and should never be committed.

> Note: the current prototype does not yet automatically load `.env`; automatic `.env` loading will be added later. Until then, the environment variable must be available to the Python process.

## Next milestone

The next milestone is to reconnect the LLM semantic layer so that the system treats each chunk as an extraction context rather than as a claim itself. One chunk may therefore produce zero, one, or multiple semantic claims. Python will continue to manage deterministic provenance fields such as document IDs and source locations.

After that, the project will move toward attribution preservation, cross-document matching, and discrepancy flags.

## Design principle

AI handles the research groundwork. Investors keep the judgment.
