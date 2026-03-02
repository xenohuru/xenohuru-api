from django.urls import path
from .views import submit_feedback, review_detail

urlpatterns = [
    path('submit/', submit_feedback, name='submit-feedback'),
    path('reviews/<int:pk>/', review_detail, name='review-detail'),
]
