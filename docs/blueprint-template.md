# Day 13 Observability Lab Report

## 1. Submission Metadata

- [REPO_URL]: https://github.com/Kez-DE/2A202600588-NguyenDucKhang-Day13
- [MEMBERS]:
  - Nguyễn Đức Khang - 2A202600588 | Role: Full-stack observability implementation, validation, and report

---

## 2. Performance Summary

- [VALIDATE_LOGS_FINAL_SCORE]: 100/100
- [TOTAL_TRACES_COUNT]: 10 traces confirmed through Langfuse API after configuring `LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY`
- [PII_LEAKS_FOUND]: 0

Validation command:

```bash
.venv311/bin/python scripts/validate_logs.py
```

Observed result:

```text
Total log records analyzed: 70
Records with missing required fields: 0
Records with missing enrichment (context): 0
Unique correlation IDs found: 31
Potential PII leaks detected: 0
Estimated Score: 100/100
```

---

## 3. Technical Evidence

### 3.1 Logging & Tracing

- [EVIDENCE_CORRELATION_ID_SCREENSHOT]: `docs/screenshots/langfuse-trace-list.png`
- [EVIDENCE_PII_REDACTION_SCREENSHOT]: `data/logs.jsonl` entries show `[REDACTED_EMAIL]`, `[REDACTED_PHONE_VN]`, and `[REDACTED_CREDIT_CARD]`; validator result reports `Potential PII leaks detected: 0`
- [EVIDENCE_TRACE_WATERFALL_SCREENSHOT]: `docs/screenshots/langfuse-trace-waterfall.png`
- [TRACE_WATERFALL_EXPLANATION]: The main `LabAgent.run` observation covers retrieval, prompt construction, fake LLM generation, token usage, quality scoring, and metric recording. Metadata includes hashed user ID, session ID, feature tag, model tag, document count, and sanitized query preview.

Implemented fields in each API log:

| Field | Purpose |
|---|---|
| `correlation_id` | Joins request, response, metrics, and traces |
| `user_id_hash` | Enables per-user debugging without raw user ID exposure |
| `session_id` | Groups turns in one conversation |
| `feature` | Splits QA vs summary workflows |
| `model` | Supports latency/cost comparison by model |
| `env` | Separates dev/staging/prod logs |

### 3.2 Dashboard & SLOs

- [DASHBOARD_6_PANELS_SCREENSHOT]: `docs/screenshots/dashboard-6-panels.png`

- [SLO_TABLE]:

| SLI | Target | Window | Current Value |
|---|---:|---|---:|
| Latency P95 | < 3000ms | 28d | ~155ms from local sample |
| Error Rate | < 2% | 28d | 0% from local sample |
| Cost Budget | < $2.50/day | 1d | <$0.03 sample total |
| Quality Score Avg | >= 0.75 | 28d | exposed by `/metrics` |

### 3.3 Alerts & Runbook

- [ALERT_RULES_SCREENSHOT]: Alert rules are defined in `config/alert_rules.yaml`
- [SAMPLE_RUNBOOK_LINK]: `docs/alerts.md#1-high-latency-p95`

Configured alerts:

| Alert | Severity | Trigger | Runbook |
|---|---|---|---|
| `high_latency_p95` | P2 | `latency_p95_ms > 5000 for 30m` | `docs/alerts.md#1-high-latency-p95` |
| `high_error_rate` | P1 | `error_rate_pct > 5 for 5m` | `docs/alerts.md#2-high-error-rate` |
| `cost_budget_spike` | P2 | `hourly_cost_usd > 2x_baseline for 15m` | `docs/alerts.md#3-cost-budget-spike` |

---

## 4. Incident Response

- [SCENARIO_NAME]: `rag_slow`
- [SYMPTOMS_OBSERVED]: `/metrics` shows P95 latency above the normal local baseline of about 150-160ms. Requests take roughly 2.6s because retrieval intentionally sleeps for 2.5s.
- [ROOT_CAUSE_PROVED_BY]: Trace waterfall would show the slow retrieval step inside `LabAgent.run`; logs can be filtered by the same `correlation_id` to confirm the request feature and sanitized query preview.
- [FIX_ACTION]: Disable the incident toggle using `.venv311/bin/python scripts/inject_incident.py --scenario rag_slow --disable`.
- [PREVENTIVE_MEASURE]: Add a latency alert, keep retrieval timeout/fallback behavior, and monitor P95 latency with a clear SLO threshold.

Additional scenarios:

| Scenario | Symptom | Root Cause Signal | Mitigation |
|---|---|---|---|
| `tool_fail` | 500 responses and error count increase | `error_type=RuntimeError`, message `Vector store timeout` | Disable failing tool or route to fallback retrieval |
| `cost_spike` | Token output and cost increase | `/metrics` shows higher `tokens_out_total` and `total_cost_usd` | Cap output tokens, shorten prompt, route easy requests to cheaper model |

---

## 5. Individual Contributions & Evidence

### Nguyễn Đức Khang - 2A202600588

- [TASKS_COMPLETED]: Implemented correlation ID middleware, structlog context enrichment, recursive PII scrubbing, deterministic answer generation, PII/correlation tests, SLOs, alerts, dashboard spec, incident runbook, validation evidence, and individual README/report.
- [EVIDENCE_LINK]: Local working tree in `2A202600588-NguyenDucKhang-Day13`; main implementation files are `app/middleware.py`, `app/logging_config.py`, `app/main.py`, `app/pii.py`, `app/mock_llm.py`, and `tests/test_app_observability.py`.

Technical details I can explain in demo:

- Why `clear_contextvars()` is called before and after each request to prevent context leakage.
- How incoming `x-request-id` is preserved and missing IDs are generated as `req-<8-char-hex>`.
- Why `user_id_hash` is logged instead of raw `user_id`.
- How PII regex order prevents 12-digit CCCD values from being partially redacted as phone numbers.
- How P95 latency is calculated from recorded request latencies and exposed through `/metrics`.

---

## 6. Bonus Items

- [BONUS_COST_OPTIMIZATION]: Cost metrics are captured as `avg_cost_usd`, `total_cost_usd`, `tokens_in_total`, and `tokens_out_total`, making before/after comparisons possible for prompt size and output-token controls.
- [BONUS_AUDIT_LOGS]: `AUDIT_LOG_PATH` is reserved in `.env.example`; not implemented as a separate writer in this submission.
- [BONUS_CUSTOM_METRIC]: `quality_avg` is exposed as a quality proxy derived from retrieved context, answer length, answer relevance, and redaction penalties.
