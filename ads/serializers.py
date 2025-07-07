from rest_framework import serializers
from .models import Ad

class AdSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.name', read_only=True)

    class Meta:
        model = Ad
        fields = [
            'id',
            'client',
            'client_name',
            'title',
            'description',
            'image',
            'link',
            'created_at',
            'expires_at'
        ]
        read_only_fields = ['client', 'created_at']

