from rest_framework import serializers

from users.models import User
from .models import Message
from users.serializers import CustomUserSerializer

class MessageSerializer(serializers.ModelSerializer):
    sender = CustomUserSerializer(read_only=True)
    recipient = CustomUserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'recipient', 'text', 'timestamp', 'is_read']
        read_only_fields = ['id', 'sender', 'timestamp', 'is_read']

    def create(self, validated_data):
        # Получаем отправителя из контекста
        validated_data['sender'] = self.context['request'].user

        # Извлекаем recipient_id и получаем получателя
        recipient_id = self.context['request'].data.get('recipient_id')
        validated_data['recipient'] = User.objects.get(id=recipient_id)

        return super().create(validated_data)
