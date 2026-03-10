from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.core.cache import cache
from django.shortcuts import get_object_or_404
import math
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse

from .models import Attraction, EndemicSpecies, AttractionBoundary, Citation, NearestTransport
from .serializers import (
    AttractionListSerializer,
    AttractionDetailSerializer,
    AttractionCreateUpdateSerializer,
    EndemicSpeciesSerializer,
    AttractionBoundarySerializer,
    CitationSerializer,
    NearestTransportSerializer,
)

BASE_QUERYSET = Attraction.objects.filter(is_active=True).select_related('region', 'created_by').prefetch_related('images', 'tips', 'endemic_species')


@extend_schema(
    tags=['Attractions'],
    summary='List or create attractions',
    description=(
        '**GET** — Returns all active attractions. Supports optional query parameters:\n\n'
        '| Parameter | Type | Description |\n'
        '|-----------|------|-------------|\n'
        '| `search` | string | Filter by name, description, short description, or region name |\n'
        '| `category` | string | Filter by category (e.g. `mountain`, `national_park`, `wildlife`, `beach`, `cultural`) |\n'
        '| `region` | string | Filter by region slug (e.g. `arusha`, `kilimanjaro`) |\n'
        '| `difficulty` | string | Filter by difficulty level (e.g. `easy`, `moderate`, `challenging`, `extreme`) |\n'
        '| `ordering` | string | Sort by any field. Prefix with `-` for descending (e.g. `-created_at`) |\n\n'
        '**POST** — Create a new attraction. Requires authentication.\n\n'
        '**curl GET example:**\n'
        '```bash\n'
        'curl "https://xenohuru-o7ix53tg.b4a.run/api/v1/attractions/?search=kilimanjaro"\n'
        '```\n\n'
        '**curl POST example:**\n'
        '```bash\n'
        'curl -X POST https://xenohuru-o7ix53tg.b4a.run/api/v1/attractions/ \\\n'
        '  -H "Authorization: Bearer <access_token>" \\\n'
        '  -H "Content-Type: application/json" \\\n'
        '  -d \'{"name":"Ngorongoro Crater","slug":"ngorongoro-crater","region":1,"category":"wildlife",'
        '"description":"...","short_description":"...","latitude":"-3.2","longitude":"35.5",'
        '"difficulty_level":"moderate","access_info":"By road from Arusha",'
        '"best_time_to_visit":"June-October","seasonal_availability":"Year-round",'
        '"estimated_duration":"1-2 days"}\'\n'
        '```'
    ),
    parameters=[
        OpenApiParameter('search', description='Filter by name, description, short description or region', required=False, type=str),
        OpenApiParameter('category', description='Filter by category slug (e.g. mountain, national_park, wildlife, beach, cultural)', required=False, type=str),
        OpenApiParameter('region', description='Filter by region slug (e.g. arusha, kilimanjaro)', required=False, type=str),
        OpenApiParameter('difficulty', description='Filter by difficulty level (easy, moderate, challenging, extreme)', required=False, type=str),
        OpenApiParameter('ordering', description='Sort results by field. Prefix with `-` for descending (e.g. `name`, `-created_at`)', required=False, type=str),
    ],
    request=AttractionCreateUpdateSerializer,
    responses={
        200: OpenApiResponse(response=AttractionListSerializer(many=True), description='List of active attractions.'),
        201: OpenApiResponse(response=AttractionCreateUpdateSerializer, description='Attraction created successfully.'),
        400: OpenApiResponse(description='Validation error — check required fields.'),
        401: OpenApiResponse(description='Authentication required for POST.'),
    },
    examples=[
        OpenApiExample(
            'Create attraction',
            request_only=True,
            value={
                'name': 'Ngorongoro Crater',
                'slug': 'ngorongoro-crater',
                'region': 1,
                'category': 'wildlife',
                'description': 'The world\'s largest inactive caldera, home to the Big Five.',
                'short_description': 'World\'s largest inactive volcanic caldera.',
                'latitude': '-3.2',
                'longitude': '35.5',
                'difficulty_level': 'moderate',
                'access_info': 'By road from Arusha (approx. 3 hours).',
                'best_time_to_visit': 'June-October',
                'seasonal_availability': 'Year-round',
                'estimated_duration': '1-2 days',
                'entrance_fee': '70.00',
                'requires_guide': True,
                'requires_permit': False,
            },
        )
    ],
)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def attraction_list_create(request):
    if request.method == 'GET':
        search = request.query_params.get('search', '')
        ordering = request.query_params.get('ordering', '')
        page = request.query_params.get('page', '1')
        category = request.query_params.get('category', '')
        region = request.query_params.get('region', '')
        difficulty = request.query_params.get('difficulty', '')
        cache_key = f'attractions_list_{search}_{ordering}_{page}_{category}_{region}_{difficulty}'
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        attractions = BASE_QUERYSET
        if search:
            attractions = attractions.filter(name__icontains=search) | \
                          attractions.filter(description__icontains=search) | \
                          attractions.filter(short_description__icontains=search) | \
                          attractions.filter(region__name__icontains=search)
        if category:
            attractions = attractions.filter(category=category)
        if region:
            attractions = attractions.filter(region__slug=region)
        if difficulty:
            attractions = attractions.filter(difficulty_level=difficulty)
        if ordering:
            attractions = attractions.order_by(ordering)
        serializer = AttractionListSerializer(attractions, many=True)
        cache.set(cache_key, serializer.data, 300)  # 5 min
        return Response(serializer.data)
    serializer = AttractionCreateUpdateSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(created_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=['Attractions'],
    summary='Retrieve, update or delete an attraction',
    description=(
        'Look up an attraction by its `slug` (the URL-friendly name, e.g. `mount-kilimanjaro`).\n\n'
        '- **GET** — Public. Returns full attraction details including region, images, and tips.\n'
        '- **PUT** — Full update. All writable fields required. Authentication required.\n'
        '- **PATCH** — Partial update. Only send the fields you want to change. Authentication required.\n'
        '- **DELETE** — Remove the attraction. Authentication required.\n\n'
        '**curl GET example:**\n'
        '```bash\n'
        'curl https://xenohuru-o7ix53tg.b4a.run/api/v1/attractions/mount-kilimanjaro/\n'
        '```\n\n'
        '**curl PATCH example:**\n'
        '```bash\n'
        'curl -X PATCH https://xenohuru-o7ix53tg.b4a.run/api/v1/attractions/mount-kilimanjaro/ \\\n'
        '  -H "Authorization: Bearer <access_token>" \\\n'
        '  -H "Content-Type: application/json" \\\n'
        '  -d \'{"entrance_fee":"80.00"}\'\n'
        '```'
    ),
    responses={
        200: OpenApiResponse(response=AttractionDetailSerializer, description='Full attraction details.'),
        204: OpenApiResponse(description='Attraction deleted successfully.'),
        401: OpenApiResponse(description='Authentication required for write operations.'),
        404: OpenApiResponse(description='No attraction found with the given slug.'),
    },

    examples=[
        OpenApiExample(
            'Partial update — change entrance fee',
            request_only=True,
            value={'entrance_fee': '80.00'},
        )
    ],
)
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly])
def attraction_detail(request, slug):
    try:
        attraction = BASE_QUERYSET.get(slug=slug)
    except Attraction.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        cache_key = f'attraction_detail_{slug}'
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)
        serializer = AttractionDetailSerializer(attraction)
        cache.set(cache_key, serializer.data, 600)  # 10 min
        return Response(serializer.data)
    elif request.method in ['PUT', 'PATCH']:
        serializer = AttractionCreateUpdateSerializer(attraction, data=request.data, partial=request.method == 'PATCH')
        if serializer.is_valid():
            serializer.save()
            cache.delete(f'attraction_detail_{slug}')
            cache.delete('featured_attractions')
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        attraction.delete()
        cache.delete(f'attraction_detail_{slug}')
        cache.delete('featured_attractions')
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    tags=['Attractions'],
    summary='Featured attractions',
    description=(
        'Returns up to 6 attractions marked as featured (`is_featured=true`).\n\n'
        'Results are cached in memory for **1 hour** — changes in the admin panel may take up to 1 hour to reflect here.\n\n'
        '**curl example:**\n'
        '```bash\n'
        'curl https://xenohuru-o7ix53tg.b4a.run/api/v1/attractions/featured/\n'
        '```'
    ),
    responses={
        200: OpenApiResponse(response=AttractionListSerializer(many=True), description='Up to 6 featured attractions.'),
    },
)
@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def featured_attractions(request):
    cache_key = 'featured_attractions'
    featured = cache.get(cache_key)

    if not featured:
        featured_qs = BASE_QUERYSET.filter(is_featured=True)[:6]
        serializer = AttractionListSerializer(featured_qs, many=True)
        cache.set(cache_key, serializer.data, 3600)
        return Response(serializer.data)

    return Response(featured)


@extend_schema(
    tags=['Attractions'],
    summary='Attractions by category',
    description=(
        'Returns all active attractions filtered by category.\n\n'
        '**Valid category values:** `mountain`, `beach`, `wildlife`, `cultural`, `historical`, '
        '`adventure`, `national_park`, `island`, `waterfall`, `lake`, `other`\n\n'
        '**curl example:**\n'
        '```bash\n'
        'curl "https://xenohuru-o7ix53tg.b4a.run/api/v1/attractions/by_category/?category=national_park"\n'
        '```'
    ),
    parameters=[
        OpenApiParameter(
            'category',
            description='Category slug. One of: `mountain`, `beach`, `wildlife`, `cultural`, `historical`, `adventure`, `national_park`, `island`, `waterfall`, `lake`, `other`',
            required=True,
            type=str,
            enum=['mountain', 'beach', 'wildlife', 'cultural', 'historical', 'adventure', 'national_park', 'island', 'waterfall', 'lake', 'other'],
        ),
    ],
    responses={
        200: OpenApiResponse(response=AttractionListSerializer(many=True), description='Attractions in the given category.'),
        400: OpenApiResponse(description='`category` query parameter is required.'),
    },
)
@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def attractions_by_category(request):
    category = request.query_params.get('category')
    if not category:
        return Response({'error': 'Category parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

    cache_key = f'attractions_category_{category}'
    cached = cache.get(cache_key)
    if cached:
        return Response(cached)

    attractions = BASE_QUERYSET.filter(category=category)
    serializer = AttractionListSerializer(attractions, many=True)
    cache.set(cache_key, serializer.data, 900)  # 15 min
    return Response(serializer.data)


@extend_schema(
    tags=['Attractions'],
    summary='Attractions by region',
    description=(
        'Returns all active attractions within a region, identified by its `slug`.\n\n'
        'Use `GET /api/v1/regions/` to list all available region slugs.\n\n'
        '**curl example:**\n'
        '```bash\n'
        'curl "https://xenohuru-o7ix53tg.b4a.run/api/v1/attractions/by_region/?region=arusha"\n'
        '```'
    ),
    parameters=[
        OpenApiParameter(
            'region',
            description='Region slug (e.g. `arusha`, `zanzibar`, `kilimanjaro`). See `GET /api/v1/regions/` for all slugs.',
            required=True,
            type=str,
        ),
    ],
    responses={
        200: OpenApiResponse(response=AttractionListSerializer(many=True), description='Attractions in the given region.'),
        400: OpenApiResponse(description='`region` query parameter is required.'),
    },
)
@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def attractions_by_region(request):
    region_slug = request.query_params.get('region')
    if not region_slug:
        return Response({'error': 'Region parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

    cache_key = f'attractions_region_{region_slug}'
    cached = cache.get(cache_key)
    if cached:
        return Response(cached)

    attractions = BASE_QUERYSET.filter(region__slug=region_slug)
    serializer = AttractionListSerializer(attractions, many=True)
    cache.set(cache_key, serializer.data, 900)  # 15 min
    return Response(serializer.data)


@extend_schema(
    tags=['Attractions'],
    summary='Endemic species for an attraction',
    description=(
        'Returns all endemic species recorded at the given attraction.\n\n'
        '**curl example:**\n'
        '```bash\n'
        'curl https://xenohuru-o7ix53tg.b4a.run/api/v1/attractions/serengeti/endemic-species/\n'
        '```'
    ),
    responses={
        200: OpenApiResponse(response=EndemicSpeciesSerializer(many=True), description='Endemic species list.'),
        404: OpenApiResponse(description='Attraction not found.'),
    },
)
@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def endemic_species_list(request, slug):
    try:
        attraction = Attraction.objects.get(slug=slug, is_active=True)
    except Attraction.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    species = attraction.endemic_species.all()
    serializer = EndemicSpeciesSerializer(species, many=True)
    return Response(serializer.data)


@extend_schema(
    tags=['Attraction Boundaries'],
    summary='Full boundary data for an attraction',
    responses={200: OpenApiResponse(response=AttractionBoundarySerializer)}
)
@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def attraction_boundary(request, slug):
    attraction = get_object_or_404(Attraction, slug=slug, is_active=True)
    boundary = get_object_or_404(AttractionBoundary, attraction=attraction)
    serializer = AttractionBoundarySerializer(boundary)
    return Response(serializer.data)


@extend_schema(
    tags=['Attraction Boundaries'],
    summary='Raw GeoJSON for map',
)
@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def attraction_boundary_geojson(request, slug):
    attraction = get_object_or_404(Attraction, slug=slug, is_active=True)
    boundary = get_object_or_404(AttractionBoundary, attraction=attraction)
    return Response(boundary.geojson if boundary.geojson else {})


@extend_schema(
    tags=['Attraction Boundaries'],
    summary='Find attractions containing a GPS point',
    parameters=[
        OpenApiParameter('lat', required=True, type=float),
        OpenApiParameter('lng', required=True, type=float),
    ],
    responses={200: OpenApiResponse(response=AttractionListSerializer(many=True))}
)
@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def attractions_within(request):
    lat = request.query_params.get('lat')
    lng = request.query_params.get('lng')
    if not lat or not lng:
        return Response({'error': 'lat and lng required'}, status=status.HTTP_400_BAD_REQUEST)
        
    try:
        lat = float(lat)
        lng = float(lng)
    except ValueError:
        return Response({'error': 'Invalid lat or lng'}, status=status.HTTP_400_BAD_REQUEST)

    boundaries = AttractionBoundary.objects.filter(
        bbox_south__lte=lat, bbox_north__gte=lat,
        bbox_west__lte=lng, bbox_east__gte=lng
    ).select_related('attraction')
    
    attractions = [b.attraction for b in boundaries if b.attraction.is_active]
    serializer = AttractionListSerializer(attractions, many=True)
    return Response(serializer.data)


@extend_schema(
    tags=['Attraction Boundaries'],
    summary='Attractions within radius',
    parameters=[
        OpenApiParameter('lat', required=True, type=float),
        OpenApiParameter('lng', required=True, type=float),
        OpenApiParameter('radius', required=True, type=float, description='Radius in km'),
    ],
    responses={200: OpenApiResponse(response=AttractionListSerializer(many=True))}
)
@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def attractions_nearby(request):
    lat = request.query_params.get('lat')
    lng = request.query_params.get('lng')
    radius = request.query_params.get('radius')
    
    if not all([lat, lng, radius]):
        return Response({'error': 'lat, lng, and radius required'}, status=status.HTTP_400_BAD_REQUEST)
        
    try:
        lat = float(lat)
        lng = float(lng)
        radius = float(radius)
    except ValueError:
        return Response({'error': 'Invalid lat, lng, or radius'}, status=status.HTTP_400_BAD_REQUEST)
    
    lat_deg_dist = radius / 111.0
    lon_deg_dist = radius / (111.0 * math.cos(math.radians(lat)))
    
    attractions = Attraction.objects.filter(
        is_active=True,
        latitude__gte=lat - lat_deg_dist,
        latitude__lte=lat + lat_deg_dist,
        longitude__gte=lng - lon_deg_dist,
        longitude__lte=lng + lon_deg_dist
    )
    
    serializer = AttractionListSerializer(attractions, many=True)
    return Response(serializer.data)


@extend_schema(
    tags=['Citations'],
    summary='List all citations',
    responses={200: OpenApiResponse(response=CitationSerializer(many=True))}
)
@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def citation_list(request):
    citations = Citation.objects.all()
    serializer = CitationSerializer(citations, many=True)
    return Response(serializer.data)


@extend_schema(
    tags=['Citations'],
    summary='Citations for attraction',
    responses={200: OpenApiResponse(response=CitationSerializer(many=True))}
)
@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def attraction_citations(request, slug):
    attraction = get_object_or_404(Attraction, slug=slug, is_active=True)
    citations = attraction.citations.all()
    serializer = CitationSerializer(citations, many=True)
    return Response(serializer.data)


@extend_schema(
    tags=['Citations'],
    summary='Citations for endemic species',
    responses={200: OpenApiResponse(response=CitationSerializer(many=True))}
)
@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def endemic_species_citations(request, pk):
    species = get_object_or_404(EndemicSpecies, pk=pk)
    citations = species.citations.all()
    serializer = CitationSerializer(citations, many=True)
    return Response(serializer.data)


@extend_schema(tags=['Attractions - Transport'], summary='List transport facilities', description='Get all transport facilities (airports, bus terminals, train stations, major cities) near an attraction.')
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def attraction_transport(request, slug):
    attraction = get_object_or_404(Attraction, slug=slug, is_active=True)
    if request.method == 'GET':
        transports = attraction.transport_facilities.all()
        serializer = NearestTransportSerializer(transports, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = NearestTransportSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(attraction=attraction)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['Attractions - Transport'], summary='Transport facility detail')
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly])
def transport_detail(request, pk):
    transport = get_object_or_404(NearestTransport, pk=pk)
    if request.method == 'GET':
        serializer = NearestTransportSerializer(transport)
        return Response(serializer.data)
    elif request.method in ['PUT', 'PATCH']:
        serializer = NearestTransportSerializer(transport, data=request.data, partial=request.method == 'PATCH')
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        transport.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=['Attractions - Transport'], summary='Filter by transport type',
    parameters=[OpenApiParameter('type', str, description='Filter: airport, train_station, bus_terminal, major_city, port, ferry')])
@api_view(['GET'])
def transport_by_type(request, slug):
    attraction = get_object_or_404(Attraction, slug=slug, is_active=True)
    transport_type = request.query_params.get('type')
    transports = attraction.transport_facilities.all()
    if transport_type:
        transports = transports.filter(transport_type=transport_type)
    serializer = NearestTransportSerializer(transports, many=True)
    return Response(serializer.data)
