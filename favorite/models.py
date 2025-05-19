from django.db import models

from startups.models import Startup
from users.models import User, SpecialistProfile, InvestorProfile


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )

    specialist = models.ForeignKey(
        SpecialistProfile,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Специалист'
    )
    startup = models.ForeignKey(
        Startup,
        related_name='favorited_by',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Стартап'
    )
    investor = models.ForeignKey(
        InvestorProfile,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Инвестор'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(specialist__isnull=False) |
                    models.Q(startup__isnull=False) |
                    models.Q(investor__isnull=False)
                ),
                name='favorite_object_not_null'
            ),
            models.UniqueConstraint(
                fields=['user', 'specialist'],
                condition=models.Q(specialist__isnull=False),
                name='unique_favorite_specialist'
            ),
            models.UniqueConstraint(
                fields=['user', 'investor'],
                condition=models.Q(investor__isnull=False),
                name='unique_favorite_investor'
            ),
            models.UniqueConstraint(
                fields=['user', 'startup'],
                condition=models.Q(startup__isnull=False),
                name='unique_favorite_startup'
            ),
        ]

    def __str__(self):
        if self.specialist:
            return f'{self.specialist.user} в избранном у {self.user}'
        if self.startup:
            return f'Стартап {self.startup.title} в избранном у {self.user}'
        if self.investor:
            return f'{self.investor.user} в избранном у {self.user}'
