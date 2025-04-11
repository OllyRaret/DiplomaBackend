from django.db import models
from users.models import User


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages', verbose_name='Отправитель')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages', verbose_name='Получатель')
    text = models.TextField(verbose_name='Текст сообщения')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Время отправки')
    is_read = models.BooleanField(default=False, verbose_name='Прочитано')

    def __str__(self):
        return f'Сообщение от {self.sender} к {self.recipient}'

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ['-timestamp']
