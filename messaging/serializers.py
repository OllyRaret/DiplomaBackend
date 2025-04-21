from rest_framework import serializers

from users.models import User
from .models import Message
from users.serializers import CustomUserSerializer

class MessageSerializer(serializers.ModelSerializer):
    sender = CustomUserSerializer(read_only=True)
    recipient = CustomUserSerializer(read_only=True)
    recipient_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='recipient', write_only=True
    )

    class Meta:
        model = Message
        fields = ['id', 'sender', 'recipient', 'recipient_id', 'text', 'timestamp', 'is_read']
        read_only_fields = ['id', 'sender', 'timestamp', 'is_read']

    def validate(self, data):
        sender = self.context['request'].user
        recipient = data.get('recipient')

        # Проверка на отправку самому себе
        if sender.id == recipient.id:
            raise serializers.ValidationError('Нельзя отправить сообщение самому себе.')

        return data
