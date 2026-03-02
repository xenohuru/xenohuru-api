from rest_framework import serializers
from .models import TourOperator


class TourOperatorListSerializer(serializers.ModelSerializer):
    tier_display = serializers.CharField(source='get_tier_display', read_only=True)

    class Meta:
        model = TourOperator
        fields = [
            'id', 'name', 'slug', 'short_description', 'logo',
            'tier', 'tier_display', 'is_verified', 'website',
        ]


class TourOperatorDetailSerializer(serializers.ModelSerializer):
    tier_display = serializers.CharField(source='get_tier_display', read_only=True)
    attraction_slugs = serializers.SerializerMethodField()

    class Meta:
        model = TourOperator
        fields = [
            'id', 'name', 'slug', 'description', 'short_description', 'logo',
            'website', 'phone', 'email', 'tier', 'tier_display',
            'is_verified', 'attraction_slugs', 'created_at', 'updated_at',
        ]

    def get_attraction_slugs(self, obj):
        return list(obj.attractions.values_list('slug', flat=True))


class TourOperatorCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourOperator
        fields = [
            'name', 'slug', 'description', 'short_description', 'logo',
            'website', 'phone', 'email', 'attractions', 'tier',
        ]
