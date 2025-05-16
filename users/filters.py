from django.db.models import Q
from django.utils.timezone import now
from django_filters import rest_framework as filters

from users.models import SpecialistProfile, InvestorProfile


class SpecialistFilter(filters.FilterSet):
    profession = filters.NumberFilter(field_name='profession__id')
    skills = filters.BaseInFilter(field_name='skills__id')
    min_experience_years = filters.NumberFilter(method='filter_by_experience')

    class Meta:
        model = SpecialistProfile
        fields = ['profession', 'skills']

    def filter_by_experience(self, queryset, name, value):

        # Фильтруем специалистов, у которых суммарный опыт >= value лет
        specialists = []
        for specialist in queryset.prefetch_related('experiences'):
            total_days = 0
            for exp in specialist.experiences.all():
                start = exp.start_date
                end = exp.end_date or now().date()
                total_days += (end - start).days

            total_years = total_days / 365
            if total_years >= value:
                specialists.append(specialist.pk)

        return queryset.filter(pk__in=specialists)


class InvestorFilter(filters.FilterSet):
    investment_min = filters.NumberFilter(field_name='investment_min', lookup_expr='lte')
    investment_max = filters.NumberFilter(field_name='investment_max', lookup_expr='gte')
    industry = filters.NumberFilter(field_name='industry')
    preferred_stages = filters.CharFilter(method='filter_by_stage')

    class Meta:
        model = InvestorProfile
        fields = ['industry', 'preferred_stages', 'investment_min', 'investment_max']

    def filter_by_stage(self, queryset, name, value):
        """
        value может быть одной стадией или через запятую: 'launch,in_progress'
        """
        stages = value.split(',')
        return queryset.filter(preferred_stages__icontains=stages[0]) if len(stages) == 1 else queryset.filter(
            *(Q(preferred_stages__icontains=stage) for stage in stages)
        )
