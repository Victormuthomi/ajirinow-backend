from django.urls import path
from .views import STKPushView, mpesa_callback

urlpatterns = [
    path('stkpush/', STKPushView.as_view(), name='stkpush'),
    path('callback/', mpesa_callback, name='stk_callback'),
]

