from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include, re_path
from djoser.views import TokenCreateView

from .views import *
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from django.views.decorators.cache import cache_page



schema_view = get_schema_view(
    openapi.Info(
        title="API Documentation",
        default_version='v1',
    ),
    public=True,
)

urlpatterns = [
    path("api/v1/list/", cache_page(60)(ProductsAPIView.as_view()), name="home"),
    path("api/v1/search/", SearchAPI.as_view(), name="search"),
    path("api/v1/drf-auth/", include("rest_framework.urls")),
    path("api/v1/delete/", RemoveFromCartAPI.as_view(), name="delete"),
    path("api/v1/cart-list/", CartViewAPI.as_view()),
    path("api/v1/add-to-cart/", AddToCartAPI.as_view(), name="add"),
    path("api/v1/filters/", SearchFilterAPI.as_view(), name="filters"),
    path("api/v1/make-order/", MakeOrderAPI.as_view(), name="make-order"),
    path("api/v1/verify/", EmailVerify.as_view(), name="verify"),
    path("api/v1/auth/", include("djoser.urls")),
    re_path(r"^auth/", include("djoser.urls.authtoken")),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
