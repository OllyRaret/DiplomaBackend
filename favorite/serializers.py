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
        if not any([attrs.get('specialist'), attrs.get('investor'), attrs.get('startup')]):
            raise serializers.ValidationError("Нужно указать хотя бы одно из полей: specialist_id, investor_id или startup_id")
        return attrs
