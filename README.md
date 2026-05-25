# Streamlit Enterprise AI Agent

## Overview

This project is a **local Python-based FP&A analytics application** that combines **Alteryx-governed financial logic**, **Google BigQuery**, and **Gemini (LLM) narrative synthesis** to deliver an interactive **Budget vs Actual variance analysis assistant**.

The goal of this solution is to help **FP&A teams, business analysts, and finance leaders**:

* Quickly understand **budget vs actual variances**
* Identify **overspends and material drivers**
* Detect **trend shifts and anomalies**
* Receive **executive-ready explanations** without sacrificing data trust or governance

This is **not a chatbot** and **not an AI that calculates numbers**. All calculations are deterministic, versioned, and controlled by Alteryx logic. AI is used **only for narrative explanation**.

---

## High-Level Architecture

**Local Components**:

* Python application
* FastAPI MCP server
* Streamlit Chat UI

**Cloud Components**:

* Google BigQuery (semantic FP&A layer)
* Gemini (Vertex AI) for narrative synthesis

**Control Principle**:

> Alteryx controls *what data exists*. Gemini controls *how it is explained*.

---

## Data Architecture (FP&A Model)

The solution follows a **Bronze → Silver → Gold** pattern.

### Bronze (Raw)

Raw financial source data, ingested as-is:

* GL transactions
* Budget plans
* Cost center masters
* Account hierarchies

These are stored in BigQuery but **never exposed directly to AI**.

### Silver (Conformed)

Standardized and enriched financial models:

* Cleaned GL transactions
* Conformed cost center and account dimensions
* Budget and actuals aligned to fiscal calendars

This layer ensures consistent joins, keys, and definitions.

### Gold (Semantic / AI-Ready)

Pre-aggregated, governed FP&A outputs:

* Monthly Budget vs Actual fact tables
* Overspend hotlists
* Trend shift signal views
* Variance driver explanation views

This is the **only layer** used by the assistant.

---

## Project Structure

```
BVA-ADK/
│
├── .venv/                   # Python virtual environment
│
├── app/                     # Backend application (MCP server)
│   ├── tools/               # Deterministic FP&A tools
│   │   ├── overspend_hotlist.py
│   │   ├── trend_shift_signals.py
│   │   └── variance_explain.py
│   │
│   ├── bigquery.py           # BigQuery client utilities
│   ├── main.py               # FastAPI MCP server
│   ├── models.py             # Pydantic response models
│   ├── settings.py           # Project and dataset configuration
│   ├── Dockerfile.mcp        # Container definition for MCP server
│   └── requirements.mcp.txt  # MCP server dependencies
│
├── client/                   # Client-side AI + MCP orchestration
│   ├── gemini_mcp_client.py
│   ├── mcp_registry.py
│   ├── prompts.py
│   └── test_client.py
│
├── src/                      # User-facing interfaces
│   ├── chat_ui.py            # Streamlit Chat UI
│   └── agent.py              # Optional agent orchestration
│
├── requirements.txt          # UI and client dependencies
└── README.md                 # This document
```

---

## Backend: MCP Server (`app/`)

### `main.py`

This file runs a **FastAPI-based MCP (Model Control Plane) server**.

Responsibilities:

* Exposes a single `/mcp` endpoint
* Routes requests to deterministic FP&A tools
* Ensures the server **never crashes**
* Normalizes time periods (YYYY-MM)
* Enforces strict tool boundaries

Supported tools:

* `overspend_hotlist`
* `trend_shift_signals`
* `variance_explain`

If no data exists for a period, it returns a **clear, explicit message**.

---

### `models.py`

Defines **Pydantic response schemas** used across the system.

Purpose:

* Enforces consistent response shapes
* Prevents malformed or hallucinated outputs
* Guarantees that AI only receives structured, validated data

---

### `bigquery.py`

Utility module for creating BigQuery clients.

Responsibilities:

* Authentication
* Centralized client creation
* Prevents duplicate connection logic

---

### `settings.py`

Central configuration for:

* GCP project ID
* BigQuery dataset
* Environment-specific settings

This keeps environment logic **out of business logic**.

---

## Deterministic FP&A Tools (`app/tools/`)

Each tool is **pure analytics logic**. No AI. No interpretation.

### `overspend_hotlist.py`

Purpose:

* Identifies largest unfavorable variances for a given period

Logic:

* Reads from `v_hook_overspend_hotlist`
* Sorts by absolute variance
* Returns top overspend categories

Used for:

* “What are the biggest overspends?” questions

---

### `trend_shift_signals.py`

Purpose:

* Detects abnormal variance behavior using historical context

Logic:

* Compares current variance to rolling averages
* Uses z-score logic
* Flags statistically significant deviations

Used for:

* “What changed this month?”
* “What trends shifted?”

---

### `variance_explain.py`

Purpose:

* Explains *why* a variance exists

Logic:

* Reads pre-aggregated variance driver views
* Groups by department, cost center, GL, or category
* Returns only material drivers

Used for:

* “Explain the variance” questions

---

## Client Layer (`client/`)

### `gemini_mcp_client.py`

This is the **core orchestration layer**.

It performs **three strictly separated steps**:

1. **Tool Routing**

   * Gemini selects *which tool* to use
   * Must return strict JSON only

2. **Deterministic Execution**

   * Calls MCP server
   * Executes Alteryx-governed logic

3. **Narrative Synthesis**

   * Gemini receives structured results
   * Generates executive-ready commentary
   * Cannot invent numbers or logic

This design ensures:

* No hallucinations
* Full auditability
* Clear AI boundaries

---

### `prompts.py`

Stores prompt templates used by Gemini.

Includes:

* Tool routing prompt (strict JSON)
* Narrative synthesis prompt (read-only)

Prompts are versionable and inspectable.

---

### `mcp_registry.py`

Defines available tools and their metadata.

Purpose:

* Central registry for allowed capabilities
* Prevents unauthorized tool execution

---

## Chat UI (`src/chat_ui.py`)

Built with **Streamlit**, styled to match **Alteryx One**.

Features:

* Suggested FP&A questions
* Chat-based interaction
* Executive-ready responses
* Expandable supporting data
* Error-safe handling

The UI never queries raw data directly.

---

## AI Safety & Governance Principles

This solution is intentionally designed to be **enterprise-safe**:

* AI never calculates numbers
* AI never sees raw transactions
* AI never invents logic
* All calculations are pre-approved
* All outputs are explainable

Gemini is used as a **narrative layer only**.

---

## Who This Is For

* FP&A Analysts
* Finance Business Partners
* Controllers
* Finance Transformation Leaders
* CFO organizations

---

## Why This Matters

This solution turns FP&A logic into a **reusable, governed asset**:

* Built once in Alteryx
* Reused across reports, dashboards, and AI
* Explained instantly
* Trusted always

---

## Next Steps (Optional)

* Deploy MCP server to Cloud Run
* Secure UI behind IAP
* Add additional FP&A hooks
* Extend to forecasting and scenario analysis

---

**Built with Alteryx + Google Cloud**

# alteryx-fpa-variance-agent
