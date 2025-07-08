from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("Phone number is required")
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(phone_number, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('fundi', 'Fundi'),
        ('client', 'Client'),
        ('advertiser', 'Advertiser'),
    ]

    phone_number = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=50)
    id_number = models.CharField(max_length=30)
    role = models.CharField(max_length=15, choices=ROLE_CHOICES)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    subscription_end = models.DateField(null=True, blank=True)  # ✅ Added

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['name', 'role']

    objects = UserManager()

    def __str__(self):
        return f"{self.name} ({self.role})"

class FundiProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='fundi_profile')
    skills = models.TextField()
    location = models.CharField(max_length=100)
    is_available = models.BooleanField(default=True)
    show_contact = models.BooleanField(default=True)
    rate_note = models.TextField(blank=True, help_text="e.g. Ksh 1500/day, negotiable")

    def __str__(self):
        return f"Fundi Profile: {self.user.name}"

class ClientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')
    role_note = models.CharField(max_length=100, blank=True, help_text="e.g. Contractor, Business Owner")

    def __str__(self):
        return f"Client Profile: {self.user.name}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == 'fundi' and not hasattr(instance, 'fundi_profile'):
            FundiProfile.objects.create(user=instance)
        elif instance.role == 'client' and not hasattr(instance, 'client_profile'):
            ClientProfile.objects.create(user=instance)

