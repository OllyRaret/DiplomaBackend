from django.contrib import admin

from .forms import InvestorProfileForm
from .models import WorkExperience, InvestorPreviousInvestment, User, SpecialistProfile, FounderProfile, InvestorProfile


class WorkExperienceInline(admin.TabularInline):
    model = WorkExperience
    extra = 1
    fields = ('organization', 'position', 'start_date', 'end_date', 'description')
    show_change_link = True


class PreviousInvestmentInline(admin.TabularInline):
    model = InvestorPreviousInvestment
    extra = 1
    fields = ('title', 'industry', 'stage', 'date', 'description')
    show_change_link = True


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'role')
    list_filter = ('role',)
    search_fields = ('email', 'full_name')


@admin.register(SpecialistProfile)
class SpecialistProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'profession')
    filter_horizontal = ('skills',)
    inlines = [WorkExperienceInline]


@admin.register(FounderProfile)
class FounderProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'industry')
    inlines = [WorkExperienceInline]


@admin.register(InvestorProfile)
class InvestorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'position')
    list_filter = ('industry',)
    form = InvestorProfileForm
    inlines = [PreviousInvestmentInline]
