from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.db import models


# Справочники
class Profession(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Skill(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Industry(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# Пользователь (с возможностью авторизации по email)
class User(AbstractUser):
    class Role(models.TextChoices):
        STARTUP = 'startup', 'Основатель стартапа'
        INVESTOR = 'investor', 'Инвестор'
        SPECIALIST = 'specialist', 'Специалист'

    username = None
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=Role.choices)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    # Общие поля профиля
    full_name = models.CharField(max_length=200)
    bio = models.TextField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    contact_email = models.EmailField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"


# Профиль специалиста
class SpecialistProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='specialist_profile')
    profession = models.ForeignKey(Profession, on_delete=models.SET_NULL, null=True, blank=True)
    skills = models.ManyToManyField(Skill, blank=True)

    def __str__(self):
        return f'Specialist: {self.user.full_name}'


# Профиль основателя стартапа
class FounderProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='founder_profile')
    industry = models.ForeignKey(Industry, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'Founder: {self.user.full_name}'


# Опыт работы
class WorkExperience(models.Model):
    # может быть либо у специалиста, либо у основателя
    specialist = models.ForeignKey(
        SpecialistProfile, on_delete=models.CASCADE, related_name='experiences', null=True, blank=True
    )
    founder = models.ForeignKey(
        FounderProfile, on_delete=models.CASCADE, related_name='experiences', null=True, blank=True
    )

    organization = models.CharField(max_length=200)
    position = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True)

    def __str__(self):
        owner = self.specialist or self.founder
        return f'{owner}: {self.organization} — {self.position}'


# Профиль инвестора
class InvestorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    industry = models.ForeignKey(Industry, on_delete=models.SET_NULL, null=True)
    company = models.CharField(max_length=255)
    position = models.CharField(max_length=255)

    STAGE_CHOICES = [
        ('waiting', 'Ожидание'),
        ('in_progress', 'В процессе'),
        ('launch', 'Запуск'),
        ('analysis', 'Анализ результатов'),
        ('completed', 'Завершён'),
    ]
    preferred_stages = ArrayField(
        base_field=models.CharField(max_length=20, choices=STAGE_CHOICES),
        default=list,
        verbose_name='Предпочтительные стадии инвестирования'
    )

    investment_min = models.DecimalField(max_digits=12, decimal_places=2)
    investment_max = models.DecimalField(max_digits=12, decimal_places=2)


class InvestorPreviousInvestment(models.Model):
    investor = models.ForeignKey(InvestorProfile, on_delete=models.CASCADE, related_name='previous_investments')
    title = models.CharField(max_length=255)
    industry = models.ForeignKey(Industry, on_delete=models.SET_NULL, null=True)
    stage = models.ForeignKey('StartupStage', on_delete=models.SET_NULL, null=True)
    date = models.DateField()
    description = models.TextField(blank=True)
