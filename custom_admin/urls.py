from django.urls import path
from . import views

app_name = 'custom_admin'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('users/', views.users_list, name='users_list'),
    path('users/ban/<int:user_id>/', views.ban_user_with_remark, name='user_ban'),
    
    path('posts/', views.posts_list, name='posts_list'),
    path('posts/flag/<int:post_id>/', views.flag_post, name='flag_post'),
    path('posts/delete/<int:post_id>/', views.delete_post, name='delete_post'),
    
    path('comments/', views.comments_list, name='comments_list'),
    path('comments/delete/<int:comment_id>/', views.delete_comment, name='comment_delete'),
    
    path('change-password/', views.change_password, name='change_password'),
]