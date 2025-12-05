import json
import logging
from json import JSONDecodeError
from typing import List

from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.db.models import Q

from .ai import CampusAiError, ChatMessage, ChatResult, get_landmark_context, run_landmark_chat, TourAgentDeps
from .models import Location, Bookmark, Tour, TourStop, TourBookmark, SharedTour, Rating
from .forms import LocationForm
from .route_utils import calculate_route_segments, RouteCalculationError
from accounts.models import Friendship

logger = logging.getLogger(__name__)


# -------------------------------------------------------------------------
#  EXISTING VIEWS (overview, API, chat)
# -------------------------------------------------------------------------
def campus_overview(request):
    """Renders interactive campus map with all known locations."""
    locations = Location.objects.all()

    bookmarked_slugs = set()
    if request.user.is_authenticated:
        bookmarked_slugs = set(
            Bookmark.objects.filter(user=request.user).values_list('location__slug', flat=True)
        )

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

    tours = []
    shared_tours = []
    bookmarked_tour_ids = set()
    if request.user.is_authenticated:
        tours = Tour.objects.filter(user=request.user).prefetch_related('stops__location')
        bookmarked_tour_ids = set(
            TourBookmark.objects.filter(user=request.user).values_list('tour__id', flat=True)
        )

        shared_tour_records = SharedTour.objects.filter(
            shared_with=request.user
        ).select_related('tour', 'shared_by').prefetch_related('tour__stops__location')
        shared_tours = [
            {
                'tour': record.tour,
                'shared_by': record.shared_by,
                'share_id': record.id,
            }
            for record in shared_tour_records
        ]

    api_key = settings.GOOGLE_MAP_API_KEY

    context = {
        'locations': locations_list,
        'locations_payload': locations_payload,
        'bookmarked_slugs': list(bookmarked_slugs),
        'tours': tours,
        'shared_tours': shared_tours,
        'bookmarked_tour_ids': bookmarked_tour_ids,
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
    bookmarked_tour_ids = set(
        TourBookmark.objects.filter(user=request.user).values_list('tour__id', flat=True)
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
        
        # Get shares for this tour
        shares = SharedTour.objects.filter(tour=tour).select_related('shared_with')
        shared_with = [{'id': s.shared_with.id, 'username': s.shared_with.username, 'share_id': s.id} for s in shares]
        
        tours_payload.append({
            'id': tour.id,
            'name': tour.name,
            'description': tour.description,
            'created_at': tour.created_at.isoformat(),
            'stops': stops,
            'is_bookmarked': tour.id in bookmarked_tour_ids,
            'shared_with': shared_with,
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

    # Get user's friends for sharing
    friends_outgoing = Friendship.objects.filter(
        from_user=request.user, status='accepted'
    ).select_related('to_user')
    
    friends_incoming = Friendship.objects.filter(
        to_user=request.user, status='accepted'
    ).select_related('from_user')
    
    friends = []
    friend_ids = set()
    
    for friendship in friends_outgoing:
        if friendship.to_user.id not in friend_ids:
            friends.append({
                'id': friendship.to_user.id,
                'username': friendship.to_user.username,
                'display_name': friendship.to_user.get_full_name() or friendship.to_user.username,
            })
            friend_ids.add(friendship.to_user.id)
    
    for friendship in friends_incoming:
        if friendship.from_user.id not in friend_ids:
            friends.append({
                'id': friendship.from_user.id,
                'username': friendship.from_user.username,
                'display_name': friendship.from_user.get_full_name() or friendship.from_user.username,
            })
            friend_ids.add(friendship.from_user.id)
    
    friends.sort(key=lambda x: x['username'])

    # Get tours shared with the user
    shared_with_user = SharedTour.objects.filter(
        shared_with=request.user
    ).select_related('tour', 'shared_by', 'tour__user').prefetch_related('tour__stops__location')
    
    shared_tours_payload = []
    for share in shared_with_user:
        tour = share.tour
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
        
        shared_tours_payload.append({
            'share_id': share.id,
            'tour_id': tour.id,
            'name': tour.name,
            'description': tour.description,
            'created_at': tour.created_at.isoformat(),
            'shared_by': share.shared_by.username,
            'shared_by_display': share.shared_by.get_full_name() or share.shared_by.username,
            'shared_at': share.created_at.isoformat(),
            'stops': stops,
            'route_data': tour.route_data,
        })

    context = {
        'tours': tours,
        'tours_payload': tours_payload,
        'locations': locations,
        'locations_payload': locations_payload,
        'bookmarked_tour_ids': bookmarked_tour_ids,
        'friends': friends,
        'shared_tours': shared_tours_payload,
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
    locations_map = {loc.id: loc for loc in locations}

    deps = TourAgentDeps(
        user=request.user,
        locations_map=locations_map,
    )

    try:
        result = run_landmark_chat(
            message,
            history=chat_history,
            landmark_context=landmark_context,
            deps=deps,
        )
    except CampusAiError as exc:
        return JsonResponse({'error': str(exc)}, status=503)

    response_data = {'reply': result.reply}
    if result.created_tour_id:
        response_data['created_tour_id'] = result.created_tour_id

    return JsonResponse(response_data)


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

    is_bookmarked = False
    user_rating = None
    if request.user.is_authenticated:
        is_bookmarked = Bookmark.objects.filter(user=request.user, location=location).exists()
        user_rating = Rating.objects.filter(user=request.user, location=location).select_related('responded_by').first()

    context = {
        'location': location,
        'is_bookmarked': is_bookmarked,
        'user_rating': user_rating,
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


@login_required
@require_POST
def toggle_tour_bookmark(request, tour_id):
    """Toggle bookmark status for a tour."""
    tour = get_object_or_404(Tour, id=tour_id)

    # Check if bookmark already exists
    bookmark = TourBookmark.objects.filter(user=request.user, tour=tour).first()

    if bookmark:
        # Remove bookmark
        bookmark.delete()
        return JsonResponse({'bookmarked': False, 'message': 'Bookmark removed'})
    else:
        # Add bookmark
        TourBookmark.objects.create(user=request.user, tour=tour)
        return JsonResponse({'bookmarked': True, 'message': 'Bookmark added'})


# -------------------------------------------------------------------------
#  TOUR VIEWS (User Story #7)
# -------------------------------------------------------------------------
@csrf_exempt
@login_required
def tour_list(request):
    """List all tours for the authenticated user with their stops (GET) or create a new tour (POST)."""
    if request.method == 'GET':
        owned_tours = Tour.objects.filter(user=request.user).prefetch_related('stops__location')
        shared_records = SharedTour.objects.filter(
            shared_with=request.user
        ).select_related('tour', 'shared_by').prefetch_related('tour__stops__location')

        data = []
        for tour in owned_tours:
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
                'tour_type': 'owned',
            })

        for record in shared_records:
            tour = record.tour
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
                'tour_type': 'shared',
                'shared_by': record.shared_by.username,
                'shared_by_display': record.shared_by.get_full_name() or record.shared_by.username,
                'share_id': record.id,
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
                logger.info(f"Successfully calculated route for tour {tour.id} ({tour.name}) with {len(route_segments) if route_segments else 0} segments")
            except RouteCalculationError as e:
                logger.error(f"Failed to calculate route for tour {tour.id} ({tour.name}): {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error calculating route for tour {tour.id} ({tour.name}): {str(e)}")

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
                logger.info(f"Successfully calculated route for tour {tour.id} ({tour.name}) with {len(route_segments) if route_segments else 0} segments")
            except RouteCalculationError as e:
                logger.error(f"Failed to calculate route for tour {tour.id} ({tour.name}): {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error calculating route for tour {tour.id} ({tour.name}): {str(e)}")

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

        is_bookmarked = TourBookmark.objects.filter(user=request.user, tour=tour).exists()

        return JsonResponse({
            'id': tour.id,
            'name': tour.name,
            'description': tour.description,
            'created_at': tour.created_at.isoformat(),
            'stops': stops,
            'route_data': tour.route_data,
            'is_bookmarked': is_bookmarked,
        })
    elif request.method == 'DELETE':
        """Delete a tour."""
        tour.delete()
        return JsonResponse({'success': True}, status=200)
    else:
        return JsonResponse({'error': 'Method not allowed.'}, status=405)


# -------------------------------------------------------------------------
#  TOUR SHARING VIEWS (User Story #11)
# -------------------------------------------------------------------------
@login_required
@require_POST
def share_tour(request, tour_id):
    """Share a tour with one or more friends."""
    tour = get_object_or_404(Tour, id=tour_id)
    
    # Validate tour ownership
    if tour.user != request.user:
        return JsonResponse({'error': 'You can only share your own tours.'}, status=403)
    
    try:
        data = json.loads(request.body)
        friend_ids = data.get('friend_ids', [])
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({'error': 'Invalid request.'}, status=400)
    
    if not isinstance(friend_ids, list) or not friend_ids:
        return JsonResponse({'error': 'friend_ids must be a non-empty array.'}, status=400)
    
    shared_count = 0
    already_shared = []
    not_friends = []
    
    for friend_id in friend_ids:
        try:
            friend_id = int(friend_id)
        except (ValueError, TypeError):
            continue
        
        # Check if users are friends
        is_friend = Friendship.objects.filter(
            Q(from_user=request.user, to_user_id=friend_id, status='accepted') |
            Q(from_user_id=friend_id, to_user=request.user, status='accepted')
        ).exists()
        
        if not is_friend:
            not_friends.append(friend_id)
            continue
        
        # Check if already shared
        existing = SharedTour.objects.filter(tour=tour, shared_with_id=friend_id).first()
        if existing:
            already_shared.append(friend_id)
            continue
        
        # Create share
        SharedTour.objects.create(
            tour=tour,
            shared_by=request.user,
            shared_with_id=friend_id,
        )
        shared_count += 1
    
    response = {
        'success': True,
        'shared_count': shared_count,
    }
    
    if already_shared:
        response['already_shared'] = already_shared
    if not_friends:
        response['not_friends'] = not_friends
    
    return JsonResponse(response)


@login_required
def shared_tours_list(request):
    """Get all tours shared with the current user."""
    shared_tours = SharedTour.objects.filter(
        shared_with=request.user
    ).select_related('tour', 'shared_by', 'tour__user').prefetch_related('tour__stops__location')
    
    tours_data = []
    for share in shared_tours:
        tour = share.tour
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
        
        tours_data.append({
            'share_id': share.id,
            'tour_id': tour.id,
            'name': tour.name,
            'description': tour.description,
            'created_at': tour.created_at.isoformat(),
            'shared_by': share.shared_by.username,
            'shared_by_id': share.shared_by.id,
            'shared_at': share.created_at.isoformat(),
            'stops': stops,
            'route_data': tour.route_data,
        })
    
    return JsonResponse({'tours': tours_data})


@login_required
@require_http_methods(['DELETE'])
def remove_shared_tour(request, share_id):
    """Remove a shared tour from the recipient's list."""
    share = get_object_or_404(SharedTour, id=share_id, shared_with=request.user)
    share.delete()
    return JsonResponse({'success': True, 'message': 'Shared tour removed.'})


@login_required
@require_http_methods(['DELETE'])
def revoke_tour_share(request, share_id):
    """Tour owner revokes sharing from a specific user."""
    share = get_object_or_404(SharedTour, id=share_id)

    # Validate ownership
    if share.tour.user != request.user:
        return JsonResponse({'error': 'You can only revoke shares of your own tours.'}, status=403)

    share.delete()
    return JsonResponse({'success': True, 'message': 'Tour sharing revoked.'})


# -------------------------------------------------------------------------
#  ADMIN FEEDBACK VIEWS (User Story #13)
# -------------------------------------------------------------------------
@user_passes_test(admin_check)
def feedback_dashboard(request):
    """Admin dashboard to view and manage user feedback."""
    ratings = Rating.objects.select_related('user', 'location', 'responded_by').all()

    status_filter = request.GET.get('status', '')
    if status_filter and status_filter in ['new', 'reviewed', 'resolved']:
        ratings = ratings.filter(status=status_filter)

    location_filter = request.GET.get('location', '')
    if location_filter:
        ratings = ratings.filter(location__slug=location_filter)

    date_from = request.GET.get('date_from', '')
    if date_from:
        try:
            from_date = datetime.strptime(date_from, '%Y-%m-%d')
            ratings = ratings.filter(created_at__date__gte=from_date.date())
        except ValueError:
            pass

    date_to = request.GET.get('date_to', '')
    if date_to:
        try:
            to_date = datetime.strptime(date_to, '%Y-%m-%d')
            ratings = ratings.filter(created_at__date__lte=to_date.date())
        except ValueError:
            pass

    ratings = ratings.order_by('-created_at')

    paginator = Paginator(ratings, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    locations = Location.objects.all().order_by('name')

    context = {
        'page_obj': page_obj,
        'locations': locations,
        'status_filter': status_filter,
        'location_filter': location_filter,
        'date_from': date_from,
        'date_to': date_to,
        'status_choices': Rating.STATUS_CHOICES,
    }
    return render(request, 'campus/feedback_dashboard.html', context)


@csrf_exempt
@user_passes_test(admin_check)
@require_POST
def respond_to_feedback(request, rating_id):
    """Admin responds to a feedback item and updates its status."""
    rating = get_object_or_404(Rating, id=rating_id)

    try:
        payload = json.loads(request.body)
    except JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON payload.'}, status=400)

    response_text = (payload.get('response') or '').strip()
    new_status = payload.get('status', '')

    if new_status and new_status not in ['new', 'reviewed', 'resolved']:
        return JsonResponse({'error': 'Invalid status value.'}, status=400)

    if response_text:
        rating.admin_response = response_text
        rating.responded_by = request.user
        rating.responded_at = timezone.now()

    if new_status:
        rating.status = new_status

    rating.save()

    return JsonResponse({
        'success': True,
        'rating_id': rating.id,
        'status': rating.status,
        'admin_response': rating.admin_response,
        'responded_by': rating.responded_by.username if rating.responded_by else None,
        'responded_at': rating.responded_at.isoformat() if rating.responded_at else None,
    })
