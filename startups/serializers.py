from rest_framework import serializers

from reference.models import Industry, Profession, Skill
from users.models import SpecialistProfile
from .models import Startup, RequiredSpecialist
from users.serializers import FounderProfileSerializer, SpecialistProfileSerializer, CustomUserSerializer
from reference.serializers import ProfessionSerializer, IndustrySerializer, SkillSerializer


class RequiredSpecialistSerializer(serializers.ModelSerializer):
    profession = ProfessionSerializer(read_only=True)
    profession_id = serializers.PrimaryKeyRelatedField(
        queryset=Profession.objects.all(),
        write_only=True,
        source='profession'
    )
    skills = SkillSerializer(many=True, read_only=True)
    skills_ids = serializers.PrimaryKeyRelatedField(
        queryset=Skill.objects.all(),
        many=True,
        write_only=True,
        source='skills'
    )
    specialist = SpecialistProfileSerializer(read_only=True)
    specialist_id = serializers.PrimaryKeyRelatedField(
        queryset=SpecialistProfile.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
        source='specialist'
    )

    class Meta:
        model = RequiredSpecialist
        fields = [
            'id',
            'profession', 'skills', 'specialist',
            'profession_id', 'skills_ids', 'specialist_id'
        ]


class StartupSerializer(serializers.ModelSerializer):
    founder = FounderProfileSerializer(read_only=True) # ToDo
    image = serializers.ImageField(required=False, allow_null=True)
    industry = IndustrySerializer(read_only=True)
    industry_id = serializers.PrimaryKeyRelatedField(
        queryset=Industry.objects.all(), source='industry', write_only=True, required=False
    )
    required_specialists = RequiredSpecialistSerializer(many=True) # ToDo
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Startup
        fields = [
            'id', 'title', 'image', 'industry', 'industry_id', 'description',
            'stage', 'investment_needed', 'founder', 'required_specialists', 'is_favorited'
        ]

    def get_is_favorited(self, obj):
        # ToDo
        return False


    def create(self, validated_data):
        required_specialists_data = validated_data.pop('required_specialists', [])
        startup = Startup.objects.create(**validated_data)

        for specialist_data in required_specialists_data:
            skills = specialist_data.pop('skills', [])
            required_specialist = RequiredSpecialist.objects.create(startup=startup, **specialist_data)
            required_specialist.skills.set(skills)

        return startup


    def update(self, instance, validated_data):
        required_specialists_data = validated_data.pop('required_specialists', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if required_specialists_data is not None:
            # Удаляем старых
            instance.required_specialists.all().delete()
            # Добавляем новых
            for specialist_data in required_specialists_data:
                skills = specialist_data.pop('skills', [])
                required_specialist = RequiredSpecialist.objects.create(startup=instance, **specialist_data)
                required_specialist.skills.set(skills)

        return instance
