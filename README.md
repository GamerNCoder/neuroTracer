# 📘 **TraceNeuro (Cognitive Authenticity Engine)**

## 📚 **Complete Platform Documentation**

**👉 For a comprehensive, detailed summary of the entire platform (features, tech stack, WIP, open questions, architecture, API, database, everything), see:**

**[`docs/PLATFORM_SUMMARY.md`](docs/PLATFORM_SUMMARY.md)** - Complete technical summary with all minute details

---

# ✅ Current status (May 2026)

- **Offline scoring**: no OpenAI/Claude/Gemini calls; detection is computed locally from cognitive markers.
- **Calibrated output**: `data/models/calibration.json` provides `classification`, `confidence`, and `calibrated=true`.
- **Human corpus**: pre‑2012 blogs scraped via Wayback (`data/human/blogs-pre2012/`).
- **Batch scraping**: resumable batches toward a larger corpus (e.g. 1000).
- **Training**: `make tune-blogs` retrains calibration and prints corpus eval.

### Quickstart (local)

```bash
cd neurotracer
./setup.sh

# Run API + web together
make dev-all
```

- Dashboard: `http://127.0.0.1:3000`
- API docs: `http://127.0.0.1:8000/docs`

### Data + training commands

```bash
# Scrape one batch (100) toward 1000 posts
make scrape-1k

# Export dataset.jsonl + splits (local only)
make build-dataset

# Retrain blog-tuned calibration and evaluate corpus
make tune-blogs
```

# 🧠 **TraceNeuro — Cognitive Authenticity Engine (Human Cognition Fingerprint + Hybrid Detection)**

TraceNeuro is an **LLM-proof Cognitive Authenticity Engine** that identifies human cognitive signatures inside text using *reasoning patterns*, *semantic drift*, *cadence irregularity*, *stylometry*, and *non-linear thought markers*.

Unlike "AI detectors" (perplexity, logits, stylistic heuristics), TraceNeuro analyzes **how the mind thinks**, not **how the model writes**.

This makes it resilient against:

* paraphrasing
* rewriting
* GPT/Claude "humanization" modes
* future LLM improvements
* hybrid AI+human text

TraceNeuro's output is a multi-component **HumanScore™**, built from real cognitive markers that AI still fails to simulate consistently.

---

## 🚀 **Why TraceNeuro Exists**

Traditional AI detectors are built on:

* token probabilities
* burstiness/perplexity
* surface-level linguistic cues

These fail instantly against:

* simple paraphrasing
* hybrid editing
* GPT-5+ depth
* humanization tools
* prompt engineering

**TraceNeuro is not a detector.**

It's a **cognitive authenticity layer**.

It asks:

> "Does this text contain the underlying cognitive patterns associated with human reasoning?"

This is the future of:

* compliance
* publishing
* academic integrity
* journalism
* enterprise governance
* AI/hybrid authorship verification

---

# 🏗️ **System Architecture (MVP Architecture Diagram)**

```
                          ┌─────────────────────────────┐
                          │       Web / CLI Client       │
                          │ (upload, paste, API request) │
                          └───────────────┬──────────────┘
                                          │
                                          ▼
                               ┌──────────────────── ┐
                               │  Edge Gateway/API   │
                               │  Auth, rate limits  │
                               └───────────┬──────────┘
                                           │
                  ┌────────────────────────┼────────────────────────┐
                  ▼                        ▼                        ▼
       ┌───────────────────┐    ┌──────────────────────┐   ┌────────────────────┐
       │ Preprocessing Svc │    │  Cognitive Marker     │   │  LLM Baseline Svc  │
       │ - cleaning        │    │    Extractor          │   │  (optional)        │
       │ - segmentation    │    │ - drift vectors       │   │ - perplexity check │
       │ - tokenization    │    │ - cadence variance    │   │ - baseline compare │
       └─────────┬─────────┘    │ - hedging signals     │   └─────────┬──────────┘
                 │              │ - metaphor rarity      │             │
                 ▼              │ - coherence breaks     │             ▼
       ┌───────────────────┐    │ - stylometric graph    │   ┌────────────────────┐
       │ Feature Encoder   │    └──────────┬─────────────┘   │ Fusion Layer        │
       │ - numerical vecs  │               │                 │ - marker weighting  │
       │ - embeddings      │               ▼                 │ - final scoring     │
       └─────────┬─────────┘    ┌──────────────────────┐     └─────────┬──────────┘
                 │              │  HumanScore Engine    │               │
                 ▼              │ - human index         │               ▼
       ┌───────────────────┐    │ - AI index            │   ┌────────────────────────────┐
       │ Report Builder    │    │ - hybrid index        │   │ Results API / Dashboard UI │
       │ - heatmaps        │    └──────────────────────┘   └────────────────────────────┘
       │ - breakdown       │
       └───────────────────┘
```

---

# 📦 **Repository Structure**

```
neurotrace/
  ├── engine/
  │     ├── preprocessing/
  │     ├── markers/
  │     │     ├── drift/
  │     │     ├── cadence/
  │     │     ├── hedging/
  │     │     ├── metaphor/
  │     │     ├── coherence/
  │     │     └── stylometry/
  │     ├── embeddings/
  │     ├── fusion/
  │     └── humanscore/
  │
  ├── api/
  │     ├── routes/
  │     ├── scoring/
  │     ├── auth/
  │     └── report/
  │
  ├── web/
  │     ├── dashboard/
  │     ├── components/
  │     └── auth/
  │
  ├── data/
  │     ├── human/
  │     ├── ai/
  │     └── hybrid/
  │
  ├── docs/
  └── tests/
```
---

# 🧩 **Core Algorithms (High-level)**

TraceNeuro uses a multi-signal approach:

### ✔ Drift Vector Analysis

Tracks meaning changes across sentences.

### ✔ Cadence Variability

Humans produce uneven pacing; AI is too smooth.

### ✔ Hedging & Cognitive Bias Markers

Humans hedge inconsistently; AI hedges predictably.

### ✔ Metaphor Rarity & Asymmetry

Humans produce unique metaphors; AI reuses patterns.

### ✔ Coherence Breaks

Humans change direction mid-thought; AI rarely does.

### ✔ Stylometric Fingerprint

Individual cognitive "voiceprint" extracted as a graph.

Weighted and fused → HumanScore™.

---

# 🤝 **Contribution**

This project is in early prototyping stage.

Collaborators should follow:

* clean commits
* modular PRs
* architecture first, implementation second
* no features without test coverage
* use examples from `/data/`

---

# 📝 **License**

MIT (may be upgraded to PolyForm or Custom Enterprise License later).

---

# 🚀 **Quick Start**

```bash
# Run setup script
./setup.sh

# Start the API server
cd api && uvicorn main:app --reload

# Start the web dashboard
cd web && npm run dev
```

---

# 📊 **Sample API Usage**

```bash
curl -X POST http://localhost:8000/api/v1/score \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your text here...",
    "options": {
      "include_breakdown": true,
      "include_heatmap": false
    }
  }'
```

See `docs/sample_payloads.md` for more examples.

