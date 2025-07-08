from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from payments.models import Payment
from accounts.models import User
from datetime import timedelta
from django.utils import timezone

class PaymentTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            phone_number="0700000000",
            name="Test User",
            id_number="12345678",
            password="password",
            role="client"
        )
        self.client.force_authenticate(user=self.user)

    def test_create_payment_record(self):
        payment = Payment.objects.create(
            user=self.user,
            phone="254700000000",
            amount=500,
            merchant_request_id="mock-merchant-id",
            checkout_request_id="mock-checkout-id",
            status="Pending",
            purpose="post_job",
            description="Awaiting payment"
        )
        self.assertEqual(Payment.objects.count(), 1)
        self.assertEqual(payment.status, "Pending")

    def test_mark_payment_completed(self):
        payment = Payment.objects.create(
            user=self.user,
            phone="254700000000",
            amount=500,
            merchant_request_id="mock-merchant-id",
            checkout_request_id="mock-checkout-id",
            status="Pending",
            purpose="post_job"
        )
        payment.status = "Completed"
        payment.save()
        self.assertEqual(Payment.objects.get(id=payment.id).status, "Completed")

    def test_payment_related_to_job(self):
        from jobs.models import Job
        job = Job.objects.create(
            client=self.user,
            title="Test Job",
            description="Test job desc",
            is_active=False
        )

        payment = Payment.objects.create(
            user=self.user,
            phone="254700000000",
            amount=100,
            merchant_request_id="mock-merchant-id",
            checkout_request_id="mock-checkout-id",
            status="Completed",
            purpose="post_job"
        )

        job.payment = payment
        job.is_active = True
        job.save()

        self.assertEqual(job.payment, payment)
        self.assertTrue(job.is_active)

