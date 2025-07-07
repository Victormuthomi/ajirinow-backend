from rest_framework import serializers
from .models import User, FundiProfile, ClientProfile


class FundiProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = FundiProfile
        fields = ['skills', 'location', 'is_available', 'show_contact', 'rate_note']


class ClientProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientProfile
        fields = ['role_note']


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    fundi_profile = FundiProfileSerializer(required=False)
    client_profile = ClientProfileSerializer(required=False)

    class Meta:
        model = User
        fields = [
            'id', 'phone_number', 'name', 'id_number', 'role',
            'password', 'fundi_profile', 'client_profile'
        ]
        extra_kwargs = {
            'phone_number': {'required': False},
            'id_number': {'required': False},
            'role': {'required': False},
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        # Pop nested profile data
        client_profile_data = validated_data.pop('client_profile', None)
        fundi_profile_data = validated_data.pop('fundi_profile', None)

        # Update User fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if client_profile_data and hasattr(instance, 'client_profile'):
            for attr, value in client_profile_data.items():
                setattr(instance.client_profile, attr, value)
            instance.client_profile.save()

        if fundi_profile_data and hasattr(instance, 'fundi_profile'):
            for attr, value in fundi_profile_data.items():
                setattr(instance.fundi_profile, attr, value)
            instance.fundi_profile.save()

        instance.save()
        return instance

