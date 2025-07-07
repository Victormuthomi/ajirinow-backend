from django.urls import path
from .views import AdListCreateView, AdDetailView, MyAdsView

urlpatterns = [
    path('', AdListCreateView.as_view(), name='ad-list-create'),
    path('mine/', MyAdsView.as_view(), name='my-ads'),
    path('<int:pk>/', AdDetailView.as_view(), name='ad-detail'),
]

