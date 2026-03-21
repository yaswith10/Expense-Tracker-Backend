from __future__ import annotations

import json
import os
from dataclasses import dataclass
from decimal import Decimal

import httpx

from ..exceptions import (
    AIConfigurationError,
    LLMProviderError,
    LLMRateLimitError,
    LLMResponseParseError,
)
from ..interface import ExpenseData, InsightResult
from ..prompts.templates import (
    EXPENSE_INSIGHTS_SYSTEM_PROMPT,
    EXPENSE_INSIGHTS_USER_PROMPT_TEMPLATE,
)

_GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
_MODEL = "llama3-8b-8192"
_REQUEST_TIMEOUT_SECONDS = 30


class GroqEngine:
    """LLM engine implementation using the Groq API.

    Implements the engine contract expected by get_expense_insights.
    The public method is generate(). All other methods are internal.

    The engine is stateless beyond the api_key provided at construction.
    It is safe to instantiate per-request.
    """

    def __init__(self, api_key: str) -> None:
        if not api_key:
            raise AIConfigurationError(
                "GroqEngine requires a non-empty api_key."
            )
        self._api_key = api_key

    def generate(self, expenses: list[ExpenseData]) -> InsightResult:
        """Generate spending insights for the provided expense list.

        Raises:
            LLMRateLimitError: if the Groq API responds with HTTP 429.
            LLMProviderError: if the Groq API responds with any other error
                or is unreachable.
            LLMResponseParseError: if the response content cannot be parsed
                into the expected JSON structure.
        """
        if not expenses:
            return InsightResult(insights=[], source="groq")

        user_prompt = self._build_user_prompt(expenses)
        raw_content = self._call_api(user_prompt)
        return self._parse_response(raw_content)

    def _build_user_prompt(self, expenses: list[ExpenseData]) -> str:
        expense_lines = "\n".join(
            f"- {e.date} | {e.category} | {e.title} | {e.amount}"
            for e in expenses
        )
        total = sum(e.amount for e in expenses)
        return EXPENSE_INSIGHTS_USER_PROMPT_TEMPLATE.format(
            expense_lines=expense_lines,
            count=len(expenses),
            total=total,
        )

    def _call_api(self, user_prompt: str) -> str:
        payload = {
            "model": _MODEL,
            "messages": [
                {"role": "system", "content": EXPENSE_INSIGHTS_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.3,
            "max_tokens": 512,
        }
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = httpx.post(
                _GROQ_API_URL,
                json=payload,
                headers=headers,
                timeout=_REQUEST_TIMEOUT_SECONDS,
            )
        except httpx.TimeoutException as exc:
            raise LLMProviderError(
                "Groq API request timed out after "
                f"{_REQUEST_TIMEOUT_SECONDS} seconds."
            ) from exc
        except httpx.RequestError as exc:
            raise LLMProviderError(
                f"Groq API request failed: {exc}"
            ) from exc

        if response.status_code == 429:
            raise LLMRateLimitError(
                "Groq API rate limit reached. Retry after a short delay."
            )
        if response.status_code != 200:
            raise LLMProviderError(
                f"Groq API returned HTTP {response.status_code}: {response.text}"
            )

        try:
            return response.json()["choices"][0]["message"]["content"]
        except (KeyError, IndexError, ValueError) as exc:
            raise LLMResponseParseError(
                f"Unexpected Groq API response structure: {response.text}"
            ) from exc

    def _parse_response(self, raw_content: str) -> InsightResult:
        try:
            data = json.loads(raw_content)
            insights: list[str] = data["insights"]
            if not isinstance(insights, list):
                raise ValueError("insights field is not a list")
            if not all(isinstance(item, str) for item in insights):
                raise ValueError("insights list contains non-string items")
        except (json.JSONDecodeError, KeyError, ValueError) as exc:
            raise LLMResponseParseError(
                f"Failed to parse LLM response into InsightResult: {exc!r}. "
                f"Raw content: {raw_content!r}"
            ) from exc

        return InsightResult(insights=insights, source="groq")
