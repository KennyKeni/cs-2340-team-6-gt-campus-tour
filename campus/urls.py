from django.urls import path
from . import views

app_name = 'campus'

urlpatterns = [
    # Existing endpoints
    path('', views.campus_overview, name='overview'),
    path('api/locations/', views.location_list, name='location-list'),
    path('api/chat/', views.chat_with_assistant, name='chat'),

    # ---------------------------------------------------------------------
    # Bookmark endpoints (User Story #8)
    # ---------------------------------------------------------------------
    path('api/locations/<slug:slug>/bookmark/', views.toggle_bookmark, name='toggle-bookmark'),

    # ---------------------------------------------------------------------
    # New admin CRUD endpoints (User Story #12 – Shashwat)
    # ---------------------------------------------------------------------
    path('manage/', views.manage_locations, name='manage_locations'),
    path('add/', views.add_location, name='add_location'),
    path('edit/<slug:slug>/', views.edit_location, name='edit_location'),
    path('delete/<slug:slug>/', views.delete_location, name='delete_location'),
]
