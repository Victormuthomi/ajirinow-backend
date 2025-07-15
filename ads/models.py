from django.db import models
from django.utils import timezone
from datetime import timedelta
from accounts.models import User
from payments.models import Payment
from cloudinary.models import CloudinaryField

# Define the upload path for ad images
def ad_image_upload_path(instance, filename):
    return f'ads/{instance.client.id}_{instance.client.name}/{filename}'

class Ad(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ads')
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = CloudinaryField('image', blank=False, null=False)

    link = models.URLField(
        blank=True,
        help_text="Optional link to a product or site"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=False)  # Initially inactive
    payment = models.ForeignKey(Payment, null=True, blank=True, on_delete=models.SET_NULL)

    def activate(self):
        """
        Activates the ad by setting is_active=True and setting expiry to 7 days from now.
        Should be called after successful payment.
        """
        self.is_active = True
        self.expires_at = timezone.now() + timedelta(days=7)
        self.save()

    def save(self, *args, **kwargs):
        # Automatically deactivate if expired
        if self.expires_at and self.expires_at < timezone.now():
            self.is_active = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Ad: {self.title} by {self.client.name}"

