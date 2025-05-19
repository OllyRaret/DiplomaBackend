from rest_framework import serializers

from startups.models import Startup
from users.models import User
from .models import Favorite


class FavoriteCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, required=False
    )
    startup_id = serializers.PrimaryKeyRelatedField(
        queryset=Startup.objects.all(),
        source='startup',
        required=False,
        write_only=True
    )

    class Meta:
        model = Favorite
        fields = ['id', 'user_id', 'startup_id']

    def validate(self, attrs):
        user = self.context['request'].user
        target_user = attrs.get('user_id')
        startup = attrs.get('startup')

        specialist = None
        investor = None

        if not target_user and not startup:
            raise serializers.ValidationError(
                'Нужно указать либо user_id специалиста/инвестора, '
                'либо startup_id.'
            )

        if target_user and startup:
            raise serializers.ValidationError(
                'Можно указать только одно из: user_id или startup_id.'
            )

        # Обработка user_id: определяем профиль
        if target_user:
            if hasattr(target_user, 'specialist_profile'):
                specialist = target_user.specialist_profile
            elif hasattr(target_user, 'investor_profile'):
                investor = target_user.investor_profile
            else:
                raise serializers.ValidationError(
                    'Указанный пользователь не является '
                    'специалистом или инвестором.'
                )

        # Проверка на дубликат
        if Favorite.objects.filter(
                user=user, specialist=specialist,
                investor=investor, startup=startup
        ).exists():
            raise serializers.ValidationError(
                'Такая запись уже добавлена в избранное'
            )

        # Устанавливаем профиль в validated_data
        if specialist:
            attrs['specialist'] = specialist
        if investor:
            attrs['investor'] = investor
        attrs.pop('user_id', None)

        return attrs
