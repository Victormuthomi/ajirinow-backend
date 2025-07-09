from rest_framework import generics, permissions
from .models import Ad
from .serializers import AdSerializer


class AdListCreateView(generics.ListCreateAPIView):
    """
    GET: List all active ads.

    POST: Create a new ad (authenticated users only).
    """
    queryset = Ad.objects.all()
    serializer_class = AdSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(client=self.request.user)


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

