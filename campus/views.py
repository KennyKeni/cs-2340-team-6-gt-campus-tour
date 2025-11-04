import json
from json import JSONDecodeError
from typing import List

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .ai import CampusAiError, ChatMessage, get_landmark_context, run_landmark_chat
from .models import Bookmark, Location


def campus_overview(request):
    # Get all locations and annotate with bookmark status for authenticated users
    locations = Location.objects.all()
    
    # Get user's bookmarked location slugs if authenticated
    bookmarked_slugs = set()
    if request.user.is_authenticated:
        bookmarked_slugs = set(
            Bookmark.objects.filter(user=request.user)
            .values_list('location__slug', flat=True)
        )
    
    # Sort locations: bookmarked first, then alphabetically
    locations_list = list(locations)
    if request.user.is_authenticated:
        locations_list.sort(key=lambda loc: (loc.slug not in bookmarked_slugs, loc.name))
    else:
        locations_list.sort(key=lambda loc: loc.name)
    
    locations_payload = [
        {
            'name': location.name,
            'slug': location.slug,
            'description': location.description,
            'latitude': float(location.latitude),
            'longitude': float(location.longitude),
            'address': location.address,
            'category': location.category,
            'historical_info': location.historical_info,
            'photo_url': location.photo.url if location.photo else None,
        }
        for location in locations_list
    ]
    
    context = {
        'locations': locations_list,
        'locations_payload': locations_payload,
        'bookmarked_slugs': bookmarked_slugs,
        'google_maps_api_key': settings.GOOGLE_MAP_API_KEY,
        'map_center': {'lat': 33.7780, 'lng': -84.3980},
    }
    return render(request, 'campus/overview.html', context)


@require_GET
def location_list(request):
    locations = Location.objects.all()
    data = []
    
    for location in locations:
        location_data = {
            'name': location.name,
            'slug': location.slug,
            'description': location.description,
            'latitude': float(location.latitude),
            'longitude': float(location.longitude),
            'address': location.address,
            'category': location.category,
            'historical_info': location.historical_info,
            'photo_url': location.photo.url if location.photo else None,
        }
        data.append(location_data)
    
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


@csrf_exempt
@require_POST
@login_required
def toggle_bookmark(request, slug):
    """Toggle bookmark status for a location."""
    location = get_object_or_404(Location, slug=slug)
    
    # Try to get existing bookmark
    bookmark, created = Bookmark.objects.get_or_create(
        user=request.user,
        location=location
    )
    
    if not created:
        # Bookmark exists, remove it
        bookmark.delete()
        bookmarked = False
    else:
        # Bookmark was created
        bookmarked = True
    
    return JsonResponse({
        'bookmarked': bookmarked,
        'location_slug': slug
    })
