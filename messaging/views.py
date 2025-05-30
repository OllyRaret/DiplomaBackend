from django.db.models import Q, Max
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.response import Response

from users.models import User
from .models import Message, Invitation
from .serializers import MessageSerializer, InvitationSerializer


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(
            Q(sender=user) | Q(recipient=user)
        ).order_by('-timestamp')

    def get_object(self):
        ''' Получаем другого пользователя по ID '''
        try:
            return User.objects.get(pk=self.kwargs['pk'])
        except User.DoesNotExist:
            raise NotFound('Пользователь не найден.')

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

    def destroy(self, request, pk=None):
        ''' Удаление диалога с пользователем /messages/{id}/ '''
        recipient = self.get_object()
        user = request.user

        messages = Message.objects.filter(
            Q(sender=user, recipient=recipient) |
            Q(sender=recipient, recipient=user)
        )
        deleted_count = messages.count()
        messages.delete()
        return Response({
            'status': f'Удалено {deleted_count} сообщений.'
        }, status=204)

    def retrieve(self, request, pk=None):
        ''' Получить диалог с конкретным пользователем (по его id) '''
        if pk == '-1':
            other_user = None
        else:
            other_user = self.get_object()
        user = request.user

        # Отметим непрочитанные входящие сообщения как прочитанные
        Message.objects.filter(
            sender=other_user,
            recipient=user,
            is_read=False
        ).update(is_read=True)

        # Получаем все сообщения между пользователями
        messages = Message.objects.filter(
            Q(sender=user, recipient=other_user) |
            Q(sender=other_user, recipient=user)
        ).order_by('timestamp')

        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def inbox(self, request):
        ''' Получить полученные пользователем сообщения '''
        messages = Message.objects.filter(recipient=request.user)
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def sent(self, request):
        ''' Получить отправленные пользователем сообщения '''
        messages = Message.objects.filter(sender=request.user)
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def dialogs(self, request):
        ''' Получить диалоги авторизованного пользователя '''
        user = request.user
        messages = Message.objects.filter(Q(sender=user) | Q(recipient=user))

        # Получаем последний message id в каждом диалоге
        latest_ids = (
            messages
            .values('sender', 'recipient')
            .annotate(latest_id=Max('id'))
            .values_list('latest_id', flat=True)
        )

        # Убираем дубли из-за того, что (sender=A, recipient=B)
        # и (sender=B, recipient=A) — это один диалог
        unique_dialogs = {}
        for m in Message.objects.filter(id__in=latest_ids):
            if m.sender is None:
                key = (None, m.recipient.id)
            else:
                user1 = min(m.sender.id, m.recipient.id)
                user2 = max(m.sender.id, m.recipient.id)
                key = (user1, user2)
            if (
                    key not in unique_dialogs
                    or unique_dialogs[key].timestamp < m.timestamp
            ):
                unique_dialogs[key] = m

        # Разделим системные и обычные диалоги
        system_dialogs = []
        user_dialogs = []
        for msg in unique_dialogs.values():
            if msg.sender is None:
                system_dialogs.append(msg)
            else:
                user_dialogs.append(msg)

        # Сортируем обычные диалоги по убыванию времени
        user_dialogs.sort(key=lambda m: m.timestamp, reverse=True)

        # Объединяем: сначала системные, потом обычные
        ordered_dialogs = system_dialogs + user_dialogs

        serializer = self.get_serializer(ordered_dialogs, many=True)
        return Response(serializer.data)


class InvitationViewSet(viewsets.ModelViewSet):
    queryset = Invitation.objects.select_related(
        'specialist__user', 'required_specialist', 'startup'
    )
    serializer_class = InvitationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'founder_profile'):
            return self.queryset.filter(startup__founder=user.founder_profile)
        elif hasattr(user, 'specialist_profile'):
            return self.queryset.filter(specialist=user.specialist_profile)
        return Invitation.objects.none()

    @action(detail=True, methods=['post'], url_path='accept')
    def accept_invitation(self, request, pk=None):
        invitation = self.get_object()
        user = request.user

        if invitation.specialist.user != user:
            raise PermissionDenied('Вы не можете принять это приглашение.')

        if invitation.is_accepted is not None:
            return Response({
                'detail': 'Приглашение уже обработано.'
            }, status=400)

        # Назначаем специалиста на вакансию
        invitation.required_specialist.specialist = invitation.specialist
        invitation.required_specialist.save()
        invitation.is_accepted = True
        invitation.save()

        # Системное сообщение стартаперу
        Message.objects.create(
            sender=None,
            recipient=invitation.startup.founder.user,
            text=f'Специалист {user.full_name} принял приглашение '
                 f'в стартап "{invitation.startup.title}".'
        )

        return Response({'detail': 'Приглашение принято.'})

    @action(detail=True, methods=['post'], url_path='decline')
    def decline_invitation(self, request, pk=None):
        invitation = self.get_object()
        user = request.user

        if invitation.specialist.user != user:
            raise PermissionDenied('Вы не можете отклонить это приглашение.')

        if invitation.is_accepted is not None:
            return Response({
                'detail': 'Приглашение уже обработано.'
            }, status=400)

        invitation.is_accepted = False
        invitation.save()

        # Системное сообщение стартаперу
        Message.objects.create(
            sender=None,
            recipient=invitation.startup.founder.user,
            text=f'Специалист {user.full_name} отклонил '
                 f'приглашение в стартап "{invitation.startup.title}".'
        )

        return Response({'detail': 'Приглашение отклонено.'})
