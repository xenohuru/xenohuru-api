from rest_framework import serializers
from .models import Attraction, AttractionImage, AttractionTip, EndemicSpecies, AttractionBoundary, Citation
from app.regions.serializers import RegionSerializer


class AttractionImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttractionImage
        fields = ['id', 'image', 'caption', 'order']


class AttractionTipSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = AttractionTip
        fields = ['id', 'title', 'description', 'created_by_username', 'created_at']


class EndemicSpeciesSerializer(serializers.ModelSerializer):
    conservation_status_display = serializers.CharField(source='get_conservation_status_display', read_only=True)

    class Meta:
        model = EndemicSpecies
        fields = [
            'id', 'common_name', 'scientific_name', 'description',
            'image', 'conservation_status', 'conservation_status_display', 'created_at',
        ]


class AttractionBoundarySerializer(serializers.ModelSerializer):
    class Meta:
        model = AttractionBoundary
        fields = [
            'id', 'attraction', 'boundary_type', 'geojson',
            'center_latitude', 'center_longitude', 'radius_km',
            'bbox_north', 'bbox_south', 'bbox_east', 'bbox_west',
            'area_sq_km', 'perimeter_km', 'elevation_min_m', 'elevation_max_m',
            'main_gate_latitude', 'main_gate_longitude', 'main_gate_name',
            'entry_points', 'zones', 'created_at', 'updated_at'
        ]


class CitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Citation
        fields = [
            'id', 'title', 'author', 'year', 'citation_type',
            'publisher', 'journal', 'doi', 'url', 'isbn', 'accessed_date',
            'formatted_citation', 'is_primary_source', 'trust_score', 'created_at'
        ]


class AttractionListSerializer(serializers.ModelSerializer):
    region_name = serializers.CharField(source='region.name', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    difficulty_display = serializers.CharField(source='get_difficulty_level_display', read_only=True)

    class Meta:
        model = Attraction
        fields = [
            'id', 'name', 'slug', 'region_name', 'category', 'category_display',
            'short_description', 'difficulty_level', 'difficulty_display',
            'featured_image', 'is_featured', 'best_time_to_visit'
        ]


class AttractionDetailSerializer(serializers.ModelSerializer):
    region = RegionSerializer(read_only=True)
    images = AttractionImageSerializer(many=True, read_only=True)
    tips = AttractionTipSerializer(many=True, read_only=True)
    endemic_species = EndemicSpeciesSerializer(many=True, read_only=True)
    boundary = AttractionBoundarySerializer(read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    difficulty_display = serializers.CharField(source='get_difficulty_level_display', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Attraction
        fields = [
            'id', 'name', 'slug', 'region', 'category', 'category_display',
            'description', 'short_description', 'latitude', 'longitude', 'altitude',
            'difficulty_level', 'difficulty_display', 'access_info', 'nearest_airport',
            'distance_from_airport', 'best_time_to_visit', 'seasonal_availability',
            'estimated_duration', 'entrance_fee', 'requires_guide', 'requires_permit',
            'featured_image', 'images', 'tips', 'endemic_species', 'boundary', 'is_featured',
            'created_by_username', 'created_at', 'updated_at'
        ]


class AttractionCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attraction
        fields = [
            'name', 'slug', 'region', 'category', 'description', 'short_description',
            'latitude', 'longitude', 'altitude', 'difficulty_level', 'access_info',
            'nearest_airport', 'distance_from_airport', 'best_time_to_visit',
            'seasonal_availability', 'estimated_duration', 'entrance_fee',
            'requires_guide', 'requires_permit', 'featured_image'
        ]
