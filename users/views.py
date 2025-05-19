from django.db.models import Count
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions
from rest_framework.exceptions import NotFound, NotAuthenticated
from rest_framework.generics import RetrieveUpdateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from reference.swagger_docs import (
    get_current_user_profile_doc,
    put_current_user_profile_doc,
    get_public_user_profile_doc
)
from startups.models import RequiredSpecialist
from .filters import SpecialistFilter, InvestorFilter
from .models import User, SpecialistProfile, InvestorProfile
from .serializers import (
    SpecialistProfileSerializer,
    FounderProfileSerializer,
    InvestorProfileSerializer, SpecialistCardSerializer, InvestorCardSerializer
)


class CurrentUserProfileView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'put']

    @method_decorator(get_current_user_profile_doc)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @method_decorator(put_current_user_profile_doc)
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    def get_serializer_class(self):
        user = self.request.user
        if user.is_authenticated:
            if user.role == User.Role.SPECIALIST:
                return SpecialistProfileSerializer
            elif user.role == User.Role.STARTUP:
                return FounderProfileSerializer
            elif user.role == User.Role.INVESTOR:
                return InvestorProfileSerializer
            raise NotFound('Профиль не найден')
        raise NotAuthenticated('Неавторизован')

    def get_object(self):
        user = self.request.user
        if user.is_authenticated:
            if user.role == User.Role.SPECIALIST:
                return user.specialist_profile
            elif user.role == User.Role.STARTUP:
                return user.founder_profile
            elif user.role == User.Role.INVESTOR:
                return user.investor_profile
            raise NotFound('Профиль не найден')
        raise NotAuthenticated('Неавторизован')


@method_decorator(get_public_user_profile_doc, name='get')
class PublicUserProfileView(RetrieveAPIView):
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        user = self.get_user()
        if user.role == User.Role.SPECIALIST:
            return SpecialistProfileSerializer
        elif user.role == User.Role.STARTUP:
            return FounderProfileSerializer
        elif user.role == User.Role.INVESTOR:
            return InvestorProfileSerializer
        raise NotFound('Профиль не найден')

    def get_object(self):
        user = self.get_user()
        if user.role == User.Role.SPECIALIST:
            return user.specialist_profile
        elif user.role == User.Role.STARTUP:
            return user.founder_profile
        elif user.role == User.Role.INVESTOR:
            return user.investor_profile
        raise NotFound('Профиль не найден')

    def get_user(self):
        try:
            return User.objects.get(pk=self.kwargs['id'])
        except User.DoesNotExist:
            raise NotFound('Пользователь не найден')


class SpecialistSearchView(generics.ListAPIView):
    queryset = SpecialistProfile.objects.select_related(
        'user', 'profession'
    ).prefetch_related(
        'skills', 'experiences'
    )
    serializer_class = SpecialistCardSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = SpecialistFilter

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class InvestorSearchView(generics.ListAPIView):
    queryset = InvestorProfile.objects.select_related('user', 'industry')
    serializer_class = InvestorCardSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = InvestorFilter

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class RecommendedSpecialistsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if not hasattr(user, 'founder_profile'):
            return Response([], status=204)

        founder = user.founder_profile
        limit = int(request.query_params.get('limit', 5))

        # Получаем все незанятые вакансии в стартапах основателя
        vacancies = RequiredSpecialist.objects.filter(
            startup__founder=founder,
            specialist__isnull=True
        ).select_related('profession').prefetch_related('skills')

        # Собираем нужные профессии и скиллы
        required_profession_ids = set()
        required_skill_ids = set()
        for vacancy in vacancies:
            required_profession_ids.add(vacancy.profession_id)
            required_skill_ids.update(
                vacancy.skills.values_list('id', flat=True)
            )

        # Базовый фильтр специалистов
        specialists = SpecialistProfile.objects.filter(
            profession_id__in=required_profession_ids,
            skills__id__in=required_skill_ids
        ).annotate(
            skill_matches=Count('skills')
        ).prefetch_related(
            'skills', 'experiences', 'user', 'profession'
        ).distinct()

        # Оцениваем опыт работы
        specialist_data = []
        for specialist in specialists:
            total_days = 0
            for exp in specialist.experiences.all():
                start = exp.start_date
                end = exp.end_date or now().date()
                total_days += (end - start).days

            experience_years = total_days / 365
            specialist_data.append((specialist, experience_years))

        # Сортируем по опыту (убывание)
        specialist_data.sort(key=lambda x: x[1], reverse=True)
        sorted_specialists = [s[0] for s in specialist_data[:limit]]

        # Сериализуем результат
        serializer = SpecialistCardSerializer(
            sorted_specialists,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)
