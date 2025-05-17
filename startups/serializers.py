import os

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from favorite.models import Favorite
from reference.models import Industry, Profession, Skill
from reference.serializers import ProfessionSerializer, IndustrySerializer, SkillSerializer
from users.serializers import SpecialistShortSerializer, FounderShortSerializer
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
    specialist = SpecialistShortSerializer(read_only=True)
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
    founder = FounderShortSerializer(read_only=True)
    image = serializers.ImageField(required=False, allow_null=True)
    industry = IndustrySerializer(read_only=True)
    industry_id = serializers.PrimaryKeyRelatedField(
        queryset=Industry.objects.all(), source='industry', write_only=True, required=True
    )
    required_specialists = RequiredSpecialistSerializer(many=True) # ToDo
    is_favorited = serializers.SerializerMethodField()
    views = serializers.IntegerField(read_only=True)
    favorites_count = serializers.SerializerMethodField()

    class Meta:
        model = Startup
        fields = [
            'id', 'title', 'image', 'industry', 'industry_id', 'description',
            'stage', 'investment_needed', 'founder', 'required_specialists',
            'is_favorited', 'views', 'favorites_count'
        ]


    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return Favorite.objects.filter(user=request.user, startup=obj).exists()


    def get_favorites_count(self, obj):
        return Favorite.objects.filter(startup=obj).count()


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
            instance.image = None
            if os.path.isfile(image_path):
                os.remove(image_path)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if required_specialists_data is not None:
            existing_specialists = list(instance.required_specialists.all())
            updated_specialists = []

            for new_data in required_specialists_data:
                new_skills_ids = set([new_skill.id for new_skill in new_data.get('skills', [])])
                new_profession = new_data.get('profession')
                new_specialist = new_data.get('specialist_user_id', None)

                match_found = False

                for existing in existing_specialists:
                    existing_skills_ids = set(existing.skills.values_list('id', flat=True))
                    if (
                        existing_skills_ids == new_skills_ids and
                        existing.profession == new_profession
                    ):
                        # Совпали по skills и профессии — проверяем specialist
                        if 'specialist_user_id' in new_data and existing.specialist != new_specialist:
                            existing.specialist = new_specialist
                            existing.save()
                        updated_specialists.append(existing.id)
                        match_found = True
                        break

                if not match_found:
                    # Если совпадения нет — создаём новую запись
                    skills = new_data.pop('skills', [])
                    specialist = new_data.pop('specialist_user_id', None)
                    required_specialist = RequiredSpecialist.objects.create(
                        startup=instance, specialist=specialist, **new_data
                    )
                    required_specialist.skills.set(skills)
                    updated_specialists.append(required_specialist.id)

            # Удаляем все записи, которые не вошли в updated_specialists
            instance.required_specialists.exclude(id__in=updated_specialists).delete()

        return instance


class StartupForSpecialistSearchSerializer(serializers.ModelSerializer):
    required_specialists = RequiredSpecialistSerializer(many=True, read_only=True)
    industry = IndustrySerializer(read_only=True)
    founder_id = serializers.PrimaryKeyRelatedField(source='founder.user', read_only=True)
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Startup
        fields = ['id', 'title', 'industry', 'description', 'required_specialists', 'founder_id', 'image', 'is_favorited']

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return Favorite.objects.filter(user=request.user, startup=obj).exists()


class StartupForSpecialistShortSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = Startup
        fields = ['id', 'title', 'description', 'stage', 'image', 'role']

    def get_role(self, obj):
        invited_roles = self.context.get('invited_roles', {})
        if invited_roles:
            return invited_roles.get(obj.id)

        specialist_profile = self.context['request'].user.specialist_profile
        required = obj.required_specialists.filter(specialist=specialist_profile).first()
        return required.profession.name if required else None


class StartupForInvestorSearchSerializer(serializers.ModelSerializer):
    industry = IndustrySerializer(read_only=True)
    founder_id = serializers.PrimaryKeyRelatedField(source='founder.user', read_only=True)
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Startup
        fields = ['id', 'title', 'industry', 'description', 'investment_needed', 'image', 'founder_id', 'is_favorited']

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return Favorite.objects.filter(user=request.user, startup=obj).exists()


class StartupForFounderShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Startup
        fields = ['id', 'title', 'description', 'stage', 'image']
