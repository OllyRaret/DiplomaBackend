from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer, UserSerializer as BaseUserSerializer
from rest_framework import serializers

from .models import User, SpecialistProfile, FounderProfile, InvestorProfile, WorkExperience, InvestorPreviousInvestment


class UserCreateSerializer(BaseUserCreateSerializer):
    password = serializers.CharField(write_only=True)
    password_confirmation = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=User.Role.choices)

    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = ('id', 'email', 'password', 'password_confirmation', 'role')

    def validate(self, data):
        if data['password'] != data['password_confirmation']:
            raise serializers.ValidationError("Пароли не совпадают.")
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirmation')
        role = validated_data.get('role')
        user = User.objects.create_user(**validated_data)

        # Создаем профиль в зависимости от роли
        if role == User.Role.SPECIALIST:
            SpecialistProfile.objects.create(user=user)
        elif role == User.Role.STARTUP:
            FounderProfile.objects.create(user=user)
        elif role == User.Role.INVESTOR:
            InvestorProfile.objects.create(user=user)

        return user


class UserSerializer(BaseUserSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'role', 'full_name', 'bio', 'contact_phone', 'contact_email', 'avatar')


# Опыт работы специалиста и стартапера
class WorkExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkExperience
        fields = ['id', 'organization', 'position', 'start_date', 'end_date', 'description']


# Инвестиционный опыт
class InvestorPreviousInvestmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestorPreviousInvestment
        fields = ['id', 'title', 'industry', 'stage', 'date', 'description']


class SpecialistProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(source='user', read_only=True)
    full_name = serializers.CharField(source='user.full_name')
    bio = serializers.CharField(source='user.bio')
    contact_phone = serializers.CharField(source='user.contact_phone')
    contact_email = serializers.EmailField(source='user.contact_email')
    avatar = serializers.ImageField(source='user.avatar')
    experience = WorkExperienceSerializer(many=True, source='experiences', required=False)
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = SpecialistProfile
        fields = [
            'user_id', 'full_name', 'bio', 'contact_phone', 'contact_email', 'avatar',
            'profession', 'skills', 'experience', 'is_favorited'
        ]

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return False # ToDo

    def update(self, instance, validated_data):
        user = instance.user

        # Обновляем поля User (обнуляем при отсутствии)
        user.full_name = validated_data.get('full_name')
        user.bio = validated_data.get('bio')
        user.contact_phone = validated_data.get('contact_phone')
        user.contact_email = validated_data.get('contact_email')
        user.avatar = validated_data.get('avatar')
        user.save()

        # Обновляем поля профиля (обнуляем при отсутствии)
        instance.profession = validated_data.get('profession')
        skills = validated_data.get('skills', [])
        instance.skills.set(skills)

        experiences_data = validated_data.pop('experiences', [])
        instance.experiences.all().delete()
        for exp in experiences_data:
            WorkExperience.objects.create(specialist=instance, **exp)

        instance.save()
        return super().update(instance, validated_data)


class FounderProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(source='user', read_only=True)
    full_name = serializers.CharField(source='user.full_name')
    bio = serializers.CharField(source='user.bio')
    contact_phone = serializers.CharField(source='user.contact_phone')
    contact_email = serializers.EmailField(source='user.contact_email')
    avatar = serializers.ImageField(source='user.avatar')
    experience = WorkExperienceSerializer(many=True, source='experiences', required=False)
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = FounderProfile
        fields = [
            'user_id', 'full_name', 'industry', 'bio', 'contact_phone', 'contact_email', 'avatar',
            'experience', 'is_favorited'
        ]

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return False # ToDo

    def update(self, instance, validated_data):
        user = instance.user

        user.full_name = validated_data.get('full_name')
        user.bio = validated_data.get('bio')
        user.contact_phone = validated_data.get('contact_phone')
        user.contact_email = validated_data.get('contact_email')
        user.avatar = validated_data.get('avatar')
        user.save()

        instance.industry = validated_data.get('industry')

        experiences_data = validated_data.get('experience', [])
        instance.experiences.all().delete()
        for exp in experiences_data:
            WorkExperience.objects.create(founder=instance, **exp)

        instance.save()
        return instance


class InvestorProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(source='user', read_only=True)
    full_name = serializers.CharField(source='user.full_name')
    bio = serializers.CharField(source='user.bio')
    contact_phone = serializers.CharField(source='user.contact_phone')
    contact_email = serializers.EmailField(source='user.contact_email')
    avatar = serializers.ImageField(source='user.avatar')
    experience = InvestorPreviousInvestmentSerializer(many=True, source='previous_investments', required=False)
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = InvestorProfile
        fields = [
            'user_id', 'full_name', 'industry', 'company', 'position',
            'bio', 'contact_phone', 'contact_email', 'avatar',
            'preferred_stages', 'investment_min', 'investment_max',
            'experience', 'is_favorited'
        ]

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return False # ToDo

    def update(self, instance, validated_data):
        user = instance.user

        user.full_name = validated_data.get('full_name')
        user.bio = validated_data.get('bio')
        user.contact_phone = validated_data.get('contact_phone')
        user.contact_email = validated_data.get('contact_email')
        user.avatar = validated_data.get('avatar')
        user.save()

        instance.industry = validated_data.get('industry')
        instance.company = validated_data.get('company')
        instance.position = validated_data.get('position')
        instance.preferred_stages.set(validated_data.get('preferred_stages', []))
        instance.investment_min = validated_data.get('investment_min')
        instance.investment_max = validated_data.get('investment_max')

        previous_data = validated_data.get('previous_investments', [])
        instance.previous_investments.all().delete()
        for exp in previous_data:
            InvestorPreviousInvestment.objects.create(investor=instance, **exp)

        instance.save()
        return instance
