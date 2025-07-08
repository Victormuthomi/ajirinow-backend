from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import User
from payments.models import Payment
from ads.models import Ad
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from datetime import timedelta

class AdsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            phone_number="0700111222",
            name="Ad Poster",
            id_number="11112222",
            password="adpass123",
            role="advertiser"
        )
        self.token = self.client.post("/api/accounts/login/", {
            "phone_number": "0700111222",
            "password": "adpass123"
        }).data["token"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token}")

    def test_post_ad_fails_without_payment(self):
        image = SimpleUploadedFile("ad.jpg", b"file_content", content_type="image/jpeg")
        response = self.client.post("/api/ads/", {
            "title": "No Pay Ad",
            "description": "Test description",
            "image": image
        }, format="multipart")
        self.assertEqual(response.status_code, 400)

    #def test_post_ad_success_with_payment(self):
        # Step 1: Try posting an ad without payment (should fail)
      #  image = SimpleUploadedFile("ad.jpg", b"file_content", content_type="image/jpeg")
        #response = self.client.post("/api/ads/", {
       #     "title": "Pending Ad",
     #       "description": "Awaiting payment",
     #       "image": image
    #    }, format="multipart")
   #     self.assertEqual(response.status_code, 400)
#
        # Step 2: Simulate payment
     #   Payment.objects.create(
    #        user=self.user,
 #           amount=500,
       #     purpose="post_ad",
  #          status="Completed"
     #   )

        # Step 3: Retry posting the ad
     #   image = SimpleUploadedFile("paid_ad.jpg", b"file_content", content_type="image/jpeg")
    #    response = self.client.post("/api/ads/", {
   #         "title": "Paid Ad",
        #    "description": "Test paid ad",
    #        "image": image
      #  }, format="multipart")

     #   self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#
     #   ad = Ad.objects.last()
      #  self.assertTrue(ad.is_active)
       # self.assertIsNotNone(ad.expires_at)

    def test_ad_auto_expiry(self):
        ad = Ad.objects.create(
            client=self.user,
            title="Old Ad",
            description="Should expire",
            is_active=True,
            expires_at=timezone.now() - timedelta(days=1)
        )
        ad.refresh_from_db()
        self.assertFalse(ad.is_active)

