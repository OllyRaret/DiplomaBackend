from django.contrib import admin
from django.urls import path, include

from users.views import UserProfileView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('profile/me/', UserProfileView.as_view(), name='user-profile'),
]
