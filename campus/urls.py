from django.urls import path
from . import views

app_name = 'campus'

urlpatterns = [
    # Existing endpoints
    path('', views.campus_overview, name='overview'),
    path('api/locations/', views.location_list, name='location-list'),
    path('api/chat/', views.chat_with_assistant, name='chat'),

    # ---------------------------------------------------------------------
    # Location detail page (User Story #9)
    # ---------------------------------------------------------------------
    path('locations/<slug:slug>/', views.location_detail, name='location-detail'),

    # ---------------------------------------------------------------------
    # Bookmark endpoints (User Story #8)
    # ---------------------------------------------------------------------
    path('api/locations/<slug:slug>/bookmark/', views.toggle_bookmark, name='toggle-bookmark'),
    path('api/tours/<int:tour_id>/bookmark/', views.toggle_tour_bookmark, name='toggle-tour-bookmark'),

    # ---------------------------------------------------------------------
    # Rating endpoints (User Story #10)
    # ---------------------------------------------------------------------
    path('api/locations/<slug:slug>/rate/', views.rate_location, name='rate_location'),

    # ---------------------------------------------------------------------
    # New admin CRUD endpoints (User Story #12 – Shashwat)
    # ---------------------------------------------------------------------
    path('manage/', views.manage_locations, name='manage_locations'),
    path('add/', views.add_location, name='add_location'),
    path('edit/<slug:slug>/', views.edit_location, name='edit_location'),
    path('delete/<slug:slug>/', views.delete_location, name='delete_location'),

    # ---------------------------------------------------------------------
    # Tour endpoints (User Story #7)
    # ---------------------------------------------------------------------
    path('tours/', views.tour_manage, name='tour-manage'),
    path('tours/create/', views.tour_create, name='tour-create'),
    path('tours/<int:tour_id>/edit/', views.tour_create, name='tour-edit'),
    path('api/tours/', views.tour_list, name='tour-list'),
    path('api/tours/<int:tour_id>/', views.tour_detail, name='tour-detail'),
    
    # ---------------------------------------------------------------------
    # Tour sharing endpoints (User Story #11)
    # ---------------------------------------------------------------------
    path('api/tours/<int:tour_id>/share/', views.share_tour, name='share_tour'),
    path('api/tours/shared/', views.shared_tours_list, name='shared_tours_list'),
    path('api/tours/shared/<int:share_id>/', views.remove_shared_tour, name='remove_shared_tour'),
    path('api/tours/shared/<int:share_id>/revoke/', views.revoke_tour_share, name='revoke_tour_share'),

    # ---------------------------------------------------------------------
    # Admin Feedback endpoints (User Story #13)
    # ---------------------------------------------------------------------
    path('admin/feedback/', views.feedback_dashboard, name='feedback_dashboard'),
    path('admin/feedback/<int:rating_id>/respond/', views.respond_to_feedback, name='respond_to_feedback'),
]
