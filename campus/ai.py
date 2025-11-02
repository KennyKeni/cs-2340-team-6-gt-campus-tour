from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from django.conf import settings

from pydantic_ai import Agent


class CampusAiError(Exception):
    """Raised when the campus AI assistant cannot be prepared."""


@dataclass
class ChatMessage:
    role: str
    content: str


def _build_agent() -> Agent[str]:
    """Instantiate the Pydantic AI agent configured for OpenRouter."""
    api_key = settings.OPENROUTER_API_KEY
    if not api_key:
        raise CampusAiError('Missing OpenRouter API key.')

    # Lazy import to avoid unnecessary provider initialization during migrations/tests.
    from pydantic_ai.models.openai import OpenAIChatModel
    from pydantic_ai.providers.openrouter import OpenRouterProvider

    model = OpenAIChatModel(
        'openai/gpt-oss-120b',
        provider=OpenRouterProvider(api_key=api_key),
    )

    system_prompt = (
        "You are an enthusiastic Georgia Tech campus tour guide. "
        "Answer questions about buildings, landmarks, traditions, and campus logistics. "
        "Whenever possible, reference the provided landmark list to give accurate details. "
        "Keep responses concise but friendly, and invite follow-up questions."
    )

    return Agent(model=model, instructions=system_prompt)


def _format_history(history: Sequence[ChatMessage]) -> str:
    lines: list[str] = []
    for message in history:
        speaker = 'Visitor' if message.role == 'user' else 'Guide'
        lines.append(f"{speaker}: {message.content.strip()}")
    return "\n".join(lines)


def get_landmark_context(locations: Iterable) -> str:
    rows = []
    for location in locations:
        rows.append(
            (
                f"- Name: {location.name}\n"
                f"  Category: {location.category or 'General'}\n"
                f"  Coordinates: ({location.latitude}, {location.longitude})\n"
                f"  Address: {location.address or 'N/A'}\n"
                f"  Summary: {location.description.strip()}"
            )
        )
    return "\n".join(rows)


def run_landmark_chat(question: str, *, history: Sequence[ChatMessage], landmark_context: str) -> str:
    agent = _build_agent()
    history_text = _format_history(history)

    prompt_parts = [
        "Landmark reference list:\n",
        landmark_context,
        "\n---\n",
    ]
    if history_text:
        prompt_parts.append("Conversation so far:\n")
        prompt_parts.append(history_text)
        prompt_parts.append("\n---\n")
    prompt_parts.append("Visitor question:\n")
    prompt_parts.append(question.strip())

    prompt = "".join(prompt_parts)

    result = agent.run_sync(prompt)
    return result.output
