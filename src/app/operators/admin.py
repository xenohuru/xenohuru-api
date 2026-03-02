from django.contrib import admin
from .models import TourOperator


@admin.register(TourOperator)
class TourOperatorAdmin(admin.ModelAdmin):
    list_display = ['name', 'tier', 'is_verified', 'is_active', 'created_at']
    list_filter = ['tier', 'is_verified', 'is_active']
    search_fields = ['name', 'description', 'email']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ['attractions']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'short_description', 'description', 'logo')
        }),
        ('Contact', {
            'fields': ('website', 'phone', 'email')
        }),
        ('Classification', {
            'fields': ('tier', 'is_verified', 'is_active')
        }),
        ('Attractions Covered', {
            'fields': ('attractions',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
