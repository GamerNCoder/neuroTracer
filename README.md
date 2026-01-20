# 📘 **README.md — TraceNeuro / Cognitive Authenticity Engine (Working Name)**

*(Working namespace: traceneuro/core — final brand TBD)*

---

## 📚 **Complete Platform Documentation**

**👉 For a comprehensive, detailed summary of the entire platform (features, tech stack, WIP, open questions, architecture, API, database, everything), see:**

**[`docs/PLATFORM_SUMMARY.md`](docs/PLATFORM_SUMMARY.md)** - Complete technical summary with all minute details

---

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

# 📅 **Roadmap (Realistic, Non-Bullshit)**

## **Phase 0 — Foundations (Week 1–2)**

* Setup repository + monorepo tooling
* Implement preprocessing engine
* Implement basic API
* Collect 500 human samples (pre-2012 blogs, Reddit 2009–2012, diary corpora)

## **Phase 1 — Cognitive Marker MVP (Week 3–6)**

* Build semantic drift extractor
* Build cadence variance module
* Build hedging detector
* Build metaphor rarity counter
* Build coherence break detector
* Build stylometric fingerprint graphs

## **Phase 2 — Fusion Layer + HumanScore (Week 6–8)**

* Weight markers
* Normalize marker distributions
* Hybrid score integration
* HumanScore™ v1

## **Phase 3 — UI + API Launch (Week 8–10)**

* Minimal dashboard
* Upload or paste-box
* JSON API endpoints
* Save scoring history
* Export reports

## **Phase 4 — Hybrid Detection Engine (Week 10–12)**

* Build training set (Human→AI→Human)
* Classify hybrid segments
* Add hybrid index to HumanScore™

## **Phase 5 — V1 (3–6 months)**

* Scaling
* Caching
* Deep reporting
* Team mode
* Audit logs
* Enterprise API
* Model fine-tuning on custom corpora

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

# 🔨 **Initial Commit Layout (copy-paste this into your GitHub project board)**

### **Commit 1:** initialize monorepo, license, readme

### **Commit 2:** add preprocessing pipeline

### **Commit 3:** implement text cleaning & segmentation

### **Commit 4:** add drift module (baseline)

### **Commit 5:** add cadence analysis module

### **Commit 6:** add hedging detector

### **Commit 7:** metaphor rarity counter

### **Commit 8:** coherence break graph

### **Commit 9:** stylometric extractor

### **Commit 10:** embeddings + feature encoder

### **Commit 11:** fusion model (HumanScore)

### **Commit 12:** first API endpoints

### **Commit 13:** web UI scaffolding (Next.js)

### **Commit 14:** scoring history database

### **Commit 15:** deploy to Vercel (internal)

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

