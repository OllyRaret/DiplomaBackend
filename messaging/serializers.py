from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from startups.models import RequiredSpecialist
from startups.serializers import RequiredSpecialistSerializer
from users.models import User
from users.serializers import CustomUserSerializer, SpecialistShortSerializer
from .models import Message, Invitation


class MessageSerializer(serializers.ModelSerializer):
    sender = CustomUserSerializer(read_only=True)
    recipient = CustomUserSerializer(read_only=True)
    recipient_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='recipient', write_only=True
    )

    class Meta:
        model = Message
        fields = [
            'id', 'sender', 'recipient', 'recipient_id',
            'text', 'timestamp', 'is_read'
        ]
        read_only_fields = ['id', 'sender', 'timestamp', 'is_read']

    def validate(self, data):
        sender = self.context['request'].user
        recipient = data.get('recipient')

        # Проверка на отправку самому себе
        if sender.id == recipient.id:
            raise serializers.ValidationError(
                'Нельзя отправить сообщение самому себе.'
            )

        return data


class InvitationSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True
    )
    specialist = SpecialistShortSerializer(read_only=True)

    required_specialist_id = serializers.PrimaryKeyRelatedField(
        queryset=RequiredSpecialist.objects.all(),
        source='required_specialist',
        write_only=True
    )
    required_specialist = RequiredSpecialistSerializer(read_only=True)

    class Meta:
        model = Invitation
        fields = [
            'id',
            'user_id', 'required_specialist_id',
            'specialist', 'required_specialist',
            'is_accepted', 'created_at',
        ]
        read_only_fields = ['id', 'startup', 'is_accepted', 'created_at']

    def validate(self, data):
        user = self.context['request'].user
        if not hasattr(user, 'founder_profile'):
            raise serializers.ValidationError(
                'Только стартаперы могут отправлять приглашения.'
            )

        invited_user = data['user_id']
        if not hasattr(invited_user, 'specialist_profile'):
            raise serializers.ValidationError(
                'Указанный пользователь не является специалистом.'
            )

        required_specialist = data['required_specialist']
        specialist = invited_user.specialist_profile
        startup = required_specialist.startup

        if required_specialist.specialist is not None:
            raise serializers.ValidationError('Эта вакансия уже занята.')

        if Invitation.objects.filter(
                required_specialist=required_specialist,
                is_accepted=None
        ).exists():
            raise serializers.ValidationError(
                'Уже есть активное приглашение на эту вакансию.'
            )

        if specialist.user == user:
            raise serializers.ValidationError('Нельзя приглашать самого себя.')

        # Нельзя пригласить специалиста на другую вакансию в том же стартапе
        already_invited = Invitation.objects.filter(
            startup=startup,
            specialist=specialist,
            is_accepted=None
        ).exists()

        already_assigned = RequiredSpecialist.objects.filter(
            startup=startup,
            specialist=specialist
        ).exists()

        if already_invited or already_assigned:
            raise serializers.ValidationError(
                'Этот специалист уже приглашён '
                'или назначен на другую вакансию в этом стартапе.'
            )

        data['specialist'] = specialist
        data.pop('user_id')

        return data

    def create(self, validated_data):
        founder = self.context['request'].user.founder_profile
        startup = validated_data['required_specialist'].startup

        if startup.founder != founder:
            raise PermissionDenied('Вы не владелец стартапа.')

        invitation = Invitation.objects.create(
            startup=startup, **validated_data
        )

        # Отправка системного сообщения специалисту
        Message.objects.create(
            sender=None,
            recipient=invitation.specialist.user,
            text=f'Вы были приглашены в стартап "{startup.title}" '
                 f'на вакансию '
                 f'{invitation.required_specialist.profession.name}.'
        )

        return invitation
