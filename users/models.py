from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import JSONField

from reference.models import Profession, Skill, Industry
from reference.stages import StartupStage
from users.manager import NoUsernameUserManager


# Пользователь (с возможностью авторизации по email)
class User(AbstractUser):
    class Role(models.TextChoices):
        STARTUP = 'startup', 'Основатель стартапа'
        INVESTOR = 'investor', 'Инвестор'
        SPECIALIST = 'specialist', 'Специалист'

    username = models.TextField(blank=True, verbose_name='Имя пользователя', help_text='Не используется')
    email = models.EmailField(unique=True, verbose_name='Электронная почта')
    role = models.CharField(max_length=20, choices=Role.choices, verbose_name='Роль', blank=True)

    objects = NoUsernameUserManager()  # Создание пользователя без username

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    # Общие поля профиля
    full_name = models.CharField(max_length=200, verbose_name='Полное имя', blank=True)
    bio = models.TextField(blank=True, verbose_name='Описание')
    contact_phone = models.CharField(max_length=20, blank=True, verbose_name='Контактный телефон')
    contact_email = models.EmailField(blank=True, verbose_name='Контактная электронная почта')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Аватар')

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


# Профиль специалиста
class SpecialistProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='specialist_profile',
        verbose_name='Пользователь'
    )
    profession = models.ForeignKey(
        Profession,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Профессия'
    )
    skills = models.ManyToManyField(Skill, blank=True, verbose_name='Навыки')

    def __str__(self):
        return f'Специалист: {self.user.full_name}'

    class Meta:
        verbose_name = 'Специалист'
        verbose_name_plural = 'Специалисты'


# Профиль основателя стартапа
class FounderProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='founder_profile',
        verbose_name='Пользователь'
    )
    industry = models.ForeignKey(Industry, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Сфера')

    def __str__(self):
        return f'Основатель: {self.user.full_name}'

    class Meta:
        verbose_name = 'Основатель стартапов'
        verbose_name_plural = 'Основатели стартапов'


# Опыт работы
class WorkExperience(models.Model):
    # может быть либо у специалиста, либо у основателя
    specialist = models.ForeignKey(
        SpecialistProfile,
        on_delete=models.CASCADE,
        related_name='experiences',
        null=True,
        blank=True,
        verbose_name='Специалист'
    )
    founder = models.ForeignKey(
        FounderProfile,
        on_delete=models.CASCADE,
        related_name='experiences',
        null=True,
        blank=True,
        verbose_name='Основатель'
    )

    organization = models.CharField(max_length=200, verbose_name='Организация')
    position = models.CharField(max_length=100, verbose_name='Должность')
    start_date = models.DateField(verbose_name='Дата начала')
    end_date = models.DateField(blank=True, null=True, verbose_name='Дата окончания')
    description = models.TextField(blank=True, verbose_name='Описание')

    def __str__(self):
        owner = self.specialist or self.founder
        return f'{owner}: {self.organization} — {self.position}'

    class Meta:
        verbose_name = 'Опыт работы'
        verbose_name_plural = 'Опыт работы'


# Профиль инвестора
class InvestorProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='investor_profile',
        verbose_name='Пользователь'
    )

    industry = models.ForeignKey(Industry, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Сфера')
    company = models.CharField(max_length=255, verbose_name='Компания', blank=True)
    position = models.CharField(max_length=255, verbose_name='Должность', blank=True)

    preferred_stages = JSONField(
        default=list,
        verbose_name='Предпочтительные стадии инвестирования',
        help_text='Список стадий из StartupStage.CHOICES',
        blank=True
    )

    investment_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, verbose_name='Минимальная инвестиция')
    investment_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, verbose_name='Максимальная инвестиция')

    def __str__(self):
        return f'Инвестор: {self.user.full_name}'

    class Meta:
        verbose_name = 'Инвестор'
        verbose_name_plural = 'Инвесторы'


class InvestorPreviousInvestment(models.Model):
    investor = models.ForeignKey(
        InvestorProfile,
        on_delete=models.CASCADE,
        related_name='previous_investments',
        verbose_name='Инвестор'
    )
    title = models.CharField(max_length=255, verbose_name='Название')
    industry = models.ForeignKey(Industry, on_delete=models.SET_NULL, null=True, verbose_name='Сфера')
    stage = models.CharField(max_length=20, choices=StartupStage.CHOICES, verbose_name='Стадия')
    date = models.DateField(verbose_name='Дата')
    description = models.TextField(blank=True, verbose_name='Описание')

    def __str__(self):
        return f'{self.title} ({self.date})'

    class Meta:
        verbose_name = 'Предыдущая инвестиция'
        verbose_name_plural = 'Предыдущие инвестиции'
