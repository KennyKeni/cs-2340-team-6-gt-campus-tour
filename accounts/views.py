from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render, get_object_or_404
from django.db.models import Count, Q
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json

from campus.models import Bookmark, Tour, TourBookmark

from .forms import CustomUserCreationForm, ProfileEditForm
from .models import UserProfile, Friendship


def register(request):
    """Handle user registration."""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile(request):
    """Display a summary of the user's campus activity."""
    location_qs = (
        Bookmark.objects
        .filter(user=request.user)
        .select_related('location')
    )
    tour_qs = (
        TourBookmark.objects
        .filter(user=request.user)
        .select_related('tour')
    )
    created_tours_qs = (
        Tour.objects
        .filter(user=request.user)
        .prefetch_related('stops__location')
        .annotate(stop_total=Count('stops'))
    )

    location_bookmarks = list(location_qs)
    tour_bookmarks = list(tour_qs)
    created_tours = list(created_tours_qs)

    full_name = request.user.get_full_name().strip()
    display_name = full_name if full_name else request.user.username
    name_for_initial = request.user.first_name or request.user.username or '?'
    initial = name_for_initial[0].upper()

    # Get or create user profile
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)

    context = {
        'location_bookmarks': location_bookmarks,
        'tour_bookmarks': tour_bookmarks,
        'created_tours': created_tours,
        'display_name': display_name,
        'user_initial': initial,
        'location_count': len(location_bookmarks),
        'tour_bookmark_count': len(tour_bookmarks),
        'created_tour_count': len(created_tours),
        'affiliation': user_profile.affiliation,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def edit_profile(request):
    """Edit user profile information."""
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileEditForm(request.POST)
        if form.is_valid():
            # Update User model fields
            request.user.first_name = form.cleaned_data['first_name'].strip()
            request.user.last_name = form.cleaned_data['last_name'].strip()
            request.user.save()

            # Update UserProfile model fields
            user_profile.affiliation = form.cleaned_data['affiliation'].strip()
            user_profile.is_private = form.cleaned_data['is_private']
            user_profile.save()

            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        # Pre-populate form with current values
        form = ProfileEditForm(initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'affiliation': user_profile.affiliation,
            'is_private': user_profile.is_private,
        })

    return render(request, 'accounts/edit_profile.html', {'form': form})


@login_required
def discover_users(request):
    """Display public user profiles."""
    search_query = request.GET.get('search', '').strip()

    # Get all users with public profiles (exclude current user)
    users_qs = User.objects.exclude(id=request.user.id).select_related('profile')

    # Filter out private profiles
    public_users = []
    for user in users_qs:
        profile, _ = UserProfile.objects.get_or_create(user=user)
        if not profile.is_private:
            public_users.append(user)

    # Apply search filter if provided
    if search_query:
        filtered_users = []
        for user in public_users:
            # Search in first name, last name, username, or affiliation
            profile = user.profile
            if (search_query.lower() in user.first_name.lower() or
                search_query.lower() in user.last_name.lower() or
                search_query.lower() in user.username.lower() or
                search_query.lower() in profile.affiliation.lower()):
                filtered_users.append(user)
        public_users = filtered_users

    # Annotate with stats
    user_data = []
    for user in public_users:
        profile = user.profile
        full_name = user.get_full_name().strip()
        display_name = full_name if full_name else user.username
        name_for_initial = user.first_name or user.username or '?'
        initial = name_for_initial[0].upper()

        # Get stats
        location_count = Bookmark.objects.filter(user=user).count()
        tour_count = Tour.objects.filter(user=user).count()

        user_data.append({
            'user': user,
            'profile': profile,
            'display_name': display_name,
            'initial': initial,
            'location_count': location_count,
            'tour_count': tour_count,
        })

    context = {
        'user_data': user_data,
        'search_query': search_query,
        'total_count': len(user_data),
    }
    return render(request, 'accounts/discover.html', context)


@login_required
def view_user_profile(request, username):
    """View another user's public profile."""
    user = get_object_or_404(User, username=username)
    user_profile, _ = UserProfile.objects.get_or_create(user=user)

    # Redirect to own profile if viewing self
    if user == request.user:
        return redirect('accounts:profile')

    # Check if profile is private
    if user_profile.is_private:
        messages.error(request, 'This profile is private.')
        return redirect('accounts:discover')

    # Get user's public data
    location_bookmarks = list(
        Bookmark.objects
        .filter(user=user)
        .select_related('location')
    )
    created_tours = list(
        Tour.objects
        .filter(user=user)
        .prefetch_related('stops__location')
        .annotate(stop_total=Count('stops'))
    )

    full_name = user.get_full_name().strip()
    display_name = full_name if full_name else user.username
    name_for_initial = user.first_name or user.username or '?'
    initial = name_for_initial[0].upper()

    # Check friendship status
    friendship_status = None
    friendship_id = None
    outgoing = Friendship.objects.filter(from_user=request.user, to_user=user).first()
    incoming = Friendship.objects.filter(from_user=user, to_user=request.user).first()
    
    if outgoing:
        friendship_status = outgoing.status
        friendship_id = outgoing.id
    elif incoming:
        if incoming.status == 'accepted':
            friendship_status = 'accepted'
            friendship_id = incoming.id

    context = {
        'profile_user': user,
        'user_profile': user_profile,
        'display_name': display_name,
        'user_initial': initial,
        'affiliation': user_profile.affiliation,
        'location_count': len(location_bookmarks),
        'tour_count': len(created_tours),
        'created_tours': created_tours,
        'friendship_status': friendship_status,
        'friendship_id': friendship_id,
    }
    return render(request, 'accounts/user_profile.html', context)


@login_required
def friends_list(request):
    """Display friends, pending incoming/outgoing requests."""
    # Get accepted friendships (both directions)
    friends_outgoing = Friendship.objects.filter(
        from_user=request.user, status='accepted'
    ).select_related('to_user', 'to_user__profile')
    
    friends_incoming = Friendship.objects.filter(
        to_user=request.user, status='accepted'
    ).select_related('from_user', 'from_user__profile')
    
    # Combine into a single friends list
    friends = []
    friend_ids = set()
    
    for friendship in friends_outgoing:
        if friendship.to_user.id not in friend_ids:
            friends.append({
                'user': friendship.to_user,
                'friendship_id': friendship.id,
                'since': friendship.created_at,
            })
            friend_ids.add(friendship.to_user.id)
    
    for friendship in friends_incoming:
        if friendship.from_user.id not in friend_ids:
            friends.append({
                'user': friendship.from_user,
                'friendship_id': friendship.id,
                'since': friendship.created_at,
            })
            friend_ids.add(friendship.from_user.id)
    
    # Sort by username
    friends.sort(key=lambda x: x['user'].username)
    
    # Get incoming pending requests
    incoming_requests = Friendship.objects.filter(
        to_user=request.user, status='pending'
    ).select_related('from_user', 'from_user__profile')
    
    # Get outgoing pending requests
    outgoing_requests = Friendship.objects.filter(
        from_user=request.user, status='pending'
    ).select_related('to_user', 'to_user__profile')
    
    context = {
        'friends': friends,
        'incoming_requests': incoming_requests,
        'outgoing_requests': outgoing_requests,
        'friends_count': len(friends),
        'incoming_count': incoming_requests.count(),
        'outgoing_count': outgoing_requests.count(),
    }
    return render(request, 'accounts/friends.html', context)


@login_required
@require_POST
def send_friend_request(request, user_id):
    """Send a friend request to another user."""
    to_user = get_object_or_404(User, id=user_id)
    
    # Can't friend yourself
    if to_user == request.user:
        return JsonResponse({'error': 'Cannot send friend request to yourself.'}, status=400)
    
    # Check if friendship already exists (in either direction)
    existing = Friendship.objects.filter(
        Q(from_user=request.user, to_user=to_user) |
        Q(from_user=to_user, to_user=request.user)
    ).first()
    
    if existing:
        if existing.status == 'accepted':
            return JsonResponse({'error': 'Already friends.'}, status=400)
        elif existing.status == 'pending':
            return JsonResponse({'error': 'Friend request already pending.'}, status=400)
        elif existing.status == 'rejected':
            # Allow re-sending after rejection
            existing.status = 'pending'
            existing.from_user = request.user
            existing.to_user = to_user
            existing.save()
            return JsonResponse({'success': True, 'message': 'Friend request sent.'})
    
    # Create new friendship request
    Friendship.objects.create(from_user=request.user, to_user=to_user, status='pending')
    return JsonResponse({'success': True, 'message': 'Friend request sent.'})


@login_required
@require_POST
def respond_to_request(request, friendship_id):
    """Accept or reject a friend request."""
    friendship = get_object_or_404(Friendship, id=friendship_id, to_user=request.user, status='pending')
    
    try:
        data = json.loads(request.body)
        action = data.get('action')
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({'error': 'Invalid request.'}, status=400)
    
    if action == 'accept':
        friendship.status = 'accepted'
        friendship.save()
        return JsonResponse({'success': True, 'message': 'Friend request accepted.'})
    elif action == 'reject':
        friendship.status = 'rejected'
        friendship.save()
        return JsonResponse({'success': True, 'message': 'Friend request rejected.'})
    else:
        return JsonResponse({'error': 'Invalid action.'}, status=400)


@login_required
@require_POST
def remove_friend(request, user_id):
    """Remove a friend (delete friendship in both directions)."""
    user = get_object_or_404(User, id=user_id)
    
    # Delete friendships in both directions
    deleted_count = Friendship.objects.filter(
        Q(from_user=request.user, to_user=user) |
        Q(from_user=user, to_user=request.user)
    ).delete()[0]
    
    if deleted_count > 0:
        return JsonResponse({'success': True, 'message': 'Friend removed.'})
    else:
        return JsonResponse({'error': 'No friendship found.'}, status=404)
