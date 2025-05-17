from rest_framework import serializers

from startups.models import Startup
from users.models import SpecialistProfile, InvestorProfile
from .models import Favorite


class FavoriteCreateSerializer(serializers.ModelSerializer):
    specialist_id = serializers.PrimaryKeyRelatedField(
        queryset=SpecialistProfile.objects.all(), source='specialist', required=False, write_only=True
    )
    investor_id = serializers.PrimaryKeyRelatedField(
        queryset=InvestorProfile.objects.all(), source='investor', required=False, write_only=True
    )
    startup_id = serializers.PrimaryKeyRelatedField(
        queryset=Startup.objects.all(), source='startup', required=False, write_only=True
    )

    class Meta:
        model = Favorite
        fields = ['id', 'specialist_id', 'investor_id', 'startup_id']

    def validate(self, attrs):
        user = self.context['request'].user
        specialist = attrs.get('specialist')
        investor = attrs.get('investor')
        startup = attrs.get('startup')

        if not any([specialist, investor, startup]):
            raise serializers.ValidationError(
                "Нужно указать хотя бы одно из полей: specialist_id, investor_id или startup_id")

        if sum(map(bool, [specialist, investor, startup])) > 1:
            raise serializers.ValidationError(
                "Можно указать только одно поле из: specialist_id, investor_id, startup_id")

        # Проверка на дубликат
        if Favorite.objects.filter(user=user, specialist=specialist, investor=investor, startup=startup).exists():
            raise serializers.ValidationError("Такая запись уже добавлена в избранное")

        return attrs
