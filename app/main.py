from __future__ import annotations

import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from structlog.contextvars import bind_contextvars

from .agent import LabAgent
from .incidents import disable, enable, status
from .logging_config import configure_logging, get_logger
from .metrics import record_error, snapshot
from .middleware import CorrelationIdMiddleware
from .pii import hash_user_id, summarize_text
from .schemas import ChatRequest, ChatResponse
from .tracing import flush_traces, tracing_enabled

configure_logging()
log = get_logger()
app = FastAPI(title="Day 13 Observability Lab")
app.add_middleware(CorrelationIdMiddleware)
agent = LabAgent()


@app.on_event("startup")
async def startup() -> None:
    log.info(
        "app_started",
        service=os.getenv("APP_NAME", "day13-observability-lab"),
        env=os.getenv("APP_ENV", "dev"),
        payload={"tracing_enabled": tracing_enabled()},
    )


@app.get("/health")
async def health() -> dict:
    return {"ok": True, "tracing_enabled": tracing_enabled(), "incidents": status()}


@app.get("/metrics")
async def metrics() -> dict:
    return snapshot()


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard() -> str:
    return """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Observability Dashboard</title>
  <style>
    :root { color-scheme: light; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
    body { margin: 0; background: #f6f7f9; color: #1f2933; }
    header { padding: 18px 24px; background: #ffffff; border-bottom: 1px solid #d9dee7; display: flex; justify-content: space-between; gap: 16px; align-items: center; }
    h1 { font-size: 20px; margin: 0; font-weight: 650; }
    main { padding: 20px 24px; }
    .grid { display: grid; grid-template-columns: repeat(3, minmax(220px, 1fr)); gap: 14px; }
    .panel { background: #ffffff; border: 1px solid #d9dee7; border-radius: 8px; padding: 16px; min-height: 138px; }
    .panel h2 { font-size: 14px; margin: 0 0 12px; color: #4b5563; font-weight: 650; }
    .value { font-size: 30px; line-height: 1.1; font-weight: 720; margin-bottom: 8px; }
    .sub { font-size: 13px; color: #64748b; line-height: 1.5; }
    .threshold { margin-top: 10px; padding-top: 10px; border-top: 1px solid #e5e9f0; font-size: 12px; color: #52606d; }
    .ok { color: #0f766e; }
    .warn { color: #b45309; }
    @media (max-width: 900px) { .grid { grid-template-columns: repeat(2, minmax(220px, 1fr)); } }
    @media (max-width: 620px) { header { align-items: flex-start; flex-direction: column; } main { padding: 14px; } .grid { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
  <header>
    <h1>Day 13 Observability Dashboard</h1>
    <div class="sub">Auto-refresh: 15s | Source: /metrics</div>
  </header>
  <main>
    <section class="grid" aria-label="Required observability panels">
      <article class="panel"><h2>Latency P50 / P95 / P99</h2><div class="value" id="latency">--</div><div class="sub" id="latency-sub"></div><div class="threshold">SLO: P95 &lt; 3000ms</div></article>
      <article class="panel"><h2>Traffic</h2><div class="value" id="traffic">--</div><div class="sub">requests since process start</div><div class="threshold">Watch for load shifts before debugging latency.</div></article>
      <article class="panel"><h2>Error Rate & Breakdown</h2><div class="value" id="errors">--</div><div class="sub" id="error-sub"></div><div class="threshold">SLO: error rate &lt; 2%</div></article>
      <article class="panel"><h2>Cost Over Time</h2><div class="value" id="cost">--</div><div class="sub" id="cost-sub"></div><div class="threshold">Budget: total &lt; $2.50/day</div></article>
      <article class="panel"><h2>Tokens In / Out</h2><div class="value" id="tokens">--</div><div class="sub">input / output total tokens</div><div class="threshold">Use output-token spikes to explain cost spikes.</div></article>
      <article class="panel"><h2>Quality Proxy</h2><div class="value" id="quality">--</div><div class="sub">heuristic answer quality average</div><div class="threshold">SLO: quality score &gt;= 0.75</div></article>
    </section>
  </main>
  <script>
    async function refresh() {
      const res = await fetch('/metrics');
      const m = await res.json();
      const errors = Object.values(m.error_breakdown || {}).reduce((a, b) => a + b, 0);
      const errorRate = m.traffic ? (errors / m.traffic) * 100 : 0;
      document.getElementById('latency').textContent = `${m.latency_p95}ms`;
      document.getElementById('latency-sub').textContent = `P50 ${m.latency_p50}ms | P95 ${m.latency_p95}ms | P99 ${m.latency_p99}ms`;
      document.getElementById('traffic').textContent = m.traffic;
      document.getElementById('errors').textContent = `${errorRate.toFixed(2)}%`;
      document.getElementById('error-sub').textContent = JSON.stringify(m.error_breakdown || {});
      document.getElementById('cost').textContent = `$${Number(m.total_cost_usd).toFixed(4)}`;
      document.getElementById('cost-sub').textContent = `avg $${Number(m.avg_cost_usd).toFixed(4)} per request`;
      document.getElementById('tokens').textContent = `${m.tokens_in_total} / ${m.tokens_out_total}`;
      document.getElementById('quality').textContent = Number(m.quality_avg).toFixed(2);
    }
    refresh();
    setInterval(refresh, 15000);
  </script>
</body>
</html>
"""


@app.post("/tracing/flush")
async def tracing_flush() -> dict:
    return {"flushed": flush_traces(), "tracing_enabled": tracing_enabled()}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: Request, body: ChatRequest) -> ChatResponse:
    bind_contextvars(
        user_id_hash=hash_user_id(body.user_id),
        session_id=body.session_id,
        feature=body.feature,
        model=agent.model,
        env=os.getenv("APP_ENV", "dev"),
    )
    
    log.info(
        "request_received",
        service="api",
        payload={"message_preview": summarize_text(body.message)},
    )
    try:
        result = agent.run(
            user_id=body.user_id,
            feature=body.feature,
            session_id=body.session_id,
            message=body.message,
        )
        log.info(
            "response_sent",
            service="api",
            latency_ms=result.latency_ms,
            tokens_in=result.tokens_in,
            tokens_out=result.tokens_out,
            cost_usd=result.cost_usd,
            payload={"answer_preview": summarize_text(result.answer)},
        )
        return ChatResponse(
            answer=result.answer,
            correlation_id=request.state.correlation_id,
            latency_ms=result.latency_ms,
            tokens_in=result.tokens_in,
            tokens_out=result.tokens_out,
            cost_usd=result.cost_usd,
            quality_score=result.quality_score,
        )
    except Exception as exc:  # pragma: no cover
        error_type = type(exc).__name__
        record_error(error_type)
        log.error(
            "request_failed",
            service="api",
            error_type=error_type,
            payload={"detail": str(exc), "message_preview": summarize_text(body.message)},
        )
        raise HTTPException(status_code=500, detail=error_type) from exc


@app.post("/incidents/{name}/enable")
async def enable_incident(name: str) -> JSONResponse:
    try:
        enable(name)
        log.warning("incident_enabled", service="control", payload={"name": name})
        return JSONResponse({"ok": True, "incidents": status()})
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/incidents/{name}/disable")
async def disable_incident(name: str) -> JSONResponse:
    try:
        disable(name)
        log.warning("incident_disabled", service="control", payload={"name": name})
        return JSONResponse({"ok": True, "incidents": status()})
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
