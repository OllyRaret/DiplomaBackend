from django.contrib import admin

from favorite.models import Favorite


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    ...
