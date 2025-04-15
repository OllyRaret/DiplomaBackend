from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from rest_framework.authentication import TokenAuthentication
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from users.views import CurrentUserProfileView, PublicUserProfileView

# Для swagger
schema_view = get_schema_view(
   openapi.Info(
      title="API для платформы стартапов",
      default_version='v1',
      description="Документация API",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
   authentication_classes=[],
)

urlpatterns = [
    path('admin/', admin.site.urls),

    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),

    path('profile/me/', CurrentUserProfileView.as_view(), name='user-profile'),
    path('profile/<int:id>/', PublicUserProfileView.as_view(), name='public-user-profile'),

    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
