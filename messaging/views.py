from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q, Max
from .models import Message
from .serializers import MessageSerializer
from users.models import User


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(Q(sender=user) | Q(recipient=user)).order_by('-timestamp')

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

    @action(detail=False, methods=['get'])
    def inbox(self, request):
        """ Получить полученные пользователем сообщения """
        messages = Message.objects.filter(recipient=request.user)
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def sent(self, request):
        """ Получить отправленные пользователем сообщения """
        messages = Message.objects.filter(sender=request.user)
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def dialogs(self, request):
        """ Получить диалоги авторизованного пользователя """
        user = request.user
        messages = Message.objects.filter(Q(sender=user) | Q(recipient=user))

        # Получаем последний message id в каждом диалоге
        latest_ids = (
            messages
            .values('sender', 'recipient')
            .annotate(latest_id=Max('id'))
            .values_list('latest_id', flat=True)
        )

        # Убираем дубли из-за того, что (sender=A, recipient=B) и (sender=B, recipient=A) — это один диалог
        unique_dialogs = {}
        for m in Message.objects.filter(id__in=latest_ids):
            user1 = min(m.sender.id, m.recipient.id)
            user2 = max(m.sender.id, m.recipient.id)
            key = (user1, user2)
            if key not in unique_dialogs or unique_dialogs[key].timestamp < m.timestamp:
                unique_dialogs[key] = m

        serializer = self.get_serializer(unique_dialogs.values(), many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """ Получить диалог с конкретным пользователем (по его id) """
        user = request.user
        try:
            other_user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'detail': 'Пользователь не найден.'}, status=404)

        messages = Message.objects.filter(
            (Q(sender=user) & Q(recipient=other_user)) |
            (Q(sender=other_user) & Q(recipient=user))
        ).order_by('timestamp')

        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='mark-as-read')
    def mark_as_read(self, request, pk=None):
        """ Отметить сообщение как прочитанное """
        message = self.get_object()
        if message.recipient != request.user:
            return Response({'detail': 'Нельзя отмечать чужие сообщения.'}, status=403)
        message.is_read = True
        message.save()
        return Response({'status': 'прочитано'})
