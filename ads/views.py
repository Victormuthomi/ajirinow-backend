from rest_framework import generics, permissions
from .models import Ad
from .serializers import AdSerializer


from django.utils import timezone

class AdListCreateView(generics.ListCreateAPIView):
    queryset = Ad.objects.all()
    serializer_class = AdSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        # Deactivate expired ads before returning
        expired_ads = Ad.objects.filter(is_active=True, expires_at__lt=timezone.now())
        for ad in expired_ads:
            ad.is_active = False
            ad.save()

        return Ad.objects.filter(is_active=True)

    def perform_create(self, serializer):
        serializer.save(client=self.request.user)

    def get_serializer_context(self):
        return {'request': self.request}


class MyAdsView(generics.ListAPIView):
    """
    GET: List ads posted by the authenticated user.
    """
    serializer_class = AdSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Ad.objects.none()
        return Ad.objects.filter(client=self.request.user)

    def get_serializer_context(self):
        return {'request': self.request}


class AdDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: View a single ad.
    PUT/PATCH/DELETE: Update or delete an ad (only by owner).
    """
    serializer_class = AdSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Ad.objects.none()
        return Ad.objects.filter(client=self.request.user)

    def get_serializer_context(self):
        return {'request': self.request}

