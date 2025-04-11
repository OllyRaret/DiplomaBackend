from django.db import models

from reference.models import Profession, Industry, Skill
from reference.stages import StartupStage
from users.models import FounderProfile, SpecialistProfile


class Startup(models.Model):
    founder = models.ForeignKey(
        FounderProfile,
        on_delete=models.CASCADE,
        related_name='startups',
        verbose_name='Основатель'
    )
    image = models.ImageField(
        upload_to='startup_images/',
        null=True,
        blank=True,
        verbose_name='Фото стартапа'
    )
    title = models.CharField(max_length=255, verbose_name='Название')
    industry = models.ForeignKey(Industry, on_delete=models.SET_NULL, null=True, verbose_name='Сфера')
    description = models.TextField(verbose_name='Описание')
    stage = models.CharField(max_length=20, choices=StartupStage.CHOICES, verbose_name='Стадия')
    investment_needed = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Необходимые инвестиции'
    )
    views = models.PositiveIntegerField(default=0, verbose_name='Количество просмотров')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Стартап'
        verbose_name_plural = 'Стартапы'


class RequiredSpecialist(models.Model):
    startup = models.ForeignKey(
        Startup,
        on_delete=models.CASCADE,
        related_name='required_specialists',
        verbose_name='Стартап'
    )
    profession = models.ForeignKey(
        Profession,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Профессия'
    )
    skills = models.ManyToManyField(Skill, verbose_name='Необходимые навыки')
    specialist = models.ForeignKey(
        SpecialistProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Найденный специалист'
    )

    def __str__(self):
        return f'{self.profession} для {self.startup.title}'

    class Meta:
        verbose_name = 'Требуемый специалист'
        verbose_name_plural = 'Требуемые специалисты'
