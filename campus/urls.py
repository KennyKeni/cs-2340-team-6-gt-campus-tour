from django.urls import path

from . import views

app_name = 'campus'

urlpatterns = [
    path('', views.campus_overview, name='overview'),
    path('api/locations/', views.location_list, name='location-list'),
    path('api/locations/<slug:slug>/bookmark/', views.toggle_bookmark, name='toggle-bookmark'),
    path('api/chat/', views.chat_with_assistant, name='chat'),
]
