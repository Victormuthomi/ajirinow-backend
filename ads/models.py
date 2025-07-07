from django.db import models
from accounts.models import User

# Move this outside the model
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

    def __str__(self):
        return f"Ad: {self.title} by {self.client.name}"

