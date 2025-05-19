from django.contrib import admin
from .models import Startup, RequiredSpecialist


class RequiredSpecialistInline(admin.TabularInline):
    model = RequiredSpecialist
    extra = 1
    verbose_name = 'Требуемый специалист'
    verbose_name_plural = 'Требуемые специалисты'


@admin.register(Startup)
class StartupAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'founder', 'industry',
        'stage', 'investment_needed', 'views'
    )
    search_fields = ('title', 'description', 'founder__user__full_name')
    list_filter = ('industry', 'stage')
    inlines = [RequiredSpecialistInline]
