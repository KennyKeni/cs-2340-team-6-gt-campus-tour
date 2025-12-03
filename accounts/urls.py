from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('discover/', views.discover_users, name='discover'),
    path('users/<str:username>/', views.view_user_profile, name='user_profile'),
    
    # Friend management routes (User Story #11)
    path('friends/', views.friends_list, name='friends_list'),
    path('friends/request/<int:user_id>/', views.send_friend_request, name='send_friend_request'),
    path('friends/respond/<int:friendship_id>/', views.respond_to_request, name='respond_to_request'),
    path('friends/remove/<int:user_id>/', views.remove_friend, name='remove_friend'),
]
