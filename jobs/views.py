from datetime import timedelta
from django.utils import timezone
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied

from .models import Job
from .serializers import JobSerializer


class JobListCreateView(generics.ListCreateAPIView):
    """
    GET:
    - Fundis (with active subscription or trial): View all active jobs.
    - Clients/Advertisers: View all active jobs.

    POST:
    - Clients/Advertisers: Create a job. Job will be inactive until payment is made.
    """
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role in ['client', 'advertiser']:
            return Job.objects.filter(is_active=True).order_by('-created_at')

        if user.role == 'fundi':
            if not user.is_on_trial and not user.is_subscribed:
                raise PermissionDenied("Subscription required to view jobs.")
            return Job.objects.filter(is_active=True).order_by('-created_at')

        return Job.objects.none()

    def perform_create(self, serializer):
        serializer.save(client=self.request.user)


class MyJobListView(generics.ListAPIView):
    """
    GET:
    - List jobs posted by the logged-in user (client or advertiser).
    """
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Job.objects.filter(client=self.request.user).order_by('-created_at')


class JobRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET:
    - View specific job by ID.

    PUT/PATCH:
    - Update a job (only if you are the owner).

    DELETE:
    - Delete a job (only if you are the owner).
    """
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        serializer.save(client=self.request.user)

