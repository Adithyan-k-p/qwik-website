from django.db import models
from accounts.models import User
from posts.models import Post
from typing import Any

class Thread(models.Model):
    first_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='thread_first')
    second_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='thread_second')
    updated_at = models.DateTimeField(auto_now=True)

    # TYPE HINTS: This tells the linter these attributes exist
    pk: int
    first_user_id: int
    second_user_id: int
    messages: Any  # This represents the reverse manager from Message model

    class Meta:
        unique_together = ('first_user', 'second_user')

    def __str__(self):
        return f"Thread {self.pk}"

class Message(models.Model):
    # The related_name='messages' is what creates the attribute on the Thread model
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    pk: int
    sender_id: int