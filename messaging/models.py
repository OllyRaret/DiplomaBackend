from django.db import models
from django.db.models import Q

from users.models import User


class Message(models.Model):
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True, related_name='sent_messages',
        verbose_name='Отправитель'
    )
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_messages',
        verbose_name='Получатель'
    )
    text = models.TextField(verbose_name='Текст сообщения')
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Время отправки'
    )
    is_read = models.BooleanField(default=False, verbose_name='Прочитано')

    def __str__(self):
        return f'Сообщение от {self.sender} к {self.recipient}'

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ['-timestamp']


class Invitation(models.Model):
    startup = models.ForeignKey(
        'startups.Startup',
        on_delete=models.CASCADE,
        related_name='invitations',
        verbose_name='Стартап'
    )
    required_specialist = models.ForeignKey(
        'startups.RequiredSpecialist',
        on_delete=models.CASCADE,
        related_name='invitations',
        verbose_name='Вакансия'
    )
    specialist = models.ForeignKey(
        'users.SpecialistProfile',
        on_delete=models.CASCADE,
        related_name='invitations',
        verbose_name='Специалист'
    )
    is_accepted = models.BooleanField(
        null=True,
        default=None,
        verbose_name='Принято'
    )  # None — в ожидании
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Время отправки'
    )

    class Meta:
        verbose_name = 'Приглашение'
        verbose_name_plural = 'Приглашения'
        constraints = [
            models.UniqueConstraint(
                fields=['required_specialist'],
                condition=Q(is_accepted=None),
                name='only_one_pending_invitation_per_vacancy'
            )
        ]

    def __str__(self):
        return (f'{self.specialist} пригласил '
                f'{self.required_specialist} в {self.startup}')
