from datetime import timedelta
from django.utils import timezone
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from .models import Job
from .serializers import JobSerializer
from payments.models import Payment

class JobListCreateView(generics.ListCreateAPIView):
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role in ['client', 'advertiser']:
            return Job.objects.filter(client=user).order_by('-created_at')

        if user.role == 'fundi':
            in_trial = (timezone.now() - user.date_joined) <= timedelta(days=7)

            latest_payment = Payment.objects.filter(
                user=user,
                purpose='subscription',
                status='Completed'
            ).order_by('-created_at').first()

            has_active_subscription = (
                latest_payment and
                latest_payment.created_at >= timezone.now() - timedelta(days=30)
            )

            if not in_trial and not has_active_subscription:
                raise PermissionDenied("Subscription required to view jobs.")

            return Job.objects.filter(is_active=True).order_by('-created_at')

        return Job.objects.none()

    def perform_create(self, serializer):
        serializer.save(client=self.request.user)  # will be inactive until paid


class MyJobListView(generics.ListAPIView):
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Job.objects.filter(client=self.request.user).order_by('-created_at')


class JobRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        serializer.save(client=self.request.user)

