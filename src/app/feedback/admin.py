from django.contrib import admin
from .models import UserFeedback, Review

@admin.register(UserFeedback)
class UserFeedbackAdmin(admin.ModelAdmin):
    list_display = ['subject', 'feedback_type', 'status', 'user', 'created_at']
    list_filter = ['feedback_type', 'status', 'created_at']
    search_fields = ['subject', 'message', 'name', 'email']
    readonly_fields = ['created_at', 'updated_at', 'ip_address', 'user_agent']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['attraction', 'user', 'rating', 'is_approved', 'is_flagged', 'created_at']
    list_filter = ['is_approved', 'is_flagged', 'rating', 'visit_type', 'visit_season']
    search_fields = ['title', 'body', 'user__username', 'attraction__name']
    readonly_fields = ['created_at', 'updated_at', 'helpful_count']
