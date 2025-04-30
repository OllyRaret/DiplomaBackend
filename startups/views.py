from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from reference.permissions import IsFounderOrReadOnly, IsStartupFounder
from users.models import User
from .models import Startup
from .serializers import StartupSerializer


class StartupViewSet(viewsets.ModelViewSet):
    queryset = Startup.objects.all().select_related('founder__user', 'industry').prefetch_related('required_specialists__skills')
    serializer_class = StartupSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsFounderOrReadOnly]

    def perform_create(self, serializer):
        if not hasattr(self.request.user, 'founder_profile'):
            raise PermissionDenied('Только основатели могут создавать стартапы')
        serializer.save(founder=self.request.user.founder_profile)

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
            # Стартапы, созданные пользователем
            startups = Startup.objects.filter(founder=user.founder_profile)
            data = [
                {
                    'id': s.id,
                    'title': s.title,
                    'description': s.description,
                    'stage': s.stage,
                    'image': s.image.url if s.image else None,
                }
                for s in startups
            ]
            return Response(data)

        elif user.role == User.Role.SPECIALIST:
            # Стартапы, в которых он назначен
            startups = Startup.objects.filter(
                required_specialists__specialist=user.specialist_profile
            ).distinct()
            data = []
            for s in startups:
                specialist = s.required_specialists.filter(specialist=user.specialist_profile).first()
                role = specialist.profession.name if specialist else None
                data.append({
                    'id': s.id,
                    'title': s.title,
                    'role': role,
                    'description': s.description,
                    'stage': s.stage,
                    'image': s.image.url if s.image else None,
                })
            return Response(data)

        return Response([], status=204)
