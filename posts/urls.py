from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('home/', views.home_view, name='home'),
    path('create/', views.create_post_view, name='create'),
    path('like/<int:post_id>/', views.like_post_view, name='like_post'),
    path('comment/<int:post_id>/', views.add_comment_view, name='add_comment'),
]