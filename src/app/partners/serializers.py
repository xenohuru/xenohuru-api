from rest_framework import serializers
from .models import Partner


class PartnerSerializer(serializers.ModelSerializer):
    tier_display = serializers.CharField(source='get_tier_display', read_only=True)

    class Meta:
        model = Partner
        fields = [
            'id', 'name', 'slug', 'description', 'logo', 'website',
            'tier', 'tier_display', 'is_active', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']
