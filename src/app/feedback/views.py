from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .models import UserFeedback, Review
from .serializers import UserFeedbackSerializer, ReviewSerializer
from app.attractions.models import Attraction


@extend_schema(
    tags=['Feedback'],
    summary='Submit user feedback',
    responses={201: OpenApiResponse(response=UserFeedbackSerializer)}
)
@api_view(['POST'])
@permission_classes([AllowAny])
def submit_feedback(request):
    serializer = UserFeedbackSerializer(data=request.data)
    if serializer.is_valid():
        if request.user.is_authenticated:
            serializer.save(user=request.user)
        else:
            serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=['Reviews'],
    summary='List reviews for an attraction',
    responses={200: OpenApiResponse(response=ReviewSerializer(many=True))}
)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def attraction_reviews(request, slug):
    attraction = get_object_or_404(Attraction, slug=slug)
    
    if request.method == 'GET':
        reviews = Review.objects.filter(attraction=attraction, is_approved=True)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)
        
    elif request.method == 'POST':
        if Review.objects.filter(attraction=attraction, user=request.user).exists():
            return Response({'error': 'You have already reviewed this attraction'}, status=status.HTTP_400_BAD_REQUEST)
            
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, attraction=attraction)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=['Reviews'],
    summary='Retrieve, update or delete a review',
    responses={
        200: OpenApiResponse(response=ReviewSerializer),
        204: OpenApiResponse(description='Deleted successfully')
    }
)
@api_view(['GET', 'PATCH', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly])
def review_detail(request, pk):
    review = get_object_or_404(Review, pk=pk)
    
    if request.method == 'GET':
        if not review.is_approved and request.user != review.user and not request.user.is_staff:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ReviewSerializer(review)
        return Response(serializer.data)
        
    elif request.method in ['PATCH', 'PUT']:
        if request.user != review.user and not request.user.is_staff:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
            
        serializer = ReviewSerializer(review, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    elif request.method == 'DELETE':
        if request.user == review.user or request.user.is_staff:
            review.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
