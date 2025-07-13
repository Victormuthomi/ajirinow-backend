from django.db import models
from accounts.models import User
from django.utils import timezone
from datetime import timedelta
from payments.models import Payment

# Define the upload path for ad images
def ad_image_upload_path(instance, filename):
    return f'ads/{instance.client.id}_{instance.client.name}/{filename}'

class Ad(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ads')
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(
        upload_to=ad_image_upload_path,
        blank=True,
        null=True,
        help_text="Optional image file (JPG, PNG, etc.)"
    )
    link = models.URLField(blank=True, help_text="Optional link to a product or site")
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=False)  # Changed to False by default

    payment = models.ForeignKey(Payment, null=True, blank=True, on_delete=models.SET_NULL)

    def save(self, *args, **kwargs):
        # Automatically deactivate if expired
        if self.expires_at and self.expires_at < timezone.now():
            self.is_active = False

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Ad: {self.title} by {self.client.name}"

