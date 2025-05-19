from django.db.models import F, Count
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from messaging.models import Invitation
from reference.permissions import IsFounderOrReadOnly, IsStartupFounder
from users.models import User
from .filters import (
    filter_startups_for_specialist,
    filter_startups_for_investor
)
from .models import Startup
from .serializers import (
    StartupSerializer, StartupForSpecialistSearchSerializer,
    StartupForInvestorSearchSerializer,
    StartupForFounderShortSerializer,
    StartupForSpecialistShortSerializer
)


class StartupViewSet(viewsets.ModelViewSet):
    queryset = Startup.objects.all().select_related(
        'founder__user', 'industry'
    ).prefetch_related('required_specialists__skills')
    serializer_class = StartupSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsFounderOrReadOnly
    ]

    def perform_create(self, serializer):
        if not hasattr(self.request.user, 'founder_profile'):
            raise PermissionDenied(
                'Только основатели могут создавать стартапы'
            )
        serializer.save(founder=self.request.user.founder_profile)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        # Увеличить просмотры, если пользователь не является основателем
        user = request.user
        if (
                user.is_authenticated
                and hasattr(user, 'founder_profile')
                and instance.founder != user.founder_profile
        ) or not user.is_authenticated:
            instance.views = F('views') + 1
            instance.save(update_fields=['views'])
            instance.refresh_from_db(fields=['views'])

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsFounderOrReadOnly()]
        elif self.action == 'create':
            return [permissions.IsAuthenticated(), IsStartupFounder()]
        return super().get_permissions()

    @action(detail=False, methods=['get'], url_path='my-startups')
    def my_startups(self, request):
        user = request.user

        if user.role == User.Role.STARTUP:
            queryset = Startup.objects.filter(founder=user.founder_profile)
            serializer = StartupForFounderShortSerializer(queryset, many=True)
            return Response(serializer.data)

        elif user.role == User.Role.SPECIALIST:
            queryset = Startup.objects.filter(
                required_specialists__specialist=user.specialist_profile
            ).distinct()
            serializer = StartupForSpecialistShortSerializer(
                queryset,
                many=True,
                context={'request': request}
            )
            return Response(serializer.data)

        return Response([], status=204)

    @action(detail=False, methods=['get'], url_path='new-startups')
    def new_startups(self, request):
        user = request.user

        if user.role != User.Role.SPECIALIST:
            return Response([], status=204)

        specialist = user.specialist_profile

        # Получаем все приглашения, на которые специалист не ответил
        pending_invitations = Invitation.objects.filter(
            specialist=specialist,
            is_accepted=None
        ).select_related('startup', 'required_specialist__profession')

        role_by_startup_id = {
            inv.startup.id: inv.required_specialist.profession.name
            for inv in pending_invitations
        }

        startups = [inv.startup for inv in pending_invitations]

        serializer = StartupForSpecialistShortSerializer(
            startups,
            many=True,
            context={'request': request, 'invited_roles': role_by_startup_id}
        )
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='search')
    def search_startups(self, request):
        user = request.user
        queryset = self.get_queryset()

        if user.role == User.Role.SPECIALIST:
            filtered = filter_startups_for_specialist(
                queryset,
                request.query_params
            )
            serializer = StartupForSpecialistSearchSerializer(
                filtered,
                many=True,
                context={'request': request}
            )
        elif user.role == User.Role.INVESTOR:
            filtered = filter_startups_for_investor(
                queryset,
                request.query_params
            )
            serializer = StartupForInvestorSearchSerializer(
                filtered,
                many=True,
                context={'request': request}
            )
        else:
            return Response({
                'detail':
                    'Только специалисты и инвесторы могут искать стартапы.'
            }, status=403)

        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='recommendations')
    def recommendations(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response({'detail': 'Требуется аутентификация'}, status=401)

        limit = request.query_params.get('limit')
        try:
            limit = int(limit)
        except (TypeError, ValueError):
            limit = 5  # значение по умолчанию

        queryset = Startup.objects.all().select_related(
            'founder__user', 'industry'
        ).prefetch_related(
            'required_specialists__skills'
        ).annotate(
            favorites_count=Count('favorited_by'),
        ).order_by('-favorites_count', '-views')  # популярные выше

        if user.role == User.Role.SPECIALIST:
            profile = user.specialist_profile
            skills = profile.skills.all()
            profession = profile.profession

            # Фильтруем по совпадению профессии и хотя бы одного навыка
            queryset = queryset.filter(
                required_specialists__profession=profession,
                required_specialists__skills__in=skills,
                required_specialists__specialist__isnull=True,
            ).distinct()[:limit]

            serializer = StartupForSpecialistSearchSerializer(
                queryset,
                many=True,
                context={'request': request}
            )
            return Response(serializer.data)

        elif user.role == User.Role.INVESTOR:
            profile = user.investor_profile
            industry = profile.industry
            stages = profile.preferred_stages
            min_inv = profile.investment_min
            max_inv = profile.investment_max

            queryset = queryset.filter(
                industry=industry,
                stage__in=stages,
                investment_needed__gte=min_inv,
                investment_needed__lte=max_inv
            )[:limit]

            serializer = StartupForInvestorSearchSerializer(
                queryset,
                many=True,
                context={'request': request}
            )
            return Response(serializer.data)

        return Response({
            'detail':
                'Только специалисты и инвесторы '
                'получают рекомендации стартапов.'
        }, status=403)
