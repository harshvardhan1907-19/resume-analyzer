import os
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

def validate_file_extension(value):
    """
    Validate that uploaded file is a PDF
    """
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.pdf']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Only PDF files are allowed.')

class Resume(models.Model):
    """
    Model to store uploaded resumes
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='resumes'
    )
    file = models.FileField(
        upload_to='resumes/%Y/%m/%d/',
        validators=[validate_file_extension]
    )
    filename = models.CharField(max_length=255)
    file_size = models.IntegerField(help_text='File size in bytes')
    content = models.TextField(blank=True, help_text='Extracted text from PDF')
    analysis = models.TextField(blank=True, help_text='AI analysis result')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    analyzed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.filename} - {self.user.username}"
    
    def save(self, *args, **kwargs):
        if not self.filename and self.file:
            self.filename = self.file.name
        if not self.file_size and self.file:
            self.file_size = self.file.size
        super().save(*args, **kwargs)

def validate_file_size(value):
    """
    Validate file size doesn't exceed 5MB
    """
    max_size = 5 * 1024 * 1024  # 5MB
    if value.size > max_size:
        raise ValidationError(f'File size exceeds 5MB limit.')

# Update the file field in Resume model:
file = models.FileField(
    upload_to='resumes/%Y/%m/%d/',
    validators=[validate_file_extension, validate_file_size]
)