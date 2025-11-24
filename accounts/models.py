from datetime import datetime
from django.contrib.auth.models import AbstractUser
from django.db import models
import os

def profile_image_path(instance, filename):
    # Get the file extension (e.g., .jpg, .png)
    ext = filename.split('.')[-1]
    # Generate timestamp: profile_pic_20251023123059
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    new_filename = f"profile_pic_{timestamp}.{ext}"
    # Return the full path: profiles/profile_pic_2025...
    return os.path.join('profiles/', new_filename)

class User(AbstractUser):
    profile_image = models.ImageField(upload_to=profile_image_path, blank=True, null=True)
    bio = models.TextField(null=True, blank=True)
    role = models.CharField(max_length=10, choices=[('user', 'User'), ('admin', 'Admin')], default='user')
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)
    last_seen = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'users'