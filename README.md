# StreamFuse

**Streaming Live RAG with Early Retrieval, Multi-Intent Decomposition, Evidence Fusion, and Session-Aware Refinement**

Samsung PRISM Generative AI Hackathon 2026  
**Theme 4 — Streaming Live RAG**

---

## Overview

StreamFuse is a Streaming Retrieval-Augmented Generation system designed for natural conversations where a user may reveal their intent gradually, ask multiple questions in a single utterance, or modify important details while the conversation is still ongoing.

Unlike traditional RAG systems that wait for a complete query before retrieval begins, StreamFuse can process incremental transcript chunks, decide whether retrieval is necessary, decompose compound requests into multiple searchable queries, retrieve evidence using hybrid search, fuse results, generate grounded responses, and refine previous results when new information arrives.

The system maintains only session-scoped memory.

---

## Problem

Traditional RAG systems generally assume that the user provides a complete and well-structured query before retrieval begins.

Real conversations behave differently.

Users may:

- reveal their intent gradually
- combine several questions in one sentence
- change constraints during the conversation
- add important details after retrieval has already started
- request formatting changes that do not require another search

StreamFuse treats retrieval as a continuously evolving process rather than a single one-shot search.

---

## Core Features

### 1. Retrieval Controller

Every incoming request is classified into one of three retrieval states:

- `WAIT` — the request appears incomplete and retrieval should not begin yet
- `RETRIEVE` — enough information is available to search the corpus
- `SUPPRESS` — the user only wants to transform or reformat an existing answer, so another corpus search is unnecessary

Example:

```text
"I need to plan"
→ WAIT

"I need to plan a workshop in Pune for 30 people"
→ RETRIEVE

"Put that answer in bullet points"
→ SUPPRESS
```

---

### 2. Streaming and Early Retrieval

StreamFuse supports incremental transcript chunks through the `/stream-chunk` API.

Example:

```text
Chunk 1:
"I need to plan"

Decision:
WAIT


Chunk 2:
"a workshop in Pune for 30 people"

Accumulated transcript:
"I need to plan a workshop in Pune for 30 people"

Decision:
RETRIEVE


Chunk 3:
"and I need the cancellation policy and catering options"

Accumulated transcript:
"I need to plan a workshop in Pune for 30 people and I need the cancellation policy and catering options"

Decision:
RETRIEVE
```

This allows retrieval to begin before the complete utterance has finished.

---

### 3. Multi-Intent Decomposition

A single natural-language request may contain several independent information needs.

Example input:

```text
Find a venue in Pune for 30 people and tell me the cancellation policy and catering options
```

StreamFuse decomposes it into:

```text
1. Find a venue in Pune for 30 people
2. Tell me the cancellation policy
3. Catering options
```

Each sub-query is then searched independently.

---

### 4. Hybrid Retrieval

StreamFuse combines sparse and dense retrieval.

The current retrieval pipeline uses:

- BM25 for lexical matching
- Sentence Transformers for semantic similarity
- Reciprocal Rank Fusion for combining rankings

Embedding model:

```text
sentence-transformers/all-MiniLM-L6-v2
```

The hybrid approach helps capture both exact keyword matches and semantically similar information.

---

### 5. Reciprocal Rank Fusion

Dense and sparse search results are combined using Reciprocal Rank Fusion.

The system independently ranks results from:

```text
BM25
+
Dense Embedding Similarity
```

and merges them into a final ranking using RRF.

This reduces dependence on a single retrieval method.

---

### 6. Evidence Fusion

Evidence retrieved from different sub-queries is collected and combined.

The pipeline:

```text
Sub-query 1 ─┐
Sub-query 2 ─┼─→ Retrieval → Evidence Collection
Sub-query 3 ─┘
                         ↓
                  Deduplication
                         ↓
                      Ranking
                         ↓
                 Grounded Answer
```

Duplicate evidence is removed before answer generation.

---

### 7. Grounded Answer Generation

StreamFuse generates responses using evidence returned from the local corpus.

Each response can include:

- generated answer
- retrieved evidence
- document identifiers
- section identifiers
- citations
- latency measurements

Example:

```text
Based on the available corpus:

- Venue A provides lunch, tea and vegetarian catering options. [demo_venues document]
- Venue A is located in Pune and can accommodate up to 40 attendees. [demo_venues document]
- Venue A allows cancellation up to 7 days before the event with a full refund. [demo_venues document]
```

If sufficient evidence is not available, the system is designed to avoid inventing unsupported information.

---

### 8. Session-Aware Refinement

StreamFuse maintains session-scoped conversational state.

Initial request:

```text
Find a venue in Pune for 30 people and tell me the cancellation policy.
```

Later request:

```text
Actually make that 50 people.
```

The system detects that the second request is a refinement and updates the earlier query:

```text
30 people
↓
50 people
```

Relevant session context is preserved instead of treating the request as a completely unrelated conversation.

---

### 9. Retrieval Suppression

Not every follow-up request requires retrieval.

Example:

```text
Put that in bullet points.
```

If the session already contains an answer, StreamFuse can return:

```text
decision = SUPPRESS
retrieval_ms = 0
```

This prevents unnecessary corpus searches.

---

### 10. Session-Scoped Memory

The current prototype stores memory only for the active session.

Stored session information includes:

- current query
- previous answer
- evidence
- citations
- response version

No persistent cross-session user profile is created.

---

## Architecture

```text
                    USER TRANSCRIPT
                           |
                           v
                +---------------------+
                | Retrieval Controller|
                | WAIT / RETRIEVE /   |
                | SUPPRESS            |
                +----------+----------+
                           |
                           v
                +---------------------+
                | Multi-Intent        |
                | Query Decomposer    |
                +----------+----------+
                           |
                 +---------+---------+
                 |         |         |
                 v         v         v
                Q1        Q2        Q3
                 |         |         |
                 +---------+---------+
                           |
                           v
                +---------------------+
                | Hybrid Retrieval    |
                | BM25 + Embeddings   |
                +----------+----------+
                           |
                           v
                +---------------------+
                | Reciprocal Rank     |
                | Fusion              |
                +----------+----------+
                           |
                           v
                +---------------------+
                | Evidence            |
                | Deduplication       |
                +----------+----------+
                           |
                           v
                +---------------------+
                | Grounded Answer     |
                | + Citations         |
                +----------+----------+
                           |
                           v
                +---------------------+
                | Session Memory      |
                | + Telemetry         |
                +---------------------+
```

---

## Streaming Flow

```text
0.0s
"I need to plan"
        |
        v
      WAIT


0.8s
"I need to plan a workshop in Pune for 30 people"
        |
        v
 EARLY RETRIEVAL


1.6s
"I need to plan a workshop in Pune for 30 people
and I need the cancellation policy and catering options"
        |
        v
 MULTI-INTENT DECOMPOSITION
        |
        v
 HYBRID RETRIEVAL
        |
        v
 EVIDENCE FUSION
        |
        v
 GROUNDED ANSWER
```

---

## Project Structure

```text
streamfuse-rag/
|
├── backend/
│   ├── __init__.py
│   ├── main.py
│   │
│   └── rag/
│       ├── __init__.py
│       ├── controller.py
│       ├── decomposer.py
│       ├── generator.py
│       ├── pipeline.py
│       ├── refiner.py
│       ├── retriever.py
│       └── session.py
│
├── frontend/
│
├── data/
│   └── corpus/
│       └── demo_venues.txt
│
├── tests/
│   ├── __init__.py
│   ├── benchmark.py
│   ├── test_pipeline.py
│   ├── test_refinement.py
│   └── test_retrieval.py
│
├── .gitignore
├── README.md
└── requirements-ai.txt
```

---

## Backend API

The backend is implemented using FastAPI.

Default local server:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

---

## Health Endpoint

```http
GET /health
```

Example response:

```json
{
  "status": "healthy",
  "engine": "ready"
}
```

---

## Standard RAG Endpoint

```http
POST /stream
```

Request:

```json
{
  "session_id": "demo123",
  "text": "Find a venue in Pune for 30 people and tell me the cancellation policy and catering options"
}
```

Example response structure:

```json
{
  "decision": "RETRIEVE",
  "refinement": false,
  "query": "Find a venue in Pune for 30 people and tell me the cancellation policy and catering options",
  "answer": "Based on the available corpus...",
  "subqueries": [
    "Find a venue in Pune for 30 people",
    "tell me the cancellation policy",
    "catering options"
  ],
  "evidence": [],
  "citations": [],
  "version": 1,
  "metrics": {
    "retrieval_ms": 26.65,
    "total_ms": 26.87
  }
}
```

---

## Streaming Endpoint

```http
POST /stream-chunk
```

Request format:

```json
{
  "session_id": "stream-demo-001",
  "chunk": "I need to plan",
  "is_final": false
}
```

The same `session_id` should be reused across chunks belonging to the same utterance.

---

## Streaming Example

### Request 1

```json
{
  "session_id": "stream-demo-001",
  "chunk": "I need to plan",
  "is_final": false
}
```

Expected decision:

```text
WAIT
```

### Request 2

```json
{
  "session_id": "stream-demo-001",
  "chunk": "a workshop in Pune for 30 people",
  "is_final": false
}
```

Accumulated transcript:

```text
I need to plan a workshop in Pune for 30 people
```

Expected decision:

```text
RETRIEVE
```

### Request 3

```json
{
  "session_id": "stream-demo-001",
  "chunk": "and I need the cancellation policy and catering options",
  "is_final": true
}
```

Expected behavior:

```text
RETRIEVE
→ MULTI-INTENT DECOMPOSITION
→ HYBRID RETRIEVAL
→ EVIDENCE FUSION
→ GROUNDED ANSWER
```

---

## Session Refinement Example

Initial request:

```json
{
  "session_id": "demo-refinement",
  "text": "Find a venue in Pune for 30 people and tell me the cancellation policy"
}
```

Follow-up request:

```json
{
  "session_id": "demo-refinement",
  "text": "Actually make that 50 people"
}
```

Expected result:

```text
refinement = true
```

Updated query:

```text
Find a venue in Pune for 50 people and tell me the cancellation policy
```

---

## Retrieval Suppression Example

After a previous answer exists:

```json
{
  "session_id": "demo-refinement",
  "text": "Put that in bullet points"
}
```

Expected:

```text
decision = SUPPRESS
retrieval_ms = 0
```

---

## Prototype Benchmark

The current prototype benchmark produced:

| Test | Result |
|---|---|
| Incomplete utterance detection | PASS |
| Normal retrieval | PASS |
| Multi-intent retrieval | PASS |
| Session refinement | PASS |
| Retrieval suppression | PASS |
| Behavior tests passed | 5 / 5 |
| Behavior test accuracy | 100% |
| Average processing latency | 35.19 ms |

Observed individual test timings during the benchmark included approximately:

```text
Incomplete utterance:   0.02 ms
Normal retrieval:      12.49 ms
Multi-intent retrieval: 93.05 ms
```

These measurements were produced using the current local prototype and temporary demo corpus.

They are not presented as production-scale RAG accuracy or latency measurements.

---

## Observability

StreamFuse exposes information useful for understanding what the retrieval pipeline is doing.

Responses may contain:

```text
decision
refinement
query
answer
subqueries
evidence
citations
version
retrieval_ms
total_ms
full_transcript
```

This allows the frontend to visualize the internal retrieval process.

---

## Technology Stack

### AI and Retrieval

- Python
- Sentence Transformers
- BM25
- NumPy
- Reciprocal Rank Fusion
- PyPDF

### Embedding Model

```text
sentence-transformers/all-MiniLM-L6-v2
```

### Backend

- FastAPI
- Pydantic
- Uvicorn

### Frontend

- React
- Vite

### Development and Collaboration

- Git
- GitHub
- feature branches
- pull requests
- VS Code

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/PrithadeyDS/streamfuse-rag.git
cd streamfuse-rag
```

---

### 2. Create a Python Virtual Environment

Windows:

```powershell
python -m venv .venv
```

Activate:

```powershell
.venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate again:

```powershell
.venv\Scripts\Activate.ps1
```

---

### 3. Install Dependencies

```powershell
pip install -r requirements-ai.txt
```

---

### 4. Run the Backend

```powershell
python -m uvicorn backend.main:app --reload
```

Expected server address:

```text
http://127.0.0.1:8000
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

---

## Running the Tests

### Retrieval Test

```powershell
python -m tests.test_retrieval
```

### Refinement Test

```powershell
python -m tests.test_refinement
```

### Complete Pipeline Test

```powershell
python -m tests.test_pipeline
```

### Benchmark

```powershell
python -m tests.benchmark
```

---

## Current Development Corpus

The current development version uses a small temporary demo corpus located in:

```text
data/corpus/
```

Example development data includes venue capacity, catering options, and cancellation rules.

The temporary demo corpus exists only to validate the RAG architecture and end-to-end prototype behavior.

It should not be interpreted as the final production knowledge corpus.

---

## Current Limitations

The current prototype has the following limitations:

- development testing currently uses a small temporary demo corpus
- voice input is simulated using transcript chunks
- query decomposition currently uses lightweight deterministic logic
- answer generation currently extracts and formats retrieved evidence instead of relying on a large generative model
- character-based chunking is currently simple and may occasionally split text at inconvenient positions
- session memory is stored in memory and resets when the backend restarts
- production-scale corpus testing has not yet been completed
- benchmark results currently measure prototype behavior rather than full RAG quality

---

## Design Philosophy

StreamFuse intentionally uses a lightweight architecture.

Instead of introducing a large multi-agent orchestration framework, the system uses focused components:

```text
Controller
↓
Decomposer
↓
Retriever
↓
Fusion
↓
Generator
↓
Session Memory
```

This keeps the pipeline understandable, measurable, and efficient.

---

## Team

### Pritha Dey — AI Engineer

Responsible for:

- Streaming RAG pipeline
- retrieval controller
- WAIT / RETRIEVE / SUPPRESS logic
- multi-intent query decomposition
- BM25 retrieval
- dense semantic retrieval
- Reciprocal Rank Fusion
- evidence deduplication
- grounded answer generation
- session refinement
- retrieval suppression
- streaming transcript logic
- prototype benchmarking

---

### Bhishmita — Frontend Engineer

Responsible for:

- frontend interface
- conversation interface
- streaming interaction experience
- retrieval-state visualization
- decomposed query display
- evidence visualization
- citation display
- telemetry visualization
- answer-version visualization

---

### Shriya — Backend and Systems Engineer

Responsible for:

- FastAPI integration
- backend orchestration
- API request and response handling
- system integration
- frontend-backend communication
- health checks
- runtime reliability
- integration testing

---

## GitHub Collaboration Workflow

The project uses one shared GitHub repository.

Development branches:

```text
main
├── ai-pritha
├── frontend-bhishmita
└── backend-shriya
```

Primary ownership:

```text
Pritha:
backend/rag/
AI tests
retrieval pipeline

Bhishmita:
frontend/

Shriya:
backend/main.py
backend/system integration
```

Changes are integrated into `main` through pull requests.

---

## Theme 4 Alignment

StreamFuse currently demonstrates the following Theme 4 capabilities:

- streaming transcript processing
- retrieval decision logic
- early retrieval before complete utterance termination
- multi-intent decomposition
- multi-query retrieval
- dense retrieval
- sparse retrieval
- rank fusion
- evidence deduplication
- grounded responses
- citations
- late-detail refinement
- session-scoped context
- retrieval suppression
- retrieval latency measurement
- answer versioning
- runtime observability

---

## Example End-to-End Flow

```text
USER STARTS SPEAKING

"I need to plan"
        |
        v
      WAIT


USER CONTINUES

"a workshop in Pune for 30 people"
        |
        v
     RETRIEVE
        |
        v
Hybrid Corpus Search


USER CONTINUES

"and I need the cancellation policy
and catering options"
        |
        v
Multi-Intent Decomposition
        |
        +-----------------------------+
        |              |              |
        v              v              v
 Venue Search    Cancellation     Catering
        |              |              |
        +--------------+--------------+
                       |
                       v
                Hybrid Retrieval
                       |
                       v
                 RRF Fusion
                       |
                       v
              Evidence Deduplication
                       |
                       v
                Grounded Answer
                       |
                       v
              Citations + Metrics


USER ADDS DETAIL

"Actually make that 50 people"
        |
        v
 Session Refinement
        |
        v
 Updated Retrieval
        |
        v
 Answer Version 2


USER SAYS

"Put that in bullet points"
        |
        v
     SUPPRESS
        |
        v
No unnecessary retrieval
```

---

## Final Goal

StreamFuse aims to make retrieval follow the natural flow of conversation instead of forcing the user to formulate a perfect query before the system can begin searching.

The prototype focuses on making streaming retrieval:

- fast
- observable
- grounded
- session-aware
- efficient
- easy to understand
- easy to extend