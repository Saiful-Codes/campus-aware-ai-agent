# Testing Summary

Campus-Aware Intelligent AI Agent — La Trobe University Capstone

This document summarises the project's quality assurance: the automated test suite, the manual QA framework, and the security/CI workflows.

---

## 1. Overview

- **185 automated test functions** across **17 test files** in `backend/tests/`
- Framework: **pytest** (`python -m pytest`)
- A structured **manual QA suite** (`backend/tests/manual_chat_test_suite.md`)
- **CI/CD security scanning**: CodeQL, Semgrep (SAST), and OWASP ZAP (DAST)

Coverage spans intent routing, Flux query safety, natural-language parsing, retry/resilience behavior, configuration validation, sensor handling, RAG resilience, and hallucination guardrails.

---

## 2. Running the Tests

```powershell
cd backend
.venv\Scripts\Activate.ps1
$env:SENSOR_SYNC_ENABLED = "false"   # prevents the sensor ingestion loop from running during tests
python -m pytest
```

Run a single test:

```powershell
python -m pytest tests/test_routing_orchestration.py::test_name
```

> Always activate `.venv` first and set `SENSOR_SYNC_ENABLED=false`, otherwise the ingestion loop adds log noise and unnecessary network calls during the run.

---

## 3. Coverage by Category

| Category | Tests | Files |
|---|---:|---|
| Intent routing | 33 | `test_routing_orchestration.py` |
| Text-to-Flux & query safety | 87 | `test_text_to_flux_parsing.py` (70), `test_flux_query_safety.py` (17) |
| LLM, guardrails & retries | 26 | `test_llm_service_callers.py` (11), `test_gemini_retry_helper.py` (6), `test_url_ranking.py` (5), `test_llm_guardrails.py` (4) |
| Sensors & InfluxDB | 16 | `test_sensor_scheduler.py` (13), `test_influx_sensor_point.py` (3) |
| RAG resilience | 8 | `test_rag_pipeline_retry.py` (3), `test_rag_chat_error_shape.py` (3), `test_rag_pipeline_concurrency.py` (2) |
| API / request handling | 7 | `test_chat_empty_query.py` (3), `test_chat_max_length.py` (3), `test_health.py` (1) |
| Configuration | 8 | `test_config_validation.py` (7), `test_config_defaults.py` (1) |
| **Total** | **185** | **17 files** |

---

## 4. What Each Suite Proves

| Test file | What it verifies |
|---|---|
| `test_routing_orchestration.py` | Intent classification correctness across all intents; sensor-intent priority |
| `test_flux_query_safety.py` | Flux injection prevention and safety constraints (measurement filter, bounded range, no `range(start: 0)`, limits) |
| `test_text_to_flux_parsing.py` | Time-range parsing, record parsing, field detection, formatting |
| `test_llm_service_callers.py` | LLM service caller contracts |
| `test_llm_guardrails.py` | Hallucination prevention (no invented fees/URLs/schedules) |
| `test_gemini_retry_helper.py` | Retry behavior for Gemini API calls |
| `test_url_ranking.py` | Trusted-source URL ranking for exact-info responses |
| `test_sensor_scheduler.py` | Ingestion loop enable/disable, interval, and failure handling |
| `test_influx_sensor_point.py` | InfluxDB sensor data-point validation |
| `test_rag_pipeline_retry.py` | RAG graceful fallback on Gemini errors |
| `test_rag_pipeline_concurrency.py` | RAG concurrency safety |
| `test_rag_chat_error_shape.py` | `/rag/chat` error response structure |
| `test_chat_empty_query.py` | Empty-query short-circuit behavior |
| `test_chat_max_length.py` | Query length validation (2000-char cap) |
| `test_config_validation.py` | Required env-var validation logic |
| `test_config_defaults.py` | Default config values |
| `test_health.py` | `/health` endpoint |

---

## 5. Manual QA Framework

`backend/tests/manual_chat_test_suite.md` is a structured manual testing document covering scenarios that are best validated by a human against the live system:

- Live sensor queries
- Historical sensor / aggregation queries
- Routing validation across intents
- Hallucination prevention
- RAG retrieval accuracy
- Edge cases

It complements the automated suite by exercising end-to-end conversational behavior and answer quality.

---

## 6. Security & CI Workflows

Located in `.github/workflows/`:

| Workflow | Type | Purpose |
|---|---|---|
| `codeql.yml` | SAST | Static analysis for code vulnerabilities |
| `semgrep.yml` | SAST | Pattern-based static security scanning |
| `zap.yml` | DAST | OWASP ZAP dynamic application security testing |

---

## 7. Known Issues

At the time of writing, the suite reports **179 passing and 6 failing** tests. The failures are concentrated in the sensor-scheduler tests and are **test-harness issues, not runtime defects** — the affected tests attempt to mock-patch a symbol (`sync_latest_sensor_data_to_influx`) at module scope, but the production code imports it *locally inside* the ingestion loop function, so the patch target does not exist at module level. The underlying scheduler and chat behavior work correctly at runtime. This is a known issue to be resolved by aligning the patch targets with the actual import location.
