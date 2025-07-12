from django.db import models
from django.utils import timezone
from datetime import timedelta
from accounts.models import User
from payments.models import Payment

class Job(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='jobs')
    title = models.CharField(max_length=100)
    description = models.TextField()
    location = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=False)  # initially inactive
    is_filled = models.BooleanField(default=False)
    payment = models.ForeignKey(Payment, null=True, blank=True, on_delete=models.SET_NULL)


    def activate(self):
        self.is_active = True
        self.expires_at = timezone.now() + timedelta(weeks=12)
        self.save()

    def save(self, *args, **kwargs):
        # Auto-deactivate if job is filled or expired
        if self.is_filled or (self.expires_at and self.expires_at < timezone.now()):
            self.is_active = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.client.name}"

