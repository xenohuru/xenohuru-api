from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from cloudinary.models import CloudinaryField

User = get_user_model()

class UserFeedback(models.Model):
    FEEDBACK_TYPES = [
        ('complaint', 'Complaint'),
        ('suggestion', 'Suggestion'),
        ('correction', 'Correction'),
        ('compliment', 'Compliment'),
        ('report_error', 'Report Error'),
        ('partnership_inquiry', 'Partnership Inquiry'),
        ('operator_inquiry', 'Operator Inquiry'),
        ('media_submission', 'Media Submission'),
        ('general', 'General'),
    ]

    STATUS_CHOICES = [
        ('new', 'New'),
        ('read', 'Read'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed'),
    ]

    # IDENTITY
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=200, blank=True, help_text='For anonymous users')
    email = models.EmailField(blank=True, help_text='For follow-up')

    # FEEDBACK TYPE
    feedback_type = models.CharField(max_length=50, choices=FEEDBACK_TYPES, default='general')

    # CONTENT
    subject = models.CharField(max_length=255)
    message = models.TextField()
    rating = models.IntegerField(null=True, blank=True, help_text='1-5 rating if applicable')

    # TARGET
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    # ATTACHMENTS
    attachment = CloudinaryField('attachment', blank=True, null=True, help_text='Screenshot/photo')

    # STATUS
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    admin_notes = models.TextField(blank=True, help_text='Internal notes')
    responded_at = models.DateTimeField(null=True, blank=True)
    response = models.TextField(blank=True, help_text='Public response shown to user')

    # META
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    
    # TIMESTAMPS
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'User Feedback'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_feedback_type_display()}: {self.subject}"


class Review(models.Model):
    # IDENTITY
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    attraction = models.ForeignKey('attractions.Attraction', on_delete=models.CASCADE, related_name='reviews')

    # CONTENT
    title = models.CharField(max_length=255, help_text='Review headline')
    body = models.TextField(help_text='Full review text')
    rating = models.IntegerField(help_text='Overall rating 1-5')

    # DETAILED RATINGS
    rating_scenery = models.IntegerField(null=True, blank=True, help_text='1-5')
    rating_accessibility = models.IntegerField(null=True, blank=True, help_text='1-5')
    rating_value_for_money = models.IntegerField(null=True, blank=True, help_text='1-5')
    rating_safety = models.IntegerField(null=True, blank=True, help_text='1-5')
    rating_facilities = models.IntegerField(null=True, blank=True, help_text='1-5')

    # VISIT CONTEXT
    VISIT_TYPES = [
        ('solo', 'Solo'),
        ('couple', 'Couple'),
        ('family', 'Family'),
        ('group', 'Group'),
        ('business', 'Business'),
    ]
    VISIT_SEASONS = [
        ('dry', 'Dry Season'),
        ('long_rains', 'Long Rains'),
        ('short_rains', 'Short Rains'),
    ]
    visited_at = models.DateField(null=True, blank=True, help_text='When they visited')
    visit_type = models.CharField(max_length=50, choices=VISIT_TYPES, blank=True)
    visit_season = models.CharField(max_length=50, choices=VISIT_SEASONS, blank=True)

    # MEDIA
    photos = models.ManyToManyField('media.Media', blank=True, related_name='reviews')

    # MODERATION
    is_approved = models.BooleanField(default=False)
    is_flagged = models.BooleanField(default=False, help_text='Reported by users')
    helpful_count = models.IntegerField(default=0, help_text='Upvotes')
    
    # TIMESTAMPS
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'attraction')
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.user.username} for {self.attraction.name}"
