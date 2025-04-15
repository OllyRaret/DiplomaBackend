from rest_framework import serializers
from .models import Profession, Skill, Industry


class ProfessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profession
        fields = ['id', 'name']


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name']


class IndustrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Industry
        fields = ['id', 'name']
