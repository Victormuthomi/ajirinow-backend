from rest_framework import serializers
from .models import Ad

class AdSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.name', read_only=True)
    image_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Ad
        fields = [
            'id',
            'client',
            'client_name',
            'title',
            'description',
            'image',        # ✅ this enables uploads
            'image_url',    # ✅ this returns full URL
            'link',
            'is_active',
            'created_at',
            'expires_at'
        ]
        read_only_fields = ['client', 'created_at']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None

