# resumes/serializers.py
from rest_framework import serializers
from .models import Resume

class ResumeSerializer(serializers.ModelSerializer):
    """
    Serializer for Resume model with additional fields
    """
    file_size_kb = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Resume
        fields = [
            'id', 'filename', 'file', 'file_size', 'file_size_kb',
            'content', 'analysis', 'status', 'status_display',
            'error_message', 'created_at', 'updated_at', 'analyzed_at'
        ]
        read_only_fields = [
            'id', 'filename', 'file_size', 'content', 'analysis',
            'status', 'error_message', 'created_at', 'updated_at', 'analyzed_at'
        ]
    
    def get_file_size_kb(self, obj):
        if obj.file_size:
            return f"{obj.file_size / 1024:.1f} KB"
        return None

class ResumeUploadSerializer(serializers.ModelSerializer):
    """
    Serializer for uploading resumes
    """
    class Meta:
        model = Resume
        fields = ['id', 'file', 'filename', 'created_at']
        read_only_fields = ['id', 'filename', 'created_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)