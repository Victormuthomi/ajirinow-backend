from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import User
from payments.models import Payment
from datetime import timedelta
from django.utils import timezone

class AccountsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.fundi_data = {
            "phone_number": "0712345678",
            "name": "Fundi User",
            "id_number": "12345678",
            "password": "testpass123",
            "role": "fundi"
        }
        self.client_data = {
            "phone_number": "0700000001",
            "name": "Client User",
            "id_number": "87654321",
            "password": "testpass123",
            "role": "client"
        }

    def test_register_fundi(self):
        response = self.client.post("/api/accounts/register/", self.fundi_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)

    def test_login_fundi(self):
        self.client.post("/api/accounts/register/", self.fundi_data, format="json")
        response = self.client.post("/api/accounts/login/", {
            "phone_number": self.fundi_data["phone_number"],
            "password": self.fundi_data["password"]
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)

    def test_profile_created_on_register(self):
        self.client.post("/api/accounts/register/", self.fundi_data, format="json")
        user = User.objects.first()
        self.assertIsNotNone(user.fundi_profile)

    def test_public_fundi_list_shows_trial_user(self):
        self.client.post("/api/accounts/register/", self.fundi_data, format="json")
        response = self.client.get("/api/accounts/fundis/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_public_fundi_list_after_payment(self):
        self.client.post("/api/accounts/register/", self.fundi_data, format="json")
        user = User.objects.first()
        user.date_joined = timezone.now() - timedelta(days=10)  # past trial
        user.save()

        payment = Payment.objects.create(
            user=user,
            amount=200,
            purpose="subscription",
            status="Completed"
        )
        payment.created_at = timezone.now() - timedelta(days=5)
        payment.save()

        response = self.client.get("/api/accounts/fundis/")
        self.assertEqual(len(response.data), 1)

    def test_public_fundi_hidden_after_expired_subscription(self):
        self.client.post("/api/accounts/register/", self.fundi_data, format="json")
        user = User.objects.first()
        user.date_joined = timezone.now() - timedelta(days=40)
        user.save()

        payment = Payment.objects.create(
            user=user,
            amount=200,
            purpose="subscription",
            status="Completed"
        )
        payment.created_at = timezone.now() - timedelta(days=31)
        payment.save()

        response = self.client.get("/api/accounts/fundis/")
        self.assertEqual(len(response.data), 0)

