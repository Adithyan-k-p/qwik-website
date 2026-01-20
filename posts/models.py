from typing import Any
from django.db import models
from django.utils import timezone
from datetime import timedelta
from accounts.models import User
import os
import uuid

def qwip_file_name(instance, filename):
    # Get the file extension (e.g., .jpg, .png)
    ext = filename.split('.')[-1]
    
    # Generate a unique filename
    # Format: qwip_YYYYMMDD_UUID(first 8 chars).ext
    # Example: qwip_20231025_a1b2c3d4.jpg
    current_time = timezone.now().strftime("%Y%m%d")
    unique_id = uuid.uuid4().hex[:8]
    new_filename = f"qwip_{current_time}_{unique_id}.{ext}"
    
    # Return the full path: qwips/new_filename.jpg
    return os.path.join('qwips', new_filename)

class Post(models.Model):
    MEDIA_TYPE_CHOICES = [('image', 'Image'), ('video', 'Video'), ('text', 'Text')]
    POST_TYPE_CHOICES = [('temporary', 'Temporary'), ('permanent', 'Permanent')]
    
    VISIBILITY_CHOICES = [('public', 'Public'), ('private', 'Friends Only')]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    caption = models.TextField()
    image = models.ImageField(upload_to=qwip_file_name, null=True, blank=True)
    
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES, default='image')
    post_type = models.CharField(max_length=15, choices=POST_TYPE_CHOICES, default='temporary')
    
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='public')
    is_archived = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.post_type == 'temporary' and not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)
            
        if self.post_type == 'permanent':
            self.expires_at = None

        if self.expires_at and self.expires_at < timezone.now():
            self.is_active = False
            
        super().save(*args, **kwargs)

    likes: Any 
    comments: Any

    def __str__(self):
        return f"{self.user.username}'s Qwip"
        # return f"{self.user.username}'s Qwip ({self.visibility})"

    class Meta:
        db_table = 'posts'

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='likes', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # A user can only like a post once
        unique_together = ('user', 'post')

    def __str__(self):
        return f"{self.user.username} liked {self.post.pk}"

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} on {self.post.pk}"