import json
from json import JSONDecodeError
from typing import List

from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST, require_http_methods

from .ai import CampusAiError, ChatMessage, get_landmark_context, run_landmark_chat
from .models import Location, Bookmark, Tour, TourStop
from .forms import LocationForm
from .route_utils import calculate_route_segments, RouteCalculationError


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
    
    # Get user's tours if authenticated
    tours = []
    if request.user.is_authenticated:
        tours = Tour.objects.filter(user=request.user).prefetch_related('stops__location')
    
    # Get API key from settings
    api_key = settings.GOOGLE_MAP_API_KEY
    
    context = {
        'locations': locations_list,
        'locations_payload': locations_payload,
        'bookmarked_slugs': list(bookmarked_slugs),
        'tours': tours,
        'google_maps_api_key': settings.GOOGLE_MAP_API_KEY,
        'map_center': {'lat': 33.7780, 'lng': -84.3980},
    }
    return render(request, 'campus/overview.html', context)


@login_required
def tour_create(request, tour_id=None):
    """Render the tour creation/edit page."""
    tour = None
    tour_payload = None

    if tour_id:
        tour = get_object_or_404(Tour, id=tour_id, user=request.user)
        stops = []
        for stop in tour.stops.all():
            stops.append({
                'id': stop.id,
                'location_id': stop.location.id,
                'order': stop.order,
                'location': {
                    'id': stop.location.id,
                    'name': stop.location.name,
                    'slug': stop.location.slug,
                    'description': stop.location.description,
                    'latitude': float(stop.location.latitude),
                    'longitude': float(stop.location.longitude),
                    'address': stop.location.address,
                    'category': stop.location.category,
                }
            })
        tour_payload = {
            'id': tour.id,
            'name': tour.name,
            'description': tour.description,
            'stops': stops,
        }

    locations = Location.objects.all()
    bookmarked_slugs = set(
        Bookmark.objects.filter(user=request.user).values_list('location__slug', flat=True)
    )

    locations_payload = [
        {
            'id': location.id,
            'name': location.name,
            'slug': location.slug,
            'description': location.description,
            'latitude': float(location.latitude),
            'longitude': float(location.longitude),
            'address': location.address,
            'category': location.category,
            'is_bookmarked': location.slug in bookmarked_slugs,
        }
        for location in locations
    ]
    context = {
        'locations': locations,
        'locations_payload': locations_payload,
        'tour': tour,
        'tour_payload': tour_payload,
        'is_edit': tour_id is not None,
    }
    return render(request, 'campus/tour_create.html', context)


@login_required
def tour_manage(request):
    """Render the tour management page where users can view and edit their tours."""
    tours = Tour.objects.filter(user=request.user).prefetch_related('stops__location')
    locations = Location.objects.all()
    bookmarked_slugs = set(
        Bookmark.objects.filter(user=request.user).values_list('location__slug', flat=True)
    )

    tours_payload = []
    for tour in tours:
        stops = []
        for stop in tour.stops.all():
            stops.append({
                'id': stop.id,
                'location_id': stop.location.id,
                'order': stop.order,
                'location': {
                    'id': stop.location.id,
                    'name': stop.location.name,
                    'slug': stop.location.slug,
                    'description': stop.location.description,
                    'latitude': float(stop.location.latitude),
                    'longitude': float(stop.location.longitude),
                    'address': stop.location.address,
                    'category': stop.location.category,
                }
            })
        tours_payload.append({
            'id': tour.id,
            'name': tour.name,
            'description': tour.description,
            'created_at': tour.created_at.isoformat(),
            'stops': stops,
        })

    locations_payload = [
        {
            'id': location.id,
            'name': location.name,
            'slug': location.slug,
            'description': location.description,
            'latitude': float(location.latitude),
            'longitude': float(location.longitude),
            'address': location.address,
            'category': location.category,
            'is_bookmarked': location.slug in bookmarked_slugs,
        }
        for location in locations
    ]

    context = {
        'tours': tours,
        'tours_payload': tours_payload,
        'locations': locations,
        'locations_payload': locations_payload,
    }
    return render(request, 'campus/tour_manage.html', context)


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
@login_required
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


# -------------------------------------------------------------------------
#  TOUR VIEWS (User Story #7)
# -------------------------------------------------------------------------
@csrf_exempt
@login_required
def tour_list(request):
    """List all tours for the authenticated user with their stops (GET) or create a new tour (POST)."""
    if request.method == 'GET':
        tours = Tour.objects.filter(user=request.user).prefetch_related('stops__location')
        data = []
        for tour in tours:
            stops = []
            for stop in tour.stops.all():
                stops.append({
                    'id': stop.id,
                    'location_id': stop.location.id,
                    'order': stop.order,
                    'location': {
                        'id': stop.location.id,
                        'name': stop.location.name,
                        'slug': stop.location.slug,
                        'description': stop.location.description,
                        'latitude': float(stop.location.latitude),
                        'longitude': float(stop.location.longitude),
                        'address': stop.location.address,
                        'category': stop.location.category,
                    }
                })
            data.append({
                'id': tour.id,
                'name': tour.name,
                'description': tour.description,
                'created_at': tour.created_at.isoformat(),
                'stops': stops,
                'route_data': tour.route_data,
            })
        return JsonResponse({'tours': data})
    elif request.method == 'POST':
        """Create a new tour for the authenticated user."""
        try:
            payload = json.loads(request.body)
        except JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON payload.'}, status=400)

        name = (payload.get('name') or '').strip()
        if not name:
            return JsonResponse({'error': 'Tour name is required.'}, status=400)

        description = (payload.get('description') or '').strip()
        location_ids = payload.get('location_ids', [])

        if not isinstance(location_ids, list):
            return JsonResponse({'error': 'location_ids must be an array.'}, status=400)

        if not location_ids:
            return JsonResponse({'error': 'At least one location is required.'}, status=400)

        # Validate that all locations exist
        locations = Location.objects.filter(id__in=location_ids)
        if locations.count() != len(location_ids):
            return JsonResponse({'error': 'One or more locations not found.'}, status=400)

        # Create tour
        tour = Tour.objects.create(
            user=request.user,
            name=name,
            description=description,
        )

        # Create tour stops in order
        for order, location_id in enumerate(location_ids, start=1):
            location = locations.get(id=location_id)
            TourStop.objects.create(
                tour=tour,
                location=location,
                order=order,
            )

        # Calculate and save route segments
        stops_data = []
        for stop in tour.stops.all():
            stops_data.append({
                'id': stop.location.id,
                'name': stop.location.name,
                'latitude': float(stop.location.latitude),
                'longitude': float(stop.location.longitude),
            })

        if len(stops_data) >= 2:
            try:
                route_segments = calculate_route_segments(stops_data)
                tour.route_data = {'segments': route_segments} if route_segments else None
                tour.save()
            except RouteCalculationError as e:
                pass

        # Return created tour with stops
        stops = []
        for stop in tour.stops.all():
            stops.append({
                'id': stop.id,
                'location_id': stop.location.id,
                'order': stop.order,
                'location': {
                    'id': stop.location.id,
                    'name': stop.location.name,
                    'slug': stop.location.slug,
                    'description': stop.location.description,
                    'latitude': float(stop.location.latitude),
                    'longitude': float(stop.location.longitude),
                    'address': stop.location.address,
                    'category': stop.location.category,
                }
            })

        return JsonResponse({
            'id': tour.id,
            'name': tour.name,
            'description': tour.description,
            'created_at': tour.created_at.isoformat(),
            'stops': stops,
            'route_data': tour.route_data,
        }, status=201)
    else:
        return JsonResponse({'error': 'Method not allowed.'}, status=405)


@csrf_exempt
@login_required
def tour_detail(request, tour_id):
    """Update (PUT) or delete (DELETE) a tour."""
    tour = get_object_or_404(Tour, id=tour_id)

    # Check ownership
    if tour.user != request.user:
        return JsonResponse({'error': 'You do not have permission to modify this tour.'}, status=403)

    if request.method == 'PUT':
        """Update an existing tour (name, description, and all stops with ordering)."""
        try:
            payload = json.loads(request.body)
        except JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON payload.'}, status=400)

        name = (payload.get('name') or '').strip()
        if not name:
            return JsonResponse({'error': 'Tour name is required.'}, status=400)

        description = (payload.get('description') or '').strip()
        location_ids = payload.get('location_ids', [])

        if not isinstance(location_ids, list):
            return JsonResponse({'error': 'location_ids must be an array.'}, status=400)

        if not location_ids:
            return JsonResponse({'error': 'At least one location is required.'}, status=400)

        # Validate that all locations exist
        locations = Location.objects.filter(id__in=location_ids)
        if locations.count() != len(location_ids):
            return JsonResponse({'error': 'One or more locations not found.'}, status=400)

        # Update tour basic info
        tour.name = name
        tour.description = description
        tour.save()

        # Delete existing stops
        tour.stops.all().delete()

        # Create new stops in order
        for order, location_id in enumerate(location_ids, start=1):
            location = locations.get(id=location_id)
            TourStop.objects.create(
                tour=tour,
                location=location,
                order=order,
            )

        # Recalculate and save route segments
        stops_data = []
        for stop in tour.stops.all():
            stops_data.append({
                'id': stop.location.id,
                'name': stop.location.name,
                'latitude': float(stop.location.latitude),
                'longitude': float(stop.location.longitude),
            })

        if len(stops_data) >= 2:
            try:
                route_segments = calculate_route_segments(stops_data)
                tour.route_data = {'segments': route_segments} if route_segments else None
                tour.save()
            except RouteCalculationError as e:
                pass

        # Return updated tour with stops
        stops = []
        for stop in tour.stops.all():
            stops.append({
                'id': stop.id,
                'location_id': stop.location.id,
                'order': stop.order,
                'location': {
                    'id': stop.location.id,
                    'name': stop.location.name,
                    'slug': stop.location.slug,
                    'description': stop.location.description,
                    'latitude': float(stop.location.latitude),
                    'longitude': float(stop.location.longitude),
                    'address': stop.location.address,
                    'category': stop.location.category,
                }
            })

        return JsonResponse({
            'id': tour.id,
            'name': tour.name,
            'description': tour.description,
            'created_at': tour.created_at.isoformat(),
            'stops': stops,
            'route_data': tour.route_data,
        })
    elif request.method == 'DELETE':
        """Delete a tour."""
        tour.delete()
        return JsonResponse({'success': True}, status=200)
    else:
        return JsonResponse({'error': 'Method not allowed.'}, status=405)
