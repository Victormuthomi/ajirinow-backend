# payments/urls.py
from django.urls import path
from .views import job_payment_status, ad_payment_status

urlpatterns = [
        path("job-status/", job_payment_status, name="job-status"),
        path('payments/ad-status/', ad_payment_status),

        ]

