from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional, Sequence

from django.conf import settings
from django.contrib.auth.models import User

from pydantic_ai import Agent, RunContext
from pydantic_ai.models import ModelSettings


class CampusAiError(Exception):
    """Raised when the campus AI assistant cannot be prepared."""


@dataclass
class ChatMessage:
    role: str
    content: str


@dataclass
class TourAgentDeps:
    user: User
    locations_map: dict
    created_tour_id: Optional[int] = None


_agent_instance: Optional[Agent[TourAgentDeps, str]] = None


def _build_agent() -> Agent[TourAgentDeps, str]:
    """Instantiate the Pydantic AI agent configured for OpenRouter with tour creation tool."""
    global _agent_instance
    if _agent_instance is not None:
        return _agent_instance

    api_key = settings.OPENROUTER_API_KEY
    if not api_key:
        raise CampusAiError('Missing OpenRouter API key.')

    from pydantic_ai.models.openai import OpenAIChatModel
    from pydantic_ai.providers.openrouter import OpenRouterProvider

    model = OpenAIChatModel(
        'openai/gpt-oss-120b:exacto',
        provider=OpenRouterProvider(api_key=api_key),
    )

    system_prompt = (
        "You are an enthusiastic Georgia Tech campus tour guide. "
        "Answer questions about buildings, landmarks, traditions, and campus logistics. "
        "Whenever possible, reference the provided landmark list to give accurate details. "
        "Keep responses concise but friendly, and invite follow-up questions. "
        "Speak in plain conversational text only—do not use bullet points, numbered lists, or special formatting.\n\n"
        "TOUR CREATION:\n"
        "You have a create_tour tool to save custom tours for users. When a user asks for a tour:\n"
        "1. First, describe the tour you would create (name, stops, why you chose them)\n"
        "2. Ask if they would like you to save it\n"
        "3. Only call create_tour after they confirm\n"
        "Use location IDs from the landmark list when calling the tool."
    )

    model_settings = ModelSettings(
        extra_body={
            'provider': {
                'sort': 'throughput',
            },
        },
    )

    agent: Agent[TourAgentDeps, str] = Agent(
        model=model,
        instructions=system_prompt,
        model_settings=model_settings,
        deps_type=TourAgentDeps,
    )

    @agent.tool
    def create_tour(
        ctx: RunContext[TourAgentDeps],
        tour_name: str,
        tour_description: str,
        location_ids: list[int],
    ) -> str:
        """
        Create a new campus tour for the user with specified locations.
        Only call this after the user confirms they want the tour created.

        Args:
            tour_name: Descriptive name for the tour
            tour_description: Brief description of the tour theme
            location_ids: Ordered list of location IDs to visit
        """
        from .models import Tour, TourStop
        from .route_utils import calculate_route_segments, RouteCalculationError

        user = ctx.deps.user
        locations_map = ctx.deps.locations_map

        valid_locations = []
        for loc_id in location_ids:
            if loc_id in locations_map:
                valid_locations.append(locations_map[loc_id])

        if not valid_locations:
            return "Error: None of the specified locations were found."

        tour = Tour.objects.create(
            user=user,
            name=tour_name,
            description=tour_description,
        )

        for order, location in enumerate(valid_locations, start=1):
            TourStop.objects.create(tour=tour, location=location, order=order)

        if len(valid_locations) >= 2:
            stops_data = [
                {
                    'id': loc.id,
                    'name': loc.name,
                    'latitude': float(loc.latitude),
                    'longitude': float(loc.longitude),
                }
                for loc in valid_locations
            ]
            try:
                route_segments = calculate_route_segments(stops_data)
                tour.route_data = {'segments': route_segments} if route_segments else None
                tour.save()
            except (RouteCalculationError, Exception):
                pass

        ctx.deps.created_tour_id = tour.id

        location_names = [loc.name for loc in valid_locations]
        return f"Created tour '{tour_name}' with {len(valid_locations)} stops: {', '.join(location_names)}. The tour is now saved to your account."

    _agent_instance = agent
    return agent


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
                f"- ID: {location.id}\n"
                f"  Name: {location.name}\n"
                f"  Category: {location.category or 'General'}\n"
                f"  Coordinates: ({location.latitude}, {location.longitude})\n"
                f"  Address: {location.address or 'N/A'}\n"
                f"  Summary: {location.description.strip()}\n"
                f"  Historical Info: {location.historical_info or ''}"
            )
        )
    return "\n".join(rows)


@dataclass
class ChatResult:
    reply: str
    created_tour_id: Optional[int] = None


def run_landmark_chat(
    question: str,
    *,
    history: Sequence[ChatMessage],
    landmark_context: str,
    deps: Optional[TourAgentDeps] = None,
) -> ChatResult:
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

    result = agent.run_sync(prompt, deps=deps)

    created_tour_id = deps.created_tour_id if deps else None
    return ChatResult(reply=result.output, created_tour_id=created_tour_id)
