from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from accounts.models import User
from jobs.models import Job
from payments.models import Payment
from datetime import timedelta
from django.utils import timezone

class JobsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            phone_number="0712345678",
            name="Client",
            id_number="12345678",
            password="testpass123",
            role="client"
        )
        self.client.force_authenticate(user=self.user)

    def test_post_job_without_payment(self):
        job_data = {
            "title": "Test Job",
            "description": "Test description",
            "location": "Nairobi"
        }
        response = self.client.post("/api/jobs/", job_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        job = Job.objects.first()
        self.assertFalse(job.is_active)

    def test_activate_job_after_payment(self):
        job = Job.objects.create(
            client=self.user,
            title="Test Job",
            description="Some work",
            location="Nairobi",
            is_active=False
        )

        payment = Payment.objects.create(
            user=self.user,
            amount=100,
            purpose="post_job",
            status="Completed"
        )

        job.payment = payment
        job.is_active = True
        job.expires_at = timezone.now() + timedelta(weeks=12)
        job.save()

        refreshed_job = Job.objects.get(id=job.id)
        self.assertTrue(refreshed_job.is_active)
        self.assertIsNotNone(refreshed_job.expires_at)

    def test_job_list_authenticated_user(self):
        Job.objects.create(
            client=self.user,
            title="Another Job",
            description="Fix something",
            location="Mombasa",
            is_active=True
        )

        response = self.client.get("/api/jobs/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

