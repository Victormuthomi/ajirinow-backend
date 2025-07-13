from rest_framework import serializers
from .models import Job
from accounts.serializers import ClientMiniSerializer  # ✅ Nested client serializer

class JobSerializer(serializers.ModelSerializer):
    client = ClientMiniSerializer(read_only=True)  # ✅ Includes name & phone_number

    class Meta:
        model = Job
        fields = [
            'id',
            'client',
            'title',
            'description',
            'location',
            'is_active',
            'created_at',
        ]
        read_only_fields = ['id', 'client', 'created_at']

