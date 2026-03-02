from rest_framework import serializers
from .models import UserFeedback, Review

class UserFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFeedback
        fields = [
            'id', 'user', 'name', 'email', 'feedback_type',
            'subject', 'message', 'rating', 'content_type',
            'object_id', 'attachment', 'status', 'response',
            'created_at'
        ]
        read_only_fields = ['status', 'response', 'user']

class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Review
        fields = [
            'id', 'user', 'username', 'attraction', 'title', 'body', 'rating',
            'rating_scenery', 'rating_accessibility', 'rating_value_for_money',
            'rating_safety', 'rating_facilities', 'visited_at', 'visit_type',
            'visit_season', 'photos', 'is_approved', 'helpful_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'is_approved', 'helpful_count', 'attraction']
