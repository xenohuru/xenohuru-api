from django.db import models
from cloudinary.models import CloudinaryField
from app.attractions.models import Attraction
from app.core.mixins import SEOMixin


class TourOperator(SEOMixin, models.Model):
    TIER_CHOICES = [
        ('budget', 'Budget'),
        ('mid', 'Mid-Range'),
        ('luxury', 'Luxury'),
    ]

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=300)
    logo = CloudinaryField('image', blank=True, null=True)
    website = models.URLField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    attractions = models.ManyToManyField(
        Attraction,
        blank=True,
        related_name='operators',
        help_text='Attractions this operator covers'
    )
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, default='mid')
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_verified', 'name']
        indexes = [
            models.Index(fields=['tier']),
            models.Index(fields=['is_verified']),
        ]

    def __str__(self):
        return self.name
