from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('home/', views.home_view, name='home'),
    path('create/', views.create_post_view, name='create'),
    path('like/<int:post_id>/', views.like_post_view, name='like_post'),
    path('comment/<int:post_id>/', views.add_comment_view, name='add_comment'),
    path('get-comments/<int:post_id>/', views.get_comments_ajax, name='get_comments_ajax'),
    path('get-likes/<int:post_id>/', views.get_likes_ajax, name='get_likes_ajax'),
    path('explore/', views.explore_view, name='explore'),
    path('post-detail/<int:post_id>/', views.post_detail_ajax, name='post_detail_ajax'),
]