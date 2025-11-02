import json
from json import JSONDecodeError
from typing import List

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .ai import CampusAiError, ChatMessage, get_landmark_context, run_landmark_chat
from .models import Location


def campus_overview(request):
    locations = Location.objects.all()
    locations_payload = [
        {
            'name': location.name,
            'slug': location.slug,
            'description': location.description,
            'latitude': float(location.latitude),
            'longitude': float(location.longitude),
            'address': location.address,
            'category': location.category,
        }
        for location in locations
    ]
    context = {
        'locations': locations,
        'locations_payload': locations_payload,
        'google_maps_api_key': settings.GOOGLE_MAP_API_KEY,
        'map_center': {'lat': 33.7780, 'lng': -84.3980},
    }
    return render(request, 'campus/overview.html', context)


@require_GET
def location_list(request):
    locations = Location.objects.values(
        'name',
        'slug',
        'description',
        'latitude',
        'longitude',
        'address',
        'category',
    )
    data = [
        {
            **location,
            'latitude': float(location['latitude']),
            'longitude': float(location['longitude']),
        }
        for location in locations
    ]
    return JsonResponse({'locations': data})


@csrf_exempt
@require_POST
def chat_with_assistant(request):
    try:
        payload = json.loads(request.body)
    except JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON payload.'}, status=400)

    message = (payload.get('message') or '').strip()
    if not message:
        return JsonResponse({'error': 'Message is required.'}, status=400)

    raw_history = payload.get('history') or []
    chat_history: List[ChatMessage] = []
    for entry in raw_history[-8:]:
        role = entry.get('role')
        content = entry.get('content')
        if role in {'user', 'assistant'} and isinstance(content, str):
            chat_history.append(ChatMessage(role=role, content=content))

    locations = list(Location.objects.all())
    landmark_context = get_landmark_context(locations)

    try:
        reply = run_landmark_chat(
            message,
            history=chat_history,
            landmark_context=landmark_context,
        )
    except CampusAiError as exc:
        return JsonResponse({'error': str(exc)}, status=503)

    return JsonResponse({'reply': reply})
