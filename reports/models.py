from django.db import models
from django.conf import settings

# Common choices for reasons (you can split these if you want specific reasons for users vs posts)
REPORT_REASONS = [
    ('spam', 'Spam'),
    ('inappropriate', 'Inappropriate Content'),
    ('harassment', 'Harassment or Bullying'),
    ('scam', 'Scam or Fraud'),
    ('false_info', 'False Information'),
    ('other', 'Other'),
]

STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('reviewed', 'Reviewed'),
    ('resolved', 'Resolved'),
    ('dismissed', 'Dismissed'),
]

class PostReport(models.Model):
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='post_reports_filed', on_delete=models.CASCADE)
    post = models.ForeignKey('posts.Post', related_name='reports', on_delete=models.CASCADE)
    
    reason = models.CharField(max_length=20, choices=REPORT_REASONS)
    description = models.TextField(blank=True, null=True, help_text="Optional details")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Post Report {self.pk} by {self.reporter.username}"

    class Meta:
        db_table = 'reports_post'

class UserReport(models.Model):
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='user_reports_filed', on_delete=models.CASCADE)
    reported_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='reports_received', on_delete=models.CASCADE)
    
    reason = models.CharField(max_length=20, choices=REPORT_REASONS)
    description = models.TextField(blank=True, null=True, help_text="Optional details")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"User Report {self.pk} by {self.reporter.username}"

    class Meta:
        db_table = 'reports_user'