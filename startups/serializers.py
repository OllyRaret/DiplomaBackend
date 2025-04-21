import os

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from reference.models import Industry, Profession, Skill
from reference.serializers import ProfessionSerializer, IndustrySerializer, SkillSerializer
from users.serializers import FounderProfileSerializer, SpecialistProfileSerializer
from .models import Startup, RequiredSpecialist

User = get_user_model()


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
    specialist_user_id = serializers.IntegerField(
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = RequiredSpecialist
        fields = [
            'id',
            'profession', 'skills', 'specialist',
            'profession_id', 'skills_ids', 'specialist_user_id'
        ]


    def validate_specialist_user_id(self, value):
        if value is None:
            return None

        try:
            user = User.objects.get(id=value)
        except User.DoesNotExist:
            raise ValidationError("Пользователь с указанным ID не найден")

        if not hasattr(user, 'specialist_profile'):
            raise ValidationError("Указанный пользователь не является специалистом")

        return user.specialist_profile


class StartupSerializer(serializers.ModelSerializer):
    founder = FounderProfileSerializer(read_only=True) # ToDo
    image = serializers.ImageField(required=False, allow_null=True)
    industry = IndustrySerializer(read_only=True)
    industry_id = serializers.PrimaryKeyRelatedField(
        queryset=Industry.objects.all(), source='industry', write_only=True, required=True
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


    def validate(self, attrs):
        # Проверка на отрицательную инвестицию
        investment = attrs.get('investment_needed')
        if investment is not None and investment < 0:
            raise ValidationError({'investment_needed': 'Сумма инвестиций не может быть отрицательной.'})

        return attrs


    def create(self, validated_data):
        required_specialists_data = validated_data.pop('required_specialists', [])
        startup = Startup.objects.create(**validated_data)

        for specialist_data in required_specialists_data:
            skills = specialist_data.pop('skills', [])
            specialist = specialist_data.pop('specialist_user_id', None)
            required_specialist = RequiredSpecialist.objects.create(startup=startup, specialist=specialist, **specialist_data)
            required_specialist.skills.set(skills)

        return startup


    def update(self, instance, validated_data):
        required_specialists_data = validated_data.pop('required_specialists', None)

        old_image = instance.image
        new_image = validated_data.get('image', None)

        # Удаление картинки, если передано null или другая картинка
        if 'image' in validated_data and old_image and (
            new_image is None or new_image != old_image
        ):
            image_path = old_image.path
            instance.image.delete(save=False)
            if os.path.isfile(image_path):
                os.remove(image_path)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if required_specialists_data is not None:
            # Удаляем старых
            instance.required_specialists.all().delete()
            # Добавляем новых
            for specialist_data in required_specialists_data:
                skills = specialist_data.pop('skills', [])
                specialist = specialist_data.pop('specialist_user_id', None)
                required_specialist = RequiredSpecialist.objects.create(startup=instance, specialist=specialist, **specialist_data)
                required_specialist.skills.set(skills)

        return instance
