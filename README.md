# Day 13 Observability Lab - Individual Submission

This repository contains a completed individual version of the Day 13 Observability Lab. The FastAPI agent is instrumented with structured JSON logs, correlation ID propagation, PII redaction, Langfuse-compatible tracing, in-memory metrics, SLO definitions, alert rules, dashboard specifications, and an individual lab report.

## Completed Scope

- Structured JSONL logs written to `data/logs.jsonl`
- Request-scoped `x-request-id` propagation through response headers and log context
- Context enrichment for `user_id_hash`, `session_id`, `feature`, `model`, and `env`
- PII scrubbing for email, Vietnamese phone numbers, CCCD, credit card, passport-like IDs, and address hints
- Langfuse trace hooks through `@observe()` and `langfuse_context`
- Metrics endpoint with traffic, latency percentiles, cost, token totals, errors, and quality proxy
- Browser dashboard at `/dashboard` with all six required panels
- Incident toggles for `rag_slow`, `tool_fail`, and `cost_spike`
- SLOs, alert rules, dashboard spec, runbook, and grading evidence document
- Tests for PII, metrics, and correlation ID propagation

## Environment

Use Python 3.11 for this lab. The pinned `pydantic-core==2.33.2` dependency is not compatible with Python 3.14 in this environment.

```bash
/Users/kenz_de/.local/bin/python3.11 -m venv .venv311
source .venv311/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Optional Langfuse tracing:

```bash
export LANGFUSE_PUBLIC_KEY=...
export LANGFUSE_SECRET_KEY=...
export LANGFUSE_HOST=https://cloud.langfuse.com
```

## Run

```bash
source .venv311/bin/activate
uvicorn app.main:app --reload
```

Health, metrics, and chat endpoints:

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/metrics
curl -X POST http://127.0.0.1:8000/chat \
  -H 'content-type: application/json' \
  -H 'x-request-id: req-manual01' \
  -d '{"user_id":"u01","session_id":"s01","feature":"qa","message":"What is your refund policy? My email is student@vinuni.edu.vn"}'
```

## Verification

Run tests:

```bash
.venv311/bin/python -m pytest -q
```

Current result:

```text
5 passed
```

Generate sample traffic:

```bash
.venv311/bin/python scripts/load_test.py --concurrency 5
```

Validate logs:

```bash
.venv311/bin/python scripts/validate_logs.py
```

Current validated result from generated sample traffic:

```text
Total log records analyzed: 70
Records with missing required fields: 0
Records with missing enrichment (context): 0
Unique correlation IDs found: 31
Potential PII leaks detected: 0
Estimated Score: 100/100
```

Langfuse verification after configuring `.env` keys:

```text
GET /api/public/traces?limit=20
status=200
count=10
```

Dashboard:

```text
http://127.0.0.1:8000/dashboard
```

## Incident Scenarios

Enable or disable scenarios while the server is running:

```bash
.venv311/bin/python scripts/inject_incident.py --scenario rag_slow
.venv311/bin/python scripts/inject_incident.py --scenario rag_slow --disable
.venv311/bin/python scripts/inject_incident.py --scenario tool_fail
.venv311/bin/python scripts/inject_incident.py --scenario cost_spike
```

Expected debugging flow:

1. Metrics show the symptom, such as P95 latency, error count, or cost increase.
2. Traces identify the affected span, such as retrieval or generation.
3. Logs explain the root cause using `correlation_id`, `error_type`, and sanitized payload context.

## Repo Map

```text
app/
  main.py                FastAPI app, request enrichment, dashboard, trace flush
  agent.py               instrumented agent pipeline
  logging_config.py      structlog JSONL pipeline and PII scrub processor
  middleware.py          correlation ID middleware
  pii.py                 redaction and user hashing helpers
  tracing.py             Langfuse observe/context fallback helpers
  schemas.py             request/response/log models
  metrics.py             in-memory metrics helpers
  incidents.py           incident toggles
  mock_llm.py            deterministic fake LLM
  mock_rag.py            deterministic retrieval
config/
  slo.yaml               SLO definitions
  alert_rules.yaml       alert definitions with runbook links
  logging_schema.json    expected log schema
docs/
  blueprint-template.md  completed individual report
  alerts.md              alert runbook
  dashboard-spec.md      6-panel dashboard spec
  grading-evidence.md    evidence checklist and local results
scripts/
  load_test.py           sample traffic generator
  inject_incident.py     incident toggle client
  validate_logs.py       log validation scorecard
tests/
  test_app_observability.py
  test_metrics.py
  test_pii.py
```
