from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from djoser.serializers import TokenCreateSerializer as DjoserTokenCreateSerializer
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer, UserSerializer as BaseUserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from reference.models import Profession, Skill, Industry
from reference.serializers import ProfessionSerializer, SkillSerializer, IndustrySerializer
from reference.stages import StartupStage
from .models import User, SpecialistProfile, FounderProfile, InvestorProfile, WorkExperience, InvestorPreviousInvestment
from .utils import update_user_fields


class CustomUserCreateSerializer(BaseUserCreateSerializer):
    email = serializers.EmailField(
        validators=[
            UniqueValidator(queryset=User.objects.all(), message="Пользователь с такой почтой уже зарегистрирован.")
        ]
    )
    password = serializers.CharField(write_only=True, required=True)
    re_password = serializers.CharField(write_only=True, required=True)
    role = serializers.ChoiceField(choices=User.Role.choices, required=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 're_password', 'role')

    def validate(self, data):
        if data['password'] != data['re_password']:
            raise serializers.ValidationError({"re_password": "Пароли не совпадают."})

        # Проверка пароля через встроенные валидаторы Django
        try:
            validate_password(data['password'], user=User(email=data.get('email')))
        except ValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})

        return data

    def create(self, validated_data):
        validated_data.pop('re_password')
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


class CustomTokenCreateSerializer(DjoserTokenCreateSerializer):
    email = serializers.EmailField(required=True, error_messages={
        'required': 'Поле email обязательно.',
        'blank': 'Поле email не может быть пустым.',
        'invalid': 'Введите корректный адрес электронной почты.'
    })
    password = serializers.CharField(required=True, error_messages={
        'required': 'Поле пароль обязательно.',
        'blank': 'Поле пароль не может быть пустым.'
    })

    default_error_messages = {
        'invalid_credentials': 'Неверный email или пароль.',
        'inactive_account': 'Учетная запись отключена.'
    }

    def validate(self, attrs):
        self.user = authenticate(
            request=self.context.get('request'),
            email=attrs.get('email'),
            password=attrs.get('password')
        )

        if not self.user:
            raise serializers.ValidationError(self.error_messages['invalid_credentials'], code='authorization')
        if not self.user.is_active:
            raise serializers.ValidationError(self.error_messages['inactive_account'], code='authorization')

        return attrs


class CustomUserSerializer(BaseUserSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'role', 'full_name', 'bio', 'contact_phone', 'contact_email', 'avatar')


# Опыт работы специалиста и стартапера
class WorkExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkExperience
        fields = ['id', 'organization', 'position', 'start_date', 'end_date', 'description']

    def validate(self, data):
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError("Дата окончания не может быть раньше даты начала.")
        return data


# Инвестиционный опыт
class InvestorPreviousInvestmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestorPreviousInvestment
        fields = ['id', 'title', 'industry', 'stage', 'date', 'description']


class SpecialistProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(source='user', read_only=True)
    role = serializers.ChoiceField(source='user.role', choices=User.Role.choices, read_only=True)
    full_name = serializers.CharField(source='user.full_name', required=False, allow_blank=True, allow_null=True)
    bio = serializers.CharField(source='user.bio', required=False, allow_blank=True, allow_null=True)
    contact_phone = serializers.CharField(source='user.contact_phone', required=False, allow_blank=True, allow_null=True)
    contact_email = serializers.EmailField(source='user.contact_email', required=False, allow_blank=True, allow_null=True)
    avatar = serializers.ImageField(source='user.avatar', required=False, allow_null=True)
    experience = WorkExperienceSerializer(many=True, source='experiences', required=False)
    profession = ProfessionSerializer(read_only=True)
    profession_id = serializers.PrimaryKeyRelatedField(
        queryset=Profession.objects.all(), source='profession', write_only=True, required=False
    )
    skills = SkillSerializer(many=True, read_only=True)
    skill_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Skill.objects.all(), source='skills', write_only=True, required=False
    )
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = SpecialistProfile
        fields = [
            'user_id', 'role', 'full_name', 'bio', 'contact_phone', 'contact_email', 'avatar',
            'profession', 'profession_id', 'skills', 'skill_ids', 'experience', 'is_favorited'
        ]

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return False # ToDo

    def update(self, instance, validated_data):
        user = instance.user

        # Обновляем поля User
        update_user_fields(user, validated_data)

        # Обновляем поля профиля (обнуляем при отсутствии)
        instance.profession = validated_data.get('profession', instance.profession)
        if 'skills' in validated_data:
            skills = validated_data.get('skills', [])
            instance.skills.set(skills)

        if 'experiences' in validated_data:
            experiences_data = validated_data.pop('experiences', instance.experiences)
            instance.experiences.all().delete()
            for exp in experiences_data:
                WorkExperience.objects.create(specialist=instance, **exp)

        instance.save()
        return instance


class FounderProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(source='user', read_only=True)
    role = serializers.ChoiceField(source='user.role', choices=User.Role.choices, read_only=True)
    full_name = serializers.CharField(source='user.full_name', required=False, allow_blank=True, allow_null=True)
    bio = serializers.CharField(source='user.bio', required=False, allow_blank=True, allow_null=True)
    contact_phone = serializers.CharField(source='user.contact_phone', required=False, allow_blank=True, allow_null=True)
    contact_email = serializers.EmailField(source='user.contact_email', required=False, allow_blank=True, allow_null=True)
    avatar = serializers.ImageField(source='user.avatar', required=False, allow_null=True)
    experience = WorkExperienceSerializer(many=True, source='experiences', required=False)
    industry = IndustrySerializer(read_only=True)
    industry_id = serializers.PrimaryKeyRelatedField(
        queryset=Industry.objects.all(), source='industry', write_only=True, required=False
    )
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = FounderProfile
        fields = [
            'user_id', 'role', 'full_name', 'industry', 'industry_id', 'bio', 'contact_phone', 'contact_email', 'avatar',
            'experience', 'is_favorited'
        ]

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return False # ToDo

    def update(self, instance, validated_data):
        user = instance.user

        update_user_fields(user, validated_data)

        instance.industry = validated_data.get('industry', instance.industry)

        if 'experiences' in validated_data:
            experiences_data = validated_data.get('experiences', instance.experiences)
            instance.experiences.all().delete()
            for exp in experiences_data:
                WorkExperience.objects.create(founder=instance, **exp)

        instance.save()
        return instance


class InvestorProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(source='user', read_only=True)
    role = serializers.ChoiceField(source='user.role', choices=User.Role.choices, read_only=True)
    full_name = serializers.CharField(source='user.full_name', required=False, allow_blank=True, allow_null=True)
    bio = serializers.CharField(source='user.bio', required=False, allow_blank=True, allow_null=True)
    contact_phone = serializers.CharField(source='user.contact_phone', required=False, allow_blank=True, allow_null=True)
    contact_email = serializers.EmailField(source='user.contact_email', required=False, allow_blank=True, allow_null=True)
    avatar = serializers.ImageField(source='user.avatar', required=False, allow_null=True)
    experience = InvestorPreviousInvestmentSerializer(many=True, source='previous_investments', required=False)
    industry = IndustrySerializer(read_only=True)
    industry_id = serializers.PrimaryKeyRelatedField(
        queryset=Industry.objects.all(), source='industry', write_only=True, required=False
    )
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = InvestorProfile
        fields = [
            'user_id', 'role', 'full_name', 'industry', 'industry_id', 'company', 'position',
            'bio', 'contact_phone', 'contact_email', 'avatar',
            'preferred_stages', 'investment_min', 'investment_max',
            'experience', 'is_favorited'
        ]


    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return False # ToDo


    def validate(self, data):
        preferred_stages = data.get('preferred_stages', [])
        valid_stages = [choice[0] for choice in StartupStage.CHOICES]
        invalid_stages = [stage for stage in preferred_stages if stage not in valid_stages]
        if invalid_stages:
            raise serializers.ValidationError({
                'preferred_stages': f"Недопустимые значения: {invalid_stages}. Допустимые: {valid_stages}"
            })

        return data


    def update(self, instance, validated_data):
        user = instance.user

        update_user_fields(user, validated_data)

        instance.industry = validated_data.get('industry', instance.industry)
        instance.company = validated_data.get('company', instance.company)
        instance.position = validated_data.get('position', instance.position)
        instance.preferred_stages = validated_data.get('preferred_stages', instance.preferred_stages)
        instance.investment_min = validated_data.get('investment_min', instance.investment_min)
        instance.investment_max = validated_data.get('investment_max', instance.investment_max)

        if 'previous_investments' in validated_data:
            previous_data = validated_data.get('previous_investments', [])
            instance.previous_investments.all().delete()
            for exp in previous_data:
                InvestorPreviousInvestment.objects.create(investor=instance, **exp)

        instance.save()
        return instance
