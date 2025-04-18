from django.utils.decorators import method_decorator
from rest_framework.exceptions import NotFound, NotAuthenticated
from rest_framework.generics import RetrieveUpdateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny

from reference.swagger_docs import get_current_user_profile_doc, put_current_user_profile_doc, \
    get_public_user_profile_doc
from .models import User
from .serializers import (
    SpecialistProfileSerializer,
    FounderProfileSerializer,
    InvestorProfileSerializer
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
            raise NotFound("Профиль не найден")
        raise NotAuthenticated("Неавторизован")

    def get_object(self):
        user = self.request.user
        if user.is_authenticated:
            if user.role == User.Role.SPECIALIST:
                return user.specialist_profile
            elif user.role == User.Role.STARTUP:
                return user.founder_profile
            elif user.role == User.Role.INVESTOR:
                return user.investor_profile
            raise NotFound("Профиль не найден")
        raise NotAuthenticated("Неавторизован")


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
        raise NotFound("Профиль не найден")

    def get_object(self):
        user = self.get_user()
        if user.role == User.Role.SPECIALIST:
            return user.specialist_profile
        elif user.role == User.Role.STARTUP:
            return user.founder_profile
        elif user.role == User.Role.INVESTOR:
            return user.investor_profile
        raise NotFound("Профиль не найден")

    def get_user(self):
        try:
            return User.objects.get(pk=self.kwargs['id'])
        except User.DoesNotExist:
            raise NotFound("Пользователь не найден")
