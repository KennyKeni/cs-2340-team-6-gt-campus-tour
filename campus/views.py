import json
from json import JSONDecodeError
from typing import List

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .ai import CampusAiError, ChatMessage, get_landmark_context, run_landmark_chat
from .models import Location, Bookmark
from .forms import LocationForm


# -------------------------------------------------------------------------
#  EXISTING VIEWS (overview, API, chat)
# -------------------------------------------------------------------------
def campus_overview(request):
    """Renders interactive campus map with all known locations."""
    # Get all locations
    locations = Location.objects.all()
    
    # Get user's bookmarked location slugs if authenticated
    bookmarked_slugs = set()
    if request.user.is_authenticated:
        bookmarked_slugs = set(
            Bookmark.objects.filter(user=request.user).values_list('location__slug', flat=True)
        )
    
    # Sort locations: bookmarked first, then alphabetically
    locations_list = list(locations)
    locations_list.sort(key=lambda loc: (loc.slug not in bookmarked_slugs, loc.name))
    
    locations_payload = [
        {
            'name': location.name,
            'slug': location.slug,
            'description': location.description,
            'historical_info': location.historical_info,
            'latitude': float(location.latitude),
            'longitude': float(location.longitude),
            'address': location.address,
            'category': location.category,
            'image_url': location.image_url,
            'photo': location.photo.url if location.photo else None,
            'is_bookmarked': location.slug in bookmarked_slugs,
        }
        for location in locations_list
    ]
    context = {
        'locations': locations_list,
        'locations_payload': locations_payload,
        'bookmarked_slugs': list(bookmarked_slugs),
        'google_maps_api_key': settings.GOOGLE_MAP_API_KEY,
        'map_center': {'lat': 33.7780, 'lng': -84.3980},
    }
    return render(request, 'campus/overview.html', context)


@require_GET
def location_list(request):
    """Returns JSON with all campus locations (for front-end map JS)."""
    locations = Location.objects.all()
    data = []
    for location in locations:
        data.append(
            {
                'name': location.name,
                'slug': location.slug,
                'description': location.description,
                'historical_info': location.historical_info,
                'latitude': float(location.latitude),
                'longitude': float(location.longitude),
                'address': location.address,
                'category': location.category,
                'image_url': location.image_url,
                'photo': request.build_absolute_uri(location.photo.url)
                if location.photo
                else None,
            }
        )
    return JsonResponse({'locations': data})


@csrf_exempt
@require_POST
def chat_with_assistant(request):
    """Handles AI assistant chat messages about landmarks."""
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


# -------------------------------------------------------------------------
#  NEW ADMIN CRUD VIEWS (User Story #12 – Shashwat)
# -------------------------------------------------------------------------
def admin_check(user):
    """Only allow staff/admin users to access these routes."""
    return user.is_staff


@user_passes_test(admin_check)
def manage_locations(request):
    """List all campus points for admin management."""
    locations = Location.objects.all().order_by('name')
    return render(request, 'campus/manage_locations.html', {'locations': locations})


@user_passes_test(admin_check)
def add_location(request):
    """Add a new campus location."""
    if request.method == 'POST':
        form = LocationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('manage_locations')
    else:
        form = LocationForm()
    return render(request, 'campus/location_form.html', {'form': form, 'title': 'Add Location'})


@user_passes_test(admin_check)
def edit_location(request, slug):
    """Edit an existing campus location by slug."""
    location = get_object_or_404(Location, slug=slug)
    if request.method == 'POST':
        form = LocationForm(request.POST, request.FILES, instance=location)
        if form.is_valid():
            form.save()
            return redirect('manage_locations')
    else:
        form = LocationForm(instance=location)
    return render(request, 'campus/location_form.html', {'form': form, 'title': f'Edit {location.name}'})


@user_passes_test(admin_check)
def delete_location(request, slug):
    """Delete a campus location."""
    location = get_object_or_404(Location, slug=slug)
    if request.method == 'POST':
        location.delete()
        return redirect('manage_locations')
    return render(request, 'campus/confirm_delete.html', {'location': location})


# -------------------------------------------------------------------------
#  LOCATION DETAIL VIEW (User Story #9)
# -------------------------------------------------------------------------
def location_detail(request, slug):
    """Display detailed information about a specific location."""
    location = get_object_or_404(Location, slug=slug)

    # Check if user has bookmarked this location
    is_bookmarked = False
    if request.user.is_authenticated:
        is_bookmarked = Bookmark.objects.filter(user=request.user, location=location).exists()

    context = {
        'location': location,
        'is_bookmarked': is_bookmarked,
        'google_maps_api_key': settings.GOOGLE_MAP_API_KEY,
    }
    return render(request, 'campus/location_detail.html', context)


# -------------------------------------------------------------------------
#  BOOKMARK VIEWS (User Story #8)
# -------------------------------------------------------------------------
@login_required
@require_POST
def toggle_bookmark(request, slug):
    """Toggle bookmark status for a location."""
    location = get_object_or_404(Location, slug=slug)

    # Check if bookmark already exists
    bookmark = Bookmark.objects.filter(user=request.user, location=location).first()

    if bookmark:
        # Remove bookmark
        bookmark.delete()
        return JsonResponse({'bookmarked': False, 'message': 'Bookmark removed'})
    else:
        # Add bookmark
        Bookmark.objects.create(user=request.user, location=location)
        return JsonResponse({'bookmarked': True, 'message': 'Bookmark added'})
