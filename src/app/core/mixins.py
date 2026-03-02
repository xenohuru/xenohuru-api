from django.db import models

class SEOMixin(models.Model):
    meta_title = models.CharField(max_length=60, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    meta_keywords = models.CharField(max_length=255, blank=True)
    og_title = models.CharField(max_length=100, blank=True)
    og_description = models.CharField(max_length=200, blank=True)
    og_image = models.ForeignKey(
        'media.Media',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',
        help_text='Social share image'
    )
    canonical_url = models.URLField(blank=True)
    schema_type = models.CharField(
        max_length=50,
        blank=True,
        choices=[
            ('TouristAttraction', 'Tourist Attraction'),
            ('Article', 'Article'),
            ('Person', 'Person'),
            ('Organization', 'Organization'),
        ]
    )
    schema_json = models.JSONField(null=True, blank=True, help_text='Full JSON-LD structured data')
    no_index = models.BooleanField(default=False, help_text='Hide from search engines')
    sitemap_priority = models.DecimalField(max_digits=2, decimal_places=1, default=0.5)
    sitemap_changefreq = models.CharField(
        max_length=20,
        choices=[
            ('always', 'Always'),
            ('hourly', 'Hourly'),
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ('yearly', 'Yearly'),
            ('never', 'Never'),
        ],
        default='monthly'
    )

    class Meta:
        abstract = True
