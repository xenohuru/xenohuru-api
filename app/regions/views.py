from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from .models import Region
from .serializers import RegionSerializer

_REGION_EXAMPLE = {
    'id': 1,
    'name': 'Arusha',
    'slug': 'arusha',
    'description': 'The safari capital of Tanzania, gateway to Serengeti and Kilimanjaro.',
    'image': 'https://res.cloudinary.com/demo/image/upload/arusha.jpg',
    'latitude': '-3.3869',
    'longitude': '36.6830',
    'attraction_count': 12,
    'created_at': '2026-01-01T00:00:00Z',
}


@extend_schema(
    tags=['Regions'],
    summary='List or create regions',
    description=(
        '**GET** — Returns all Tanzania regions ordered by name. Each region includes an `attraction_count`.\n\n'
        '**POST** — Create a new region. Requires authentication.\n\n'
        '**Required fields (POST):** `name`, `slug`, `description`, `latitude`, `longitude`\n\n'
        '**curl GET example:**\n'
        '```bash\n'
        'curl https://xenohuru-o7ix53tg.b4a.run/api/v1/regions/\n'
        '```\n\n'
        '**curl POST example:**\n'
        '```bash\n'
        'curl -X POST https://xenohuru-o7ix53tg.b4a.run/api/v1/regions/ \\\n'
        '  -H "Authorization: Bearer <access_token>" \\\n'
        '  -H "Content-Type: application/json" \\\n'
        '  -d \'{"name":"Arusha","slug":"arusha","description":"Safari capital of Tanzania.",'
        '"latitude":"-3.3869","longitude":"36.6830"}\'\n'
        '```'
    ),
    request=RegionSerializer,
    responses={
        200: OpenApiResponse(
            response=RegionSerializer(many=True),
            description='List of all regions.',
            examples=[OpenApiExample('Regions list', value=[_REGION_EXAMPLE])],
        ),
        201: OpenApiResponse(
            response=RegionSerializer,
            description='Region created successfully.',
            examples=[OpenApiExample('Created region', value=_REGION_EXAMPLE)],
        ),
        400: OpenApiResponse(description='Validation error — check required fields or duplicate slug/name.'),
        401: OpenApiResponse(description='Authentication required for POST.'),
    },
    examples=[
        OpenApiExample(
            'Create region',
            request_only=True,
            value={
                'name': 'Arusha',
                'slug': 'arusha',
                'description': 'Safari capital of Tanzania, gateway to Serengeti and Kilimanjaro.',
                'latitude': '-3.3869',
                'longitude': '36.6830',
            },
        )
    ],
)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def region_list_create(request):
    if request.method == 'GET':
        regions = Region.objects.all()
        serializer = RegionSerializer(regions, many=True)
        return Response(serializer.data)
    serializer = RegionSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=['Regions'],
    summary='Retrieve, update or delete a region',
    description=(
        'Look up a region by its `slug` (e.g. `arusha`, `zanzibar`, `kilimanjaro`).\n\n'
        '- **GET** — Public. Returns region details including `attraction_count`.\n'
        '- **PUT** — Full replace. All writable fields required. Authentication required.\n'
        '- **PATCH** — Partial update. Send only the fields to change. Authentication required.\n'
        '- **DELETE** — Removes the region and **cascades** to all its attractions. Authentication required.\n\n'
        '**curl GET example:**\n'
        '```bash\n'
        'curl https://xenohuru-o7ix53tg.b4a.run/api/v1/regions/arusha/\n'
        '```\n\n'
        '**curl PATCH example:**\n'
        '```bash\n'
        'curl -X PATCH https://xenohuru-o7ix53tg.b4a.run/api/v1/regions/arusha/ \\\n'
        '  -H "Authorization: Bearer <access_token>" \\\n'
        '  -H "Content-Type: application/json" \\\n'
        '  -d \'{"description":"Updated description."}\'\n'
        '```'
    ),
    request=RegionSerializer,
    responses={
        200: OpenApiResponse(
            response=RegionSerializer,
            description='Region details.',
            examples=[OpenApiExample('Region detail', value=_REGION_EXAMPLE)],
        ),
        204: OpenApiResponse(description='Region deleted. All associated attractions are also deleted (cascade).'),
        401: OpenApiResponse(description='Authentication required for write operations.'),
        404: OpenApiResponse(
            description='No region found with the given slug.',
            examples=[OpenApiExample('Not found', value={'error': 'Not found'})],
        ),
    },
    examples=[
        OpenApiExample(
            'Partial update (PATCH)',
            request_only=True,
            value={'description': 'Updated region description.'},
        )
    ],
)
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly])
def region_detail(request, slug):
    try:
        region = Region.objects.get(slug=slug)
    except Region.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = RegionSerializer(region)
        return Response(serializer.data)
    elif request.method in ['PUT', 'PATCH']:
        serializer = RegionSerializer(region, data=request.data, partial=request.method == 'PATCH')
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        region.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
