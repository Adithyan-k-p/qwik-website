from .models import Message
from django.db.models import Q

def unread_messages_count(request):
    if request.user.is_authenticated:
        # Count messages where:
        # 1. Thread involves me
        # 2. I am NOT the sender
        # 3. is_read is False
        count = Message.objects.filter(
            thread__first_user=request.user, is_read=False
        ).exclude(sender=request.user).count() + \
        Message.objects.filter(
            thread__second_user=request.user, is_read=False
        ).exclude(sender=request.user).count()
        
        return {'global_unread_count': count}
    return {'global_unread_count': 0}

