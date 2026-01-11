from django.urls import path
from . import views

app_name = 'chats'

urlpatterns = [
    path('', views.inbox_view, name='inbox'),
    path('<str:username>/', views.chat_room_view, name='chat_room'),
    path('search-ajax/', views.search_users_ajax, name='search_users_ajax'),
]