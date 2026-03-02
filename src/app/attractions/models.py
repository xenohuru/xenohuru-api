from django.db import models
from django.contrib.auth import get_user_model
from cloudinary.models import CloudinaryField
from app.regions.models import Region
from app.core.mixins import SEOMixin

User = get_user_model()


class Attraction(SEOMixin, models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('moderate', 'Moderate'),
        ('challenging', 'Challenging'),
        ('difficult', 'Difficult'),
        ('extreme', 'Extreme'),
    ]

    CATEGORY_CHOICES = [
        ('mountain', 'Mountain'),
        ('beach', 'Beach'),
        ('wildlife', 'Wildlife Safari'),
        ('cultural', 'Cultural Site'),
        ('historical', 'Historical Site'),
        ('adventure', 'Adventure Activity'),
        ('national_park', 'National Park'),
        ('island', 'Island'),
        ('waterfall', 'Waterfall'),
        ('lake', 'Lake'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='attractions')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField()
    short_description = models.CharField(max_length=300)
    
    # Location data
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    altitude = models.IntegerField(help_text='Altitude in meters', null=True, blank=True)
    
    # Difficulty & Access
    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    access_info = models.TextField(help_text='How to reach this attraction')
    nearest_airport = models.CharField(max_length=100, blank=True)
    distance_from_airport = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text='Distance in km')
    
    # Seasonal info
    best_time_to_visit = models.CharField(max_length=200)
    seasonal_availability = models.TextField(help_text='When is this attraction accessible?')
    
    # Practical info
    estimated_duration = models.CharField(max_length=100, help_text='e.g., 5-7 days, 2 hours')
    entrance_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text='Fee in USD')
    requires_guide = models.BooleanField(default=False)
    requires_permit = models.BooleanField(default=False)
    
    # Media
    featured_image = CloudinaryField('image')
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_attractions')
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', '-created_at']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['region']),
            models.Index(fields=['difficulty_level']),
        ]

    def __str__(self):
        return self.name


class AttractionImage(models.Model):
    attraction = models.ForeignKey(Attraction, on_delete=models.CASCADE, related_name='images')
    image = CloudinaryField('image')
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-uploaded_at']

    def __str__(self):
        return f"{self.attraction.name} - Image {self.order}"


class AttractionTip(models.Model):
    attraction = models.ForeignKey(Attraction, on_delete=models.CASCADE, related_name='tips')
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.attraction.name} - {self.title}"


class EndemicSpecies(models.Model):
    CONSERVATION_STATUS_CHOICES = [
        ('LC', 'Least Concern'),
        ('NT', 'Near Threatened'),
        ('VU', 'Vulnerable'),
        ('EN', 'Endangered'),
        ('CR', 'Critically Endangered'),
        ('EW', 'Extinct in the Wild'),
        ('EX', 'Extinct'),
    ]

    attraction = models.ForeignKey(
        Attraction, on_delete=models.CASCADE,
        related_name='endemic_species'
    )
    common_name = models.CharField(max_length=200)
    scientific_name = models.CharField(max_length=200, blank=True)
    description = models.TextField()
    image = CloudinaryField('image', blank=True, null=True)
    conservation_status = models.CharField(
        max_length=2, choices=CONSERVATION_STATUS_CHOICES, default='LC'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['common_name']
        verbose_name_plural = 'Endemic Species'

    def __str__(self):
        return f"{self.common_name} ({self.attraction.name})"


class AttractionBoundary(models.Model):
    BOUNDARY_TYPES = [
        ('polygon', 'Polygon'),
        ('circle', 'Circle'),
        ('corridor', 'Corridor'),
        ('point_cluster', 'Point Cluster'),
    ]

    attraction = models.OneToOneField(Attraction, on_delete=models.CASCADE, related_name='boundary')
    boundary_type = models.CharField(max_length=50, choices=BOUNDARY_TYPES)
    
    # POLYGON
    geojson = models.JSONField(null=True, blank=True, help_text='Full GeoJSON polygon/multipolygon')

    # CIRCLE
    center_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    center_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    radius_km = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    # BOUNDING BOX
    bbox_north = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    bbox_south = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    bbox_east = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    bbox_west = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # AREA INFO
    area_sq_km = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    perimeter_km = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    elevation_min_m = models.IntegerField(null=True, blank=True)
    elevation_max_m = models.IntegerField(null=True, blank=True)

    # ENTRY POINTS
    main_gate_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    main_gate_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    main_gate_name = models.CharField(max_length=200, blank=True)
    entry_points = models.JSONField(null=True, blank=True, help_text='List of {name, lat, lng, type}')

    # ZONES WITHIN
    zones = models.JSONField(null=True, blank=True, help_text='[{name, description, geojson}]')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Attraction Boundaries'

    def __str__(self):
        return f"Boundary for {self.attraction.name}"


class Citation(models.Model):
    CITATION_TYPES = [
        ('research_paper', 'Research Paper'),
        ('book', 'Book'),
        ('government_report', 'Government Report'),
        ('news', 'News Article'),
        ('website', 'Website'),
        ('ngo_report', 'NGO Report'),
        ('documentary', 'Documentary'),
    ]

    # CORE
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, blank=True)
    year = models.IntegerField(null=True, blank=True)
    citation_type = models.CharField(max_length=50, choices=CITATION_TYPES)

    # SOURCE DETAILS
    publisher = models.CharField(max_length=255, blank=True)
    journal = models.CharField(max_length=255, blank=True)
    doi = models.CharField(max_length=100, blank=True)
    url = models.URLField(blank=True)
    isbn = models.CharField(max_length=50, blank=True)
    accessed_date = models.DateField(null=True, blank=True)

    # RELATIONSHIPS
    attractions = models.ManyToManyField(Attraction, blank=True, related_name='citations')
    regions = models.ManyToManyField('regions.Region', blank=True, related_name='citations')
    endemic_species = models.ManyToManyField(EndemicSpecies, blank=True, related_name='citations')
    articles = models.ManyToManyField('blog.Article', blank=True, related_name='citations')

    # DISPLAY
    formatted_citation = models.TextField(blank=True, help_text='Auto-generated APA format')
    is_primary_source = models.BooleanField(default=False)
    trust_score = models.IntegerField(null=True, blank=True, help_text='1-5 rating')
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-year', 'title']

    def __str__(self):
        return self.title
