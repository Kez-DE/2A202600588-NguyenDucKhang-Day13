# Evidence Collection Sheet

## Local Verification Completed

| Evidence | Status | Location / Command |
|---|---|---|
| Unit tests | Passed | `.venv311/bin/python -m pytest -q` |
| Log validator | 100/100 | `.venv311/bin/python scripts/validate_logs.py` |
| Langfuse traces | 10 confirmed | Langfuse API `GET /api/public/traces?limit=20` returned `count=10` |
| 6-panel dashboard | Implemented | `http://127.0.0.1:8000/dashboard` |
| JSON logs with correlation ID | Collected | `data/logs.jsonl`, examples `req-demo0001` to `req-demo0010` |
| PII redaction | Verified | `data/logs.jsonl` contains `[REDACTED_EMAIL]`, `[REDACTED_PHONE_VN]`, `[REDACTED_CREDIT_CARD]` |
| Dashboard specification | Completed | `docs/dashboard-spec.md` |
| Alert rules | Completed | `config/alert_rules.yaml` and `docs/alerts.md` |
| SLO table | Completed | `config/slo.yaml` and `docs/blueprint-template.md` |
| Langfuse trace list screenshot | Collected | `docs/screenshots/langfuse-trace-list.png` |
| Langfuse waterfall screenshot | Collected | `docs/screenshots/langfuse-trace-waterfall.png` |
| Dashboard screenshot | Collected | `docs/screenshots/dashboard-6-panels.png` |

## Validator Output

```text
Total log records analyzed: 70
Records with missing required fields: 0
Records with missing enrichment (context): 0
Unique correlation IDs found: 31
Potential PII leaks detected: 0
Estimated Score: 100/100
```

## Screenshots Collected

- `docs/screenshots/langfuse-trace-list.png`
- `docs/screenshots/langfuse-trace-waterfall.png`
- `docs/screenshots/dashboard-6-panels.png`

Additional evidence available in repo:

- `scripts/validate_logs.py` score 100/100
- `data/logs.jsonl` lines with `correlation_id`
- `data/logs.jsonl` lines showing PII redaction
- Alert rules in `config/alert_rules.yaml`

## Demo Script

1. Start the app with `uvicorn app.main:app --reload`.
2. Generate sample traffic with `.venv311/bin/python scripts/load_test.py --concurrency 5`.
3. Open `/metrics` and show latency, traffic, cost, token, error, and quality values.
4. Run `.venv311/bin/python scripts/validate_logs.py`.
5. Enable `rag_slow`, generate traffic, and show P95 latency increase.
6. Disable `rag_slow` and show recovery.
7. Explain how `correlation_id` joins metrics, traces, and logs.
