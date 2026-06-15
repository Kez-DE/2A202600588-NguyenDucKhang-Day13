from __future__ import annotations

import random
import re
import time
from dataclasses import dataclass

from .incidents import STATE


@dataclass
class FakeUsage:
    input_tokens: int
    output_tokens: int


@dataclass
class FakeResponse:
    text: str
    usage: FakeUsage
    model: str


class FakeLLM:
    def __init__(self, model: str = "claude-sonnet-4-5") -> None:
        self.model = model

    def generate(self, prompt: str) -> FakeResponse:
        time.sleep(0.15)
        input_tokens = max(20, len(prompt) // 4)
        output_tokens = random.randint(80, 180)
        if STATE["cost_spike"]:
            output_tokens *= 4
        answer = self._answer_from_prompt(prompt)
        return FakeResponse(text=answer, usage=FakeUsage(input_tokens, output_tokens), model=self.model)

    def _answer_from_prompt(self, prompt: str) -> str:
        docs_match = re.search(r"Docs=(.*)\nQuestion=", prompt, flags=re.DOTALL)
        question_match = re.search(r"Question=(.*)$", prompt, flags=re.DOTALL)
        docs = docs_match.group(1).lower() if docs_match else ""
        question = question_match.group(1).lower() if question_match else ""

        if "refund" in docs or "refund" in question:
            return "Refunds are available within 7 days when the user provides proof of purchase."
        if "metrics" in docs or "traces" in docs or "logs" in docs:
            return (
                "Metrics show that a problem exists, traces localize the slow or failing step, "
                "and logs explain the root cause with correlation IDs."
            )
        if "pii" in docs or "sensitive" in question or "credit card" in question:
            return "PII and sensitive data such as email, phone, CCCD, passport, and credit card values should not appear in app logs."
        return "Use the observability workflow: check SLO metrics, inspect traces for the affected span, then read sanitized logs by correlation ID."
