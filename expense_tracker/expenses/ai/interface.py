from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from .exceptions import AIConfigurationError

if TYPE_CHECKING:
    from .engines.groq_engine import GroqEngine


@dataclass(frozen=True)
class ExpenseData:
    """Immutable representation of a single expense passed to the AI module.

    The view layer is responsible for converting ORM Expense instances to
    ExpenseData before calling get_expense_insights. This keeps the AI module
    fully decoupled from Django's ORM.
    """

    title: str
    amount: Decimal
    category: str
    date: date


@dataclass(frozen=True)
class InsightResult:
    """Typed result returned by get_expense_insights.

    insights: ordered list of natural language recommendation strings.
    source: identifier of the engine that produced this result, for logging.
    """

    insights: list[str]
    source: str


def get_expense_insights(expenses: list[ExpenseData]) -> InsightResult:
    """Return AI-generated spending insights for the provided expense list.

    This is the sole public entry point for the AI module. The caller supplies
    a list of ExpenseData instances and receives an InsightResult. The engine
    implementation is resolved here and is invisible to the caller.

    Raises:
        AIConfigurationError: if LLM_API_KEY is not set in the environment.
        LLMProviderError: if the LLM provider is unreachable or returns an error.
        LLMRateLimitError: if the provider responds with HTTP 429.
        LLMResponseParseError: if the provider response cannot be parsed.
    """
    api_key = os.environ.get("LLM_API_KEY")
    if not api_key:
        raise AIConfigurationError(
            "LLM_API_KEY is not set. Add it to your environment before using the AI module."
        )

    from .engines.groq_engine import GroqEngine

    engine: GroqEngine = GroqEngine(api_key=api_key)
    return engine.generate(expenses)
