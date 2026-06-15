from __future__ import annotations

import os
from typing import Any

try:
    from langfuse import get_client, observe
except Exception:  # pragma: no cover
    def observe(*args: Any, **kwargs: Any):
        def decorator(func):
            return func
        return decorator

    def get_client(*args: Any, **kwargs: Any) -> Any:
        return None


class _LangfuseContext:
    def update_current_trace(self, **kwargs: Any) -> None:
        client = get_client()
        if client:
            client.update_current_trace(**kwargs)

    def update_current_observation(self, **kwargs: Any) -> None:
        client = get_client()
        if not client:
            return None

        metadata = kwargs.get("metadata")
        if metadata:
            client.update_current_span(metadata=metadata)

        usage_details = kwargs.get("usage_details")
        if usage_details:
            client.update_current_generation(usage_details=usage_details)


langfuse_context = _LangfuseContext()


def flush_traces() -> bool:
    client = get_client()
    if not client:
        return False
    client.flush()
    return True


if False:  # pragma: no cover
    class _DummyContext:
        def update_current_trace(self, **kwargs: Any) -> None:
            return None

        def update_current_observation(self, **kwargs: Any) -> None:
            return None


def tracing_enabled() -> bool:
    return bool(os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"))
