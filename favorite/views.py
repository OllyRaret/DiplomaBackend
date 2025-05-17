from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from favorite.models import Favorite
from favorite.serializers import FavoriteCreateSerializer
from startups.serializers import StartupForSpecialistSearchSerializer, StartupForInvestorSearchSerializer
from users.models import User
from users.serializers import SpecialistCardSerializer, InvestorCardSerializer


class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def specialists(self, request):
        favorites = self.get_queryset().filter(specialist__isnull=False).select_related(
            'specialist__user', 'specialist__profession'
        ).prefetch_related('specialist__skills')

        serializer = SpecialistCardSerializer(
            [f.specialist for f in favorites],
            many=True,
            context={'request': request}
        )

        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def investors(self, request):
        favorites = self.get_queryset().filter(investor__isnull=False).select_related(
            'investor__user', 'investor__industry'
        )

        serializer = InvestorCardSerializer(
            [f.investor for f in favorites],
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def startup_for_specialist(self, request):
        if request.user.role != User.Role.SPECIALIST and request.user.role != User.Role.STARTUP:
            return Response({'detail': 'Доступно только для специалистов и основателей стартапов.'}, status=403)
        favorites = self.get_queryset().filter(startup__isnull=False).select_related('startup__industry', 'startup__founder__user').prefetch_related('startup__required_specialists__profession')
        serializer = StartupForSpecialistSearchSerializer(
            [f.startup for f in favorites],
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def startup_for_investor(self, request):
        if request.user.role != User.Role.INVESTOR:
            return Response({'detail': 'Доступно только для инвесторов.'}, status=403)
        favorites = self.get_queryset().filter(startup__isnull=False).select_related('startup__industry', 'startup__founder__user')
        serializer = StartupForInvestorSearchSerializer(
            [f.startup for f in favorites],
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)

    @action(detail=False, methods=['delete'])
    def remove(self, request):
        user = request.user
        specialist_id = request.data.get('specialist_id')
        investor_id = request.data.get('investor_id')
        startup_id = request.data.get('startup_id')

        if specialist_id:
            favorite = Favorite.objects.filter(user=user, specialist_id=specialist_id).first()
        elif investor_id:
            favorite = Favorite.objects.filter(user=user, investor_id=investor_id).first()
        elif startup_id:
            favorite = Favorite.objects.filter(user=user, startup_id=startup_id).first()
        else:
            return Response({'detail': 'Укажите хотя бы одно из полей: specialist_id, investor_id или startup_id'}, status=400)

        if not favorite:
            return Response({'detail': 'Избранное не найдено.'}, status=404)

        favorite.delete()
        return Response(status=204)
