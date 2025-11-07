from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.db.models import Count
from django.contrib import messages

from campus.models import Bookmark, Tour, TourBookmark

from .forms import CustomUserCreationForm, ProfileEditForm
from .models import UserProfile


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
            user_profile.save()

            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        # Pre-populate form with current values
        form = ProfileEditForm(initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'affiliation': user_profile.affiliation,
        })

    return render(request, 'accounts/edit_profile.html', {'form': form})
