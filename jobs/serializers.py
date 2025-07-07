from rest_framework import serializers
from .models import Job

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ['id', 'client', 'title', 'description', 'location', 'is_active', 'created_at']
        read_only_fields = ['id', 'client', 'created_at']

