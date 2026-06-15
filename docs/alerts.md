# Alert Rules and Runbooks

These alerts are symptom-based first. They page on user-visible impact, then use traces and logs to prove root cause.

## 1. High Latency P95

- Alert: `high_latency_p95`
- Severity: P2
- Trigger: `latency_p95_ms > 5000 for 30m`
- SLO affected: P95 latency < 3000ms
- Likely incident: `rag_slow`

First checks:

1. Open `/metrics` and confirm `latency_p95` is above baseline.
2. Open the slowest traces from the same time window.
3. Compare retrieval/RAG duration against generation duration.
4. Filter `data/logs.jsonl` by the trace `correlation_id`.
5. Check `/health` for active incident toggles.

Mitigation:

- Disable the injected incident: `.venv311/bin/python scripts/inject_incident.py --scenario rag_slow --disable`
- Add or lower retrieval timeout.
- Route to fallback retrieval if the vector store is slow.
- Reduce prompt size for very long inputs.

Prevention:

- Keep latency SLO line on the dashboard.
- Monitor P95/P99, not only average latency.
- Include trace metadata for feature, model, and document count.

## 2. High Error Rate

- Alert: `high_error_rate`
- Severity: P1
- Trigger: `error_rate_pct > 5 for 5m`
- SLO affected: error rate < 2%
- Likely incident: `tool_fail`

First checks:

1. Group logs by `error_type`.
2. Inspect failed traces with the same `correlation_id`.
3. Determine whether the failure is retrieval, LLM, schema validation, or infrastructure.
4. Confirm whether `/health` shows `tool_fail=true`.

Mitigation:

- Disable the failing tool scenario: `.venv311/bin/python scripts/inject_incident.py --scenario tool_fail --disable`
- Return a fallback answer if retrieval fails.
- Roll back the latest change if errors started after deployment.
- Add retries only where idempotent and bounded.

Prevention:

- Keep `error_type` in all failure logs.
- Separate dependency errors from application errors.
- Add a fallback path for retrieval outages.

## 3. Cost Budget Spike

- Alert: `cost_budget_spike`
- Severity: P2
- Trigger: `hourly_cost_usd > 2x_baseline for 15m`
- SLO affected: daily cost < $2.50
- Likely incident: `cost_spike`

First checks:

1. Compare `tokens_in_total` and `tokens_out_total` on the dashboard.
2. Split traces by `feature` and `model`.
3. Check whether output tokens increased while traffic stayed stable.
4. Confirm whether `/health` shows `cost_spike=true`.

Mitigation:

- Disable the incident: `.venv311/bin/python scripts/inject_incident.py --scenario cost_spike --disable`
- Cap output tokens for summary and QA.
- Shorten prompt context.
- Route simple requests to a cheaper model.

Prevention:

- Add token and cost panels beside latency.
- Monitor average cost and total cost.
- Tag traces by feature and model for attribution.
