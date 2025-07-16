from django.db import models
from django.utils import timezone


class ProcessedMessage(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    original_message = models.TextField(help_text="The original message from the user")
    task_id = models.CharField(max_length=255, unique=True, help_text="Celery task ID")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now, help_text="When the task was created")
    processed_at = models.DateTimeField(null=True, blank=True, help_text="When processing completed")
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['task_id']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.original_message[:50]}... ({self.status})"
