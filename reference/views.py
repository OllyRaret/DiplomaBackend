from rest_framework import generics
from .models import Profession, Skill, Industry
from .serializers import (
    ProfessionSerializer, SkillSerializer,
    IndustrySerializer
)


class ProfessionListView(generics.ListAPIView):
    """ Получить список профессий из БД """
    queryset = Profession.objects.all()
    serializer_class = ProfessionSerializer


class SkillListView(generics.ListAPIView):
    """ Получить список навыков из БД """
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer


class IndustryListView(generics.ListAPIView):
    """ Получить список сфер из БД """
    queryset = Industry.objects.all()
    serializer_class = IndustrySerializer
