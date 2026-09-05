# He Slide Harmonizer Agent

> **Domain:** Digital Pathology & Quantitative Histopathology
> **Reference Guidelines & Standards:** `College of American Pathologists (CAP) Synoptic Protocols & DICOM WSI`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

**He Slide Harmonizer Agent** is an advanced analytical and computational platform implementing Optical Stain Normalization & Scanner Harmonizer (Macenko/Vahadane). It provides multi-agent evaluation of digital pathology slide quality, stain consistency, and cross-scanner harmonization.

---

## ⚙️ Key Capabilities & Algorithmic Modules

### 🔬 Core Algorithmic & Evaluation Engines

- **`Severity`** — dedicated module for severity evaluation and state verification.
- **`DomainKnowledgeRegistry`**: Enterprise domain rules, guideline matrices, and evidence benchmarks.
- **`AgentAlert`** — dedicated module for agent alert evaluation and state verification.
- **`ColorVectorEstimatorAgent`**: Specialized Sub-Agent 1 for he-slide-harmonizer-agent
- **`StainMatrixNormalizerAgent`**: Specialized Sub-Agent 2 for he-slide-harmonizer-agent
- **`QualityConsistencyAgent`**: Specialized Sub-Agent 3 for he-slide-harmonizer-agent

### 🏗️ Architecture Components

- **`agents/`** — Enterprise agent framework with supervisor orchestrator, specialized workers, and FastAPI REST API
- **`he_slide_harmonizer_agent/`** — Clinical agent package with coordinator, sub-agents, and domain engine
- **`slide_harmonizer.py`** — Core harmonization module with CLI
- **`enrichment.py`** — Enrichment feature suite with multiple evaluation engines
- **`simulator.py`** — High-throughput batch simulation and stress testing

---

## 💻 Installation

```bash
# Clone the repository
git clone https://github.com/abusuraihsakhri/he-slide-harmonizer-agent.git
cd he-slide-harmonizer-agent

# Install dependencies
pip install fastapi uvicorn pydantic pytest
```

---

## 💻 CLI Quickstart & Usage

### 1. Single Task Evaluation
```bash
python cli.py audit
```

### 2. Batch Processing
```bash
python cli.py batch -i sample.csv -o results.csv
```

### 3. System Query Chat
```bash
python cli.py chat "What is the system status?"
```

### 4. Verify Audit Trail Integrity
```bash
python cli.py verify-audit
```

### 5. Launch REST API Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### Parameter Reference
- `--task-id`: Specifies input measurement or parameter value.
- `--target`: Specifies input measurement or parameter value.
- `--primary`: Specifies input measurement or parameter value.
- `--secondary`: Specifies input measurement or parameter value.
- `--critical`: Specifies input measurement or parameter value.
- `--status`: Specifies input measurement or parameter value.
- `--input`: Specifies input measurement or parameter value.
- `--output`: Specifies input measurement or parameter value.

### Input Data Schema

| Field | Description | Requirement |
|:------|:------------|:------------|
| `case_id` | Parameter / observation metric | Required |
| `patient_synthetic_id` | Parameter / observation metric | Required |
| `metric_primary` | Parameter / observation metric | Required |
| `metric_secondary` | Parameter / observation metric | Required |
| `is_stat` | Parameter / observation metric | Required |
| `status_flag` | Parameter / observation metric | Required |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active AST and regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition. Per-session random key generation prevents audit forgery.
* **Path Traversal Protection:** All batch file I/O is validated to remain within the working directory.
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances (`llama3`, `mistral`), Claude 3.5 Sonnet, GPT-4o, and deterministic test mocks.
* **Active Learning Bayesian Calibration:** Dynamic tracker updating worker reliability weights and monitoring Brier calibration drift.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py 1000
```

---

## 🐳 Container Deployment

```bash
docker build -t he-slide-harmonizer-agent .
docker run -p 8000:8000 he-slide-harmonizer-agent
```

---

## 📁 Project Structure

```
he-slide-harmonizer-agent/
├── agents/                          # Enterprise agent framework
│   ├── api.py                       # FastAPI REST server
│   ├── base.py                      # Security, PHI guard, audit trail
│   ├── llm_factory.py               # LLM provider factory
│   ├── learning.py                  # Bayesian calibration engine
│   ├── metrics.py                   # Prometheus metrics collector
│   ├── models.py                    # Pydantic data models
│   ├── streamer.py                  # WebSocket telemetry
│   ├── supervisor.py                # Master orchestrator
│   └── workers.py                   # Specialized domain workers
├── he_slide_harmonizer_agent/       # Clinical agent package
│   ├── agents.py                    # Coordinator & sub-agents
│   ├── cli.py                       # Clinical CLI
│   ├── consistency.py               # Cross-scanner consistency scoring
│   ├── engine.py                    # Clinical domain engine
│   ├── models.py                    # Clinical data models
│   ├── reference.py                 # Stain reference target agent
│   ├── server.py                    # Clinical FastAPI server
│   └── validation.py                # Stain vector validation
├── tests/                           # Test suites
├── cli.py                           # Main CLI entry point
├── enrichment.py                    # Enrichment feature suite
├── simulator.py                     # Batch simulation
├── slide_harmonizer.py              # Core harmonization module
├── pyproject.toml                   # Project configuration
├── Dockerfile                       # Container definition
└── README.md                        # This file
```
