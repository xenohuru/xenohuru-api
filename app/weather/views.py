from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse
from app.attractions.models import Attraction
from .models import WeatherCache, SeasonalWeatherPattern
from .serializers import WeatherCacheSerializer, SeasonalWeatherPatternSerializer, CurrentWeatherSerializer
from .services import WeatherService

_CURRENT_WEATHER_EXAMPLE = {
    'temperature': 28.4,
    'apparent_temperature': 30.1,
    'humidity': 65,
    'precipitation': 0.0,
    'rain': 0.0,
    'weather_code': 1,
    'weather_description': 'Mainly clear',
    'cloud_cover': 15,
    'wind_speed': 12.3,
    'timestamp': '2026-02-26T10:00',
}

_FORECAST_EXAMPLE = {
    'dates': ['2026-02-26', '2026-02-27', '2026-02-28'],
    'temperature_max': [29.5, 30.1, 28.8],
    'temperature_min': [18.2, 19.0, 17.5],
    'precipitation': [0.0, 2.3, 5.1],
    'rain': [0.0, 2.3, 5.1],
    'weather_codes': [1, 61, 63],
}


@extend_schema(
    tags=['Weather'],
    summary='List all cached weather records',
    description=(
        'Returns all weather records stored in the database. Each record is tied to one attraction '
        'and was last populated by the `update_attraction_weather_cache` service method.\n\n'
        'For live weather data use `GET /api/v1/weather/current/` instead.\n\n'
        '**curl example:**\n'
        '```bash\n'
        'curl https://xenohuru-o7ix53tg.b4a.run/api/v1/weather/\n'
        '```'
    ),
    responses={
        200: OpenApiResponse(
            response=WeatherCacheSerializer(many=True),
            description='List of cached weather records.',
            examples=[
                OpenApiExample(
                    'Cache list',
                    value=[{'attraction_name': 'Mount Kilimanjaro', **_CURRENT_WEATHER_EXAMPLE, 'last_updated': '2026-02-26T09:00:00Z'}],
                )
            ],
        )
    },
)
@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def weather_list(request):
    weather_caches = WeatherCache.objects.all()
    serializer = WeatherCacheSerializer(weather_caches, many=True)
    return Response(serializer.data)


@extend_schema(
    tags=['Weather'],
    summary='Get cached weather by ID',
    description=(
        'Retrieve a single cached weather record by its numeric `id`.\n\n'
        'To find the IDs, call `GET /api/v1/weather/` first.\n\n'
        '**curl example:**\n'
        '```bash\n'
        'curl https://xenohuru-o7ix53tg.b4a.run/api/v1/weather/1/\n'
        '```'
    ),
    responses={
        200: OpenApiResponse(
            response=WeatherCacheSerializer,
            description='Cached weather record for one attraction.',
            examples=[
                OpenApiExample(
                    'Cache detail',
                    value={'attraction_name': 'Mount Kilimanjaro', **_CURRENT_WEATHER_EXAMPLE, 'last_updated': '2026-02-26T09:00:00Z'},
                )
            ],
        ),
        404: OpenApiResponse(
            description='No cached weather record found with the given ID.',
            examples=[OpenApiExample('Not found', value={'error': 'Not found'})],
        ),
    },
)
@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def weather_detail(request, pk):
    try:
        weather_cache = WeatherCache.objects.get(pk=pk)
    except WeatherCache.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = WeatherCacheSerializer(weather_cache)
    return Response(serializer.data)


@extend_schema(
    tags=['Weather'],
    summary='Current weather for a location',
    description=(
        'Fetch **live** current weather from Open-Meteo. Results are cached in memory for **30 minutes**.\n\n'
        'Provide the location using **one** of these two options:\n\n'
        '| Option | Parameters | Example |\n'
        '|--------|------------|---------|\n'
        '| GPS coordinates | `lat` + `lon` | `?lat=-3.0674&lon=37.3556` |\n'
        '| Attraction slug | `attraction` | `?attraction=mount-kilimanjaro` |\n\n'
        '**Weather code** meanings: `0`=Clear sky, `1`=Mainly clear, `2`=Partly cloudy, `3`=Overcast, '
        '`45/48`=Fog, `51-55`=Drizzle, `61-65`=Rain, `80-82`=Rain showers, `95`=Thunderstorm.\n\n'
        '**curl example (by coordinates):**\n'
        '```bash\n'
        'curl "https://xenohuru-o7ix53tg.b4a.run/api/v1/weather/current/?lat=-3.0674&lon=37.3556"\n'
        '```\n\n'
        '**curl example (by attraction slug):**\n'
        '```bash\n'
        'curl "https://xenohuru-o7ix53tg.b4a.run/api/v1/weather/current/?attraction=mount-kilimanjaro"\n'
        '```'
    ),
    parameters=[
        OpenApiParameter('lat', description='Latitude (decimal degrees, e.g. `-3.0674`). Required if `attraction` is not provided.', required=False, type=float),
        OpenApiParameter('lon', description='Longitude (decimal degrees, e.g. `37.3556`). Required if `attraction` is not provided.', required=False, type=float),
        OpenApiParameter('attraction', description='Attraction slug (e.g. `mount-kilimanjaro`). Auto-resolves coordinates. See `GET /api/v1/attractions/` for slugs.', required=False, type=str),
    ],
    responses={
        200: OpenApiResponse(
            response=CurrentWeatherSerializer,
            description='Current weather data. All temperature values are in °C, wind speed in km/h, precipitation in mm.',
            examples=[OpenApiExample('Current weather', value=_CURRENT_WEATHER_EXAMPLE)],
        ),
        400: OpenApiResponse(
            description='Neither `lat`+`lon` nor `attraction` was provided.',
            examples=[OpenApiExample('Missing params', value={'error': 'Latitude and longitude or attraction slug required'})],
        ),
        404: OpenApiResponse(
            description='No attraction found with the given slug.',
            examples=[OpenApiExample('Not found', value={'error': 'Attraction not found'})],
        ),
        503: OpenApiResponse(
            description='Open-Meteo API is unreachable or returned an error.',
            examples=[OpenApiExample('API error', value={'error': 'Weather API error: Connection timeout'})],
        ),
    },
)
@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def current_weather(request):
    lat = request.query_params.get('lat')
    lon = request.query_params.get('lon')
    attraction_slug = request.query_params.get('attraction')

    if attraction_slug:
        try:
            attraction = Attraction.objects.get(slug=attraction_slug)
            lat = attraction.latitude
            lon = attraction.longitude
        except Attraction.DoesNotExist:
            return Response({'error': 'Attraction not found'}, status=status.HTTP_404_NOT_FOUND)

    if not lat or not lon:
        return Response(
            {'error': 'Latitude and longitude or attraction slug required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    weather_data = WeatherService.fetch_current_weather(lat, lon)

    if 'error' in weather_data:
        return Response(weather_data, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    serializer = CurrentWeatherSerializer(data=weather_data)
    serializer.is_valid()
    return Response(serializer.data)


@extend_schema(
    tags=['Weather'],
    summary='Multi-day weather forecast for a location',
    description=(
        'Fetch a **live** multi-day weather forecast from Open-Meteo. Results are cached in memory for **30 minutes**.\n\n'
        'Provide the location using **one** of these two options:\n\n'
        '| Option | Parameters | Example |\n'
        '|--------|------------|---------|\n'
        '| GPS coordinates | `lat` + `lon` | `?lat=-3.0674&lon=37.3556` |\n'
        '| Attraction slug | `attraction` | `?attraction=mount-kilimanjaro` |\n\n'
        'Use the optional `days` parameter to control the forecast window (default: 7, max: 16).\n\n'
        '**curl example (7-day forecast by attraction):**\n'
        '```bash\n'
        'curl "https://xenohuru-o7ix53tg.b4a.run/api/v1/weather/forecast/?attraction=mount-kilimanjaro&days=7"\n'
        '```\n\n'
        '**curl example (3-day forecast by coordinates):**\n'
        '```bash\n'
        'curl "https://xenohuru-o7ix53tg.b4a.run/api/v1/weather/forecast/?lat=-3.0674&lon=37.3556&days=3"\n'
        '```'
    ),
    parameters=[
        OpenApiParameter('lat', description='Latitude (decimal degrees). Required if `attraction` is not provided.', required=False, type=float),
        OpenApiParameter('lon', description='Longitude (decimal degrees). Required if `attraction` is not provided.', required=False, type=float),
        OpenApiParameter('attraction', description='Attraction slug. Auto-resolves coordinates. See `GET /api/v1/attractions/` for slugs.', required=False, type=str),
        OpenApiParameter('days', description='Number of forecast days (default: `7`, max: `16`).', required=False, type=int),
    ],
    responses={
        200: OpenApiResponse(
            description=(
                'Forecast data. Arrays are aligned by index — `dates[0]` corresponds to `temperature_max[0]`, etc.\n\n'
                'All temperatures in °C, precipitation/rain in mm.'
            ),
            examples=[OpenApiExample('7-day forecast', value=_FORECAST_EXAMPLE)],
        ),
        400: OpenApiResponse(
            description='Neither `lat`+`lon` nor `attraction` was provided.',
            examples=[OpenApiExample('Missing params', value={'error': 'Latitude and longitude or attraction slug required'})],
        ),
        404: OpenApiResponse(
            description='No attraction found with the given slug.',
            examples=[OpenApiExample('Not found', value={'error': 'Attraction not found'})],
        ),
        503: OpenApiResponse(
            description='Open-Meteo API is unreachable or returned an error.',
            examples=[OpenApiExample('API error', value={'error': 'Weather API error: Connection timeout'})],
        ),
    },
)
@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def forecast_weather(request):
    lat = request.query_params.get('lat')
    lon = request.query_params.get('lon')
    days = request.query_params.get('days', 7)
    attraction_slug = request.query_params.get('attraction')

    if attraction_slug:
        try:
            attraction = Attraction.objects.get(slug=attraction_slug)
            lat = attraction.latitude
            lon = attraction.longitude
        except Attraction.DoesNotExist:
            return Response({'error': 'Attraction not found'}, status=status.HTTP_404_NOT_FOUND)

    if not lat or not lon:
        return Response(
            {'error': 'Latitude and longitude or attraction slug required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    forecast_data = WeatherService.fetch_forecast(lat, lon, int(days))

    if 'error' in forecast_data:
        return Response(forecast_data, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    return Response(forecast_data)


@extend_schema(
    tags=['Weather'],
    summary='Historical seasonal weather patterns for an attraction',
    description=(
        'These are **not** live data — they are historical patterns entered by contributors.\n\n'
        'Tanzania has three seasons:\n'
        '- **Dry season** (`dry`) — June–October: best time to visit most parks\n'
        '- **Short rains** (`short_rain`) — November–December\n'
        '- **Long rains** (`long_rain`) — March–May\n\n'
        '**curl example:**\n'
        '```bash\n'
        'curl "https://xenohuru-o7ix53tg.b4a.run/api/v1/weather/seasonal/?attraction=mount-kilimanjaro"\n'
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
        200: OpenApiResponse(
            response=SeasonalWeatherPatternSerializer(many=True),
            description='Seasonal weather patterns for the attraction. Returns an empty list if none have been added yet.',
            examples=[
                OpenApiExample(
                    'Seasonal patterns',
                    value=[
                        {
                            'id': 1,
                            'season_type': 'dry',
                            'season_display': 'Dry Season',
                            'start_month': 6,
                            'end_month': 10,
                            'avg_temperature': '22.50',
                            'avg_rainfall': '5.00',
                            'description': 'Clear skies and cool temperatures. Ideal for climbing.',
                        },
                        {
                            'id': 2,
                            'season_type': 'long_rain',
                            'season_display': 'Long Rain Season',
                            'start_month': 3,
                            'end_month': 5,
                            'avg_temperature': '18.00',
                            'avg_rainfall': '180.00',
                            'description': 'Heavy rains make trails slippery. Not recommended.',
                        },
                    ],
                )
            ],
        ),
        400: OpenApiResponse(
            description='`attraction` query parameter is required.',
            examples=[OpenApiExample('Missing param', value={'error': 'Attraction slug required'})],
        ),
        404: OpenApiResponse(
            description='No attraction found with the given slug.',
            examples=[OpenApiExample('Not found', value={'error': 'Attraction not found'})],
        ),
    },
)
@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def seasonal_weather(request):
    attraction_slug = request.query_params.get('attraction')

    if not attraction_slug:
        return Response(
            {'error': 'Attraction slug required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        attraction = Attraction.objects.get(slug=attraction_slug)
        patterns = SeasonalWeatherPattern.objects.filter(attraction=attraction)
        serializer = SeasonalWeatherPatternSerializer(patterns, many=True)
        return Response(serializer.data)
    except Attraction.DoesNotExist:
        return Response({'error': 'Attraction not found'}, status=status.HTTP_404_NOT_FOUND)


@extend_schema(
    tags=['Weather'],
    summary='Historical weather data',
    description='Get historical weather data for a location. Supports last 5, 7, 30, or 90 days. Uses Open-Meteo Archive API (free). Returns daily temperature, precipitation, rainfall, humidity, wind speed.',
    parameters=[
        OpenApiParameter('lat', float, description='Latitude'),
        OpenApiParameter('lon', float, description='Longitude'),
        OpenApiParameter('attraction', str, description='Attraction slug (alternative to lat/lon)'),
        OpenApiParameter('days', int, description='Number of past days (default: 7, max: 90)'),
    ]
)
@api_view(['GET'])
@permission_classes([AllowAny])
def historical_weather(request):
    lat = request.query_params.get('lat')
    lon = request.query_params.get('lon')
    attraction_slug = request.query_params.get('attraction')
    days = request.query_params.get('days', 7)

    try:
        days = int(days)
    except (ValueError, TypeError):
        days = 7

    if attraction_slug:
        try:
            from app.attractions.models import Attraction
            attraction = Attraction.objects.get(slug=attraction_slug, is_active=True)
            lat, lon = attraction.latitude, attraction.longitude
        except Attraction.DoesNotExist:
            return Response({'error': 'Attraction not found'}, status=status.HTTP_404_NOT_FOUND)

    if not lat or not lon:
        return Response(
            {'error': 'Provide lat & lon coordinates or attraction slug'},
            status=status.HTTP_400_BAD_REQUEST
        )

    data = WeatherService.fetch_historical_weather(lat, lon, days)
    if 'error' in data:
        return Response(data, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    return Response(data)
