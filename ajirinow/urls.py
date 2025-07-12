from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# 🔹 Swagger imports
from rest_framework.schemas import get_schema_view
from rest_framework.documentation import include_docs_urls
from drf_yasg.views import get_schema_view as get_yasg_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_yasg_view(
    openapi.Info(
        title="AjiriNow API",
        default_version="v1",
        description="API documentation for the AjiriNow platform",
        contact=openapi.Contact(email="support@ajirinow.co.ke"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # App routes
    path('api/accounts/', include('accounts.urls')),
    path('api/jobs/', include('jobs.urls')),
    path('api/ads/', include('ads.urls')),
    path('api/mpesa/', include('mpesa.urls')),
     path('api/payments/', include('payments.urls')),

    # 🔹 Swagger UI & ReDoc
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

