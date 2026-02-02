from django.urls import path
from . import views

app_name = 'custom_admin'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('users/', views.users_list, name='users_list'),
    path('users/ban/<int:user_id>/', views.ban_user_with_remark, name='user_ban'),
    
    path('posts/', views.posts_list, name='posts_list'),
    path('posts/detail/<int:post_id>/', views.post_detail_admin, name='post_detail_admin'),
    path('posts/flag/<int:post_id>/', views.flag_post, name='flag_post'),
    path('posts/delete/<int:post_id>/', views.delete_post, name='delete_post'),
    
    path('comments/', views.comments_list, name='comments_list'),
    path('comments/delete/<int:comment_id>/', views.delete_comment, name='comment_delete'),
    
    path('reports/', views.reports_list, name='reports_list'),
    path('reports/<str:report_type>/<int:report_id>/status/', views.update_report_status, name='update_report_status'),
    path('reports/user/<int:report_id>/detail/', views.view_user_report, name='view_user_report'),
    path('reports/post/<int:report_id>/detail/', views.view_post_report, name='view_post_report'),
    
    path('change-password/', views.change_password, name='change_password'),
]