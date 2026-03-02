from django.db import models
from cloudinary.models import CloudinaryField
from app.core.mixins import SEOMixin


class Partner(SEOMixin, models.Model):
    TIER_CHOICES = [
        ('platinum', 'Platinum'),
        ('gold', 'Gold'),
        ('silver', 'Silver'),
        ('community', 'Community'),
    ]

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    logo = CloudinaryField('image', blank=True, null=True)
    website = models.URLField(blank=True)
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, default='community')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['tier', 'name']
        indexes = [
            models.Index(fields=['tier']),
        ]

    def __str__(self):
        return f'{self.name} ({self.get_tier_display()})'
