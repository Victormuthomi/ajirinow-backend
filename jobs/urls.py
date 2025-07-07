from django.urls import path
from .views import JobListCreateView, MyJobListView, JobRetrieveUpdateDeleteView

urlpatterns = [
    path('', JobListCreateView.as_view(), name='job-list-create'),
    path('mine/', MyJobListView.as_view(), name='my-jobs'),
    path('<int:pk>/', JobRetrieveUpdateDeleteView.as_view(), name='job-detail'),
]

