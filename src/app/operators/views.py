from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from .models import TourOperator
from .serializers import (
    TourOperatorListSerializer,
    TourOperatorDetailSerializer,
    TourOperatorCreateUpdateSerializer,
)

BASE_QUERYSET = TourOperator.objects.filter(is_active=True).prefetch_related('attractions')


@extend_schema(
    tags=['Operators'],
    summary='List or submit a tour operator',
    description=(
        '**GET** — Returns all active tour operators. Supports optional query parameters:\n\n'
        '| Parameter | Type | Description |\n'
        '|-----------|------|-------------|\n'
        '| `search` | string | Filter by name or description |\n'
        '| `tier` | string | Filter by tier: `budget`, `mid`, `luxury` |\n\n'
        '**POST** — Submit a new tour operator. Requires authentication.\n\n'
        '**curl GET example:**\n'
        '```bash\n'
        'curl "https://cf89615f228bb45cc805447510de80.pythonanywhere.com/api/v1/operators/"\n'
        '```'
    ),
    parameters=[
        OpenApiParameter('search', description='Filter by name or description', required=False, type=str),
        OpenApiParameter('tier', description='Filter by tier: `budget`, `mid`, `luxury`', required=False, type=str,
                         enum=['budget', 'mid', 'luxury']),
    ],
    request=TourOperatorCreateUpdateSerializer,
    responses={
        200: OpenApiResponse(response=TourOperatorListSerializer(many=True), description='List of active operators.'),
        201: OpenApiResponse(response=TourOperatorCreateUpdateSerializer, description='Operator created.'),
        400: OpenApiResponse(description='Validation error.'),
        401: OpenApiResponse(description='Authentication required for POST.'),
    },
)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def operator_list_create(request):
    if request.method == 'GET':
        operators = BASE_QUERYSET
        search = request.query_params.get('search')
        if search:
            operators = operators.filter(name__icontains=search) | \
                        operators.filter(description__icontains=search)
        tier = request.query_params.get('tier')
        if tier:
            operators = operators.filter(tier=tier)
        serializer = TourOperatorListSerializer(operators, many=True)
        return Response(serializer.data)
    serializer = TourOperatorCreateUpdateSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=['Operators'],
    summary='Retrieve, update or delete a tour operator',
    description=(
        'Look up a tour operator by its `slug`.\n\n'
        '- **GET** — Public. Returns full operator detail including covered attraction slugs.\n'
        '- **PUT/PATCH** — Update. Authentication required.\n'
        '- **DELETE** — Remove operator. Authentication required.\n\n'
        '**curl GET example:**\n'
        '```bash\n'
        'curl https://cf89615f228bb45cc805447510de80.pythonanywhere.com/api/v1/operators/serengeti-adventures/\n'
        '```'
    ),
    responses={
        200: OpenApiResponse(response=TourOperatorDetailSerializer, description='Full operator detail.'),
        204: OpenApiResponse(description='Operator deleted.'),
        401: OpenApiResponse(description='Authentication required for write operations.'),
        404: OpenApiResponse(description='Operator not found.'),
    },
)
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly])
def operator_detail(request, slug):
    try:
        operator = BASE_QUERYSET.get(slug=slug)
    except TourOperator.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = TourOperatorDetailSerializer(operator)
        return Response(serializer.data)
    elif request.method in ['PUT', 'PATCH']:
        serializer = TourOperatorCreateUpdateSerializer(operator, data=request.data, partial=request.method == 'PATCH')
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        operator.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    tags=['Operators'],
    summary='Tour operators by attraction',
    description=(
        'Returns all active, verified tour operators that cover the given attraction.\n\n'
        '**curl example:**\n'
        '```bash\n'
        'curl "https://cf89615f228bb45cc805447510de80.pythonanywhere.com/api/v1/operators/by_attraction/?attraction=mount-kilimanjaro"\n'
        '```'
    ),
    parameters=[
        OpenApiParameter(
            'attraction',
            description='Attraction slug (e.g. `mount-kilimanjaro`). See `GET /api/v1/attractions/` for all slugs.',
            required=True,
            type=str,
        ),
    ],
    responses={
        200: OpenApiResponse(response=TourOperatorListSerializer(many=True), description='Operators for the given attraction.'),
        400: OpenApiResponse(description='`attraction` query parameter is required.'),
    },
)
@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def operators_by_attraction(request):
    attraction_slug = request.query_params.get('attraction')
    if not attraction_slug:
        return Response({'error': 'attraction parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
    operators = BASE_QUERYSET.filter(attractions__slug=attraction_slug)
    serializer = TourOperatorListSerializer(operators, many=True)
    return Response(serializer.data)
