# payments/urls.py
from django.urls import path
from .views import job_payment_status

urlpatterns = [
        path("job-status/", job_payment_status, name="job-status"),
        ]

