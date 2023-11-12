from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include, re_path
from .views import *
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

schema_view = get_schema_view(
    openapi.Info(
        title="API Documentation",
        default_version='v1',
    ),
    public=True,
)

urlpatterns = [
    path("api/v1/list/", ProductsAPIView.as_view(), name="home"),
    path("api/v1/search/", SearchAPI.as_view(), name="search"),
    path("api/v1/drf-auth/", include("rest_framework.urls")),
    path("api/v1/delete/", RemoveFromCartAPI.as_view(), name="delete"),
    path("api/v1/auth/", include("djoser.urls")),
    re_path(r"^auth/", include("djoser.urls.authtoken")),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
