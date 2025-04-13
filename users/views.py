from rest_framework.exceptions import NotFound
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated

from .models import User
from .serializers import (
    SpecialistProfileSerializer,
    FounderProfileSerializer,
    InvestorProfileSerializer
)


class UserProfileView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        user = self.request.user
        if user.role == User.Role.SPECIALIST:
            return SpecialistProfileSerializer
        elif user.role == User.Role.STARTUP:
            return FounderProfileSerializer
        elif user.role == User.Role.INVESTOR:
            return InvestorProfileSerializer
        raise NotFound("Профиль не найден")

    def get_object(self):
        user = self.request.user
        if user.role == User.Role.SPECIALIST:
            return user.specialist_profile
        elif user.role == User.Role.STARTUP:
            return user.founder_profile
        elif user.role == User.Role.INVESTOR:
            return user.investor_profile
        raise NotFound("Профиль не найден")
