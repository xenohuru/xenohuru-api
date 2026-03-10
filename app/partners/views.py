from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from .models import Partner
from .serializers import PartnerSerializer

BASE_QUERYSET = Partner.objects.filter(is_active=True)


@extend_schema(
    tags=['Partners'],
    summary='List or submit a partner',
    description=(
        '**GET** — Returns all active partners. Supports optional filter:\n\n'
        '| Parameter | Type | Description |\n'
        '|-----------|------|-------------|\n'
        '| `tier` | string | Filter by tier: `platinum`, `gold`, `silver`, `community` |\n\n'
        '**POST** — Submit a partner application. Requires authentication.\n\n'
        '**curl GET example:**\n'
        '```bash\n'
        'curl "https://xenohuru-o7ix53tg.b4a.run/api/v1/partners/"\n'
        '```'
    ),
    parameters=[
        OpenApiParameter('tier', description='Filter by tier', required=False, type=str,
                         enum=['platinum', 'gold', 'silver', 'community']),
    ],
    request=PartnerSerializer,
    responses={
        200: OpenApiResponse(response=PartnerSerializer(many=True), description='List of active partners.'),
        201: OpenApiResponse(response=PartnerSerializer, description='Partner created.'),
        400: OpenApiResponse(description='Validation error.'),
        401: OpenApiResponse(description='Authentication required for POST.'),
    },
)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def partner_list_create(request):
    if request.method == 'GET':
        partners = BASE_QUERYSET
        tier = request.query_params.get('tier')
        if tier:
            partners = partners.filter(tier=tier)
        serializer = PartnerSerializer(partners, many=True)
        return Response(serializer.data)
    serializer = PartnerSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=['Partners'],
    summary='Retrieve, update or delete a partner',
    description=(
        'Look up a partner by its `slug`.\n\n'
        '- **GET** — Public. Returns full partner detail.\n'
        '- **PUT/PATCH** — Update. Authentication required.\n'
        '- **DELETE** — Remove partner. Authentication required.\n\n'
        '**curl GET example:**\n'
        '```bash\n'
        'curl https://xenohuru-o7ix53tg.b4a.run/api/v1/partners/acacia-foundation/\n'
        '```'
    ),
    responses={
        200: OpenApiResponse(response=PartnerSerializer, description='Partner detail.'),
        204: OpenApiResponse(description='Partner deleted.'),
        401: OpenApiResponse(description='Authentication required for write operations.'),
        404: OpenApiResponse(description='Partner not found.'),
    },
)
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly])
def partner_detail(request, slug):
    try:
        partner = BASE_QUERYSET.get(slug=slug)
    except Partner.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = PartnerSerializer(partner)
        return Response(serializer.data)
    elif request.method in ['PUT', 'PATCH']:
        serializer = PartnerSerializer(partner, data=request.data, partial=request.method == 'PATCH')
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        partner.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
