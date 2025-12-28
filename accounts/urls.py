from django.urls import path
from . import views

app_name = 'accounts'  # For namespacing

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('check-username/', views.check_username, name='check_username'),
    
    path('check-email/', views.check_email, name='check_email'),
    path('profile/<str:username>/', views.profile_view, name='profile'),

    # 2. The Shortcut (if someone visits /accounts/profile/, redirect them to their named profile)
    path('profile/', views.current_profile_redirect, name='current_profile'),
    path('follow/<str:username>/', views.follow_user_view, name='follow_user'),
    path('remove-follower/<str:username>/', views.remove_follower_view, name='remove_follower'),

    path('search-users/', views.search_users_ajax, name='search_users_ajax'),
]