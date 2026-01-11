from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Max
from django.http import JsonResponse
from accounts.models import User, Follow
from .models import Thread
from typing import List, Any

@login_required
def inbox_view(request):
    my_pk = request.user.pk

    # 1. Fetch threads where the user is a participant
    # Annotate with the latest message timestamp to order the inbox
    threads_qs = Thread.objects.filter(
        Q(first_user_id=my_pk) | Q(second_user_id=my_pk)
    ).annotate(last_msg_time=Max('messages__timestamp')).order_by('-last_msg_time')

    thread_list_data = []
    messaged_pks = []

    for thread in threads_qs:
        # Determine the person I am talking to
        if thread.first_user_id == my_pk:
            other_user = thread.second_user
        else:
            other_user = thread.first_user
        
        messaged_pks.append(other_user.pk)

        # Get last message safely
        last_msg = thread.messages.order_by('-timestamp').first()
        # Count unread messages from the OTHER user
        unread_count = thread.messages.filter(sender=other_user, is_read=False).count()

        thread_list_data.append({
            'other_user': other_user,
            'last_msg': last_msg,
            'unread_count': unread_count
        })

    # 2. Suggestions logic (Followed users not yet messaged)
    suggestions = User.objects.filter(followers__follower=request.user)\
        .exclude(pk__in=messaged_pks)\
        .exclude(is_staff=True).distinct()[:5]

    return render(request, 'chats/inbox.html', {
        'threads': thread_list_data,
        'suggestions': suggestions
    })

@login_required
def search_users_ajax(request):
    query = request.GET.get('q', '').strip()
    users = User.objects.filter(
        Q(username__icontains=query) | Q(first_name__icontains=query)
    ).exclude(Q(is_staff=True) | Q(pk=request.user.pk))[:8]

    results = []
    for u in users:
        results.append({
            'username': u.username,
            'avatar': u.profile_image.url if u.profile_image else f"https://ui-avatars.com/api/?name={u.username}",
            'url': f"/chats/{u.username}/"
        })
    return JsonResponse({'users': results})


@login_required
def chat_room_view(request, username: str):
    other_user = get_object_or_404(User, username=username)
    my_pk = request.user.pk
    other_pk = other_user.pk
    
    # Try to get the thread, but DO NOT create it yet
    thread = Thread.objects.filter(
        Q(first_user_id=my_pk, second_user_id=other_pk) | 
        Q(first_user_id=other_pk, second_user_id=my_pk)
    ).first()
    
    messages = []
    if thread:
        # Mark messages as read
        thread.messages.filter(sender=other_user, is_read=False).update(is_read=True)
        messages = thread.messages.all()
    
    return render(request, 'chats/chat_room.html', {
        'other_user': other_user,
        'thread_messages': messages,
        'thread': thread # Might be None
    })