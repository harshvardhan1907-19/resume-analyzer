from django.contrib import admin
from .models import Resume

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('filename', 'user', 'status', 'file_size', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('filename', 'user__username')
    readonly_fields = ('filename', 'file_size', 'created_at', 'updated_at')