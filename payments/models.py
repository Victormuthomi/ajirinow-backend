from django.db import models
from accounts.models import User
from django.utils import timezone
from datetime import timedelta

class Payment(models.Model):
    PURPOSE_CHOICES = [
        ('subscription', 'Subscription'),
        ('post_job', 'Post Job'),
        ('post_ad', 'Post Ad'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    merchant_request_id = models.CharField(max_length=100)
    checkout_request_id = models.CharField(max_length=100)
    status = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    post_expiry_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.name} - {self.purpose} - {self.status}"

    def save(self, *args, **kwargs):
        if not self.pk:
            if self.purpose == "subscription":
                self.amount = 200
            elif self.purpose == "post_job":
                self.amount = 100
            elif self.purpose == "post_ad":
                self.amount = 500

        if self.status == "Completed":
            if self.purpose == "subscription" and self.user.role == "fundi":
                self.user.subscription_end = timezone.now().date() + timedelta(days=30)
                # Don't try to set self.user.is_subscribed — it's a @property
                self.user.save()
            elif self.purpose == "post_job":
                self.post_expiry_date = timezone.now().date() + timedelta(weeks=12)
            elif self.purpose == "post_ad":
                self.post_expiry_date = timezone.now().date() + timedelta(weeks=1)

        super().save(*args, **kwargs)

