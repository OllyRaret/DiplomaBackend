from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.routers import DefaultRouter

from favorite.views import FavoriteViewSet
from messaging.views import MessageViewSet, InvitationViewSet
from reference.views import ProfessionListView, IndustryListView, SkillListView
from startups.views import StartupViewSet
from users.views import (
    CurrentUserProfileView, PublicUserProfileView,
    SpecialistSearchView, InvestorSearchView,
    RecommendedSpecialistsView
)

# Для swagger
schema_view = get_schema_view(
   openapi.Info(
      title='API для платформы стартапов',
      default_version='v1',
      description='Документация API',
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
   authentication_classes=[],
)

router = DefaultRouter()
router.register(r'messages', MessageViewSet, basename='messages')
router.register(r'startups', StartupViewSet, basename='startup')
router.register(r'favorites', FavoriteViewSet, basename='favorites')
router.register(r'invitations', InvitationViewSet, basename='invitations')

urlpatterns = [
    path('admin/', admin.site.urls),

    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),

    path('profile/me/', CurrentUserProfileView.as_view(), name='user-profile'),
    path(
        'profile/<int:id>/',
        PublicUserProfileView.as_view(),
        name='public-user-profile'
    ),

    path('professions/', ProfessionListView.as_view(), name='profession-list'),
    path('skills/', SkillListView.as_view(), name='skill-list'),
    path('industries/', IndustryListView.as_view(), name='industry-list'),

    path(
        'search/specialists/',
        SpecialistSearchView.as_view(),
        name='specialist-search'
    ),
    path(
        'search/investors/',
        InvestorSearchView.as_view(),
        name='investor-search'
    ),

    path(
        'specialists/recommendations/',
        RecommendedSpecialistsView.as_view(),
        name='specialist-recommendations'
    ),

    path('', include(router.urls)),

    path(
        'swagger/',
        schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui'
    ),
    path(
        'redoc/',
        schema_view.with_ui('redoc', cache_timeout=0),
        name='schema-redoc'
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
