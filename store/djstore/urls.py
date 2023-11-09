from django.urls import path, include, re_path
from .views import *

urlpatterns = [
    path("api/v1/list/", ProductsAPIView.as_view(), name="home"),
    path("api/v1/drf-auth/", include("rest_framework.urls")),
    path("api/v1/auth/", include("djoser.urls")),
    re_path(r"^auth/", include("djoser.urls.authtoken")),
]
