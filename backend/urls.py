from django.contrib import admin
from django.urls import path, include

from users.views import CurrentUserProfileView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('profile/me/', CurrentUserProfileView.as_view(), name='user-profile'),
]
