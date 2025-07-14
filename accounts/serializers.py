from rest_framework import serializers
from .models import User, FundiProfile, ClientProfile


class FundiProfileSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="user.name", read_only=True)
    id_number = serializers.CharField(source="user.id_number", read_only=True)
    is_active = serializers.BooleanField(source="user.is_active", read_only=True)
    phone_number = serializers.CharField(source="user.phone_number", read_only=True)

    # ✅ Trial-related fields
    on_trial = serializers.SerializerMethodField()
    trial_ends = serializers.DateTimeField(source="user.trial_ends", read_only=True)

    # ✅ Subscription-related fields (directly from DB, not recomputed)
    is_subscribed = serializers.SerializerMethodField()
    subscription_end = serializers.DateField(source="user.subscription_end", read_only=True)

    class Meta:
        model = FundiProfile
        fields = [
            'skills',
            'location',
            'is_available',
            'show_contact',
            'rate_note',
            'name',
            'id_number',
            'phone_number',
            'is_active',
            'on_trial',
            'trial_ends',
            'is_subscribed',
            'subscription_end',
        ]

    def get_on_trial(self, obj):
        return obj.user.is_on_trial

    def get_is_subscribed(self, obj):
        return obj.user.is_subscribed


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
            'id',
            'phone_number',
            'name',
            'id_number',
            'role',
            'password',
            'fundi_profile',
            'client_profile',
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
        client_profile_data = validated_data.pop('client_profile', None)
        fundi_profile_data = validated_data.pop('fundi_profile', None)

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


class ClientMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['name', 'phone_number']

