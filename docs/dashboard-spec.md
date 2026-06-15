# Dashboard Spec

The dashboard is implemented at `http://127.0.0.1:8000/dashboard` as a single Layer-2 operational view for the FastAPI agent. It reads live data from `/metrics`; the same panel definitions can also be recreated in a hosted dashboard tool.

## Global Settings

- Time range: last 1 hour by default
- Refresh: 15-30 seconds
- Environment filter: `env`
- Feature filter: `feature`
- Model filter: `model`
- Drilldown key: `correlation_id`

## Required 6 Panels

| Panel | Metric | Unit | Threshold / SLO Line | Purpose |
|---|---|---|---|---|
| 1. Latency percentiles | `latency_p50`, `latency_p95`, `latency_p99` | ms | P95 < 3000ms | Detect slow user experience and tail latency |
| 2. Traffic | `traffic` | requests | Baseline band from normal traffic | Show load and request volume |
| 3. Error breakdown | `error_breakdown` | errors by type | Error rate < 2% | Identify failing dependency or code path |
| 4. Cost | `avg_cost_usd`, `total_cost_usd` | USD | Daily total < $2.50 | Detect cost spikes from long outputs |
| 5. Tokens | `tokens_in_total`, `tokens_out_total` | tokens | Output token anomaly line | Explain cost and latency changes |
| 6. Quality proxy | `quality_avg` | score 0-1 | >= 0.75 | Watch for answer degradation |

## Drilldown Workflow

1. Start with a red panel, such as P95 latency or cost.
2. Filter by `feature` and `model` to isolate the affected slice.
3. Pick a `correlation_id` from logs or trace list.
4. Open the trace waterfall to locate the slow/failing step.
5. Read sanitized JSON logs for payload preview, `error_type`, token usage, and cost.

## Acceptance Checklist

- All six panels are visible on the main dashboard.
- Every panel has units.
- Latency, error, cost, and quality panels include threshold lines.
- Logs and traces can be joined by `correlation_id`.
- PII is redacted before dashboard ingestion.
