from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from .serializers import RegisterSerializer, UserSerializer, CustomTokenObtainPairSerializer

User = get_user_model()


@extend_schema(
    tags=['Auth'],
    summary='Register a new user',
    description=(
        'Create a new user account.\n\n'
        '**Required fields:** `username`, `email`, `password`, `password_confirm`\n\n'
        '**Optional fields:** `phone`, `bio`\n\n'
        '**Password rules:** minimum 8 characters; `password` and `password_confirm` must match.\n\n'
        '**curl example:**\n'
        '```bash\n'
        'curl -X POST https://xenohuru-o7ix53tg.b4a.run/api/v1/auth/register/ \\\n'
        '  -H "Content-Type: application/json" \\\n'
        '  -d \'{"username":"john","email":"john@example.com","password":"Secure123!","password_confirm":"Secure123!"}\'\n'
        '```'
    ),
    request=RegisterSerializer,
    responses={
        201: OpenApiResponse(
            response=UserSerializer,
            description='User created successfully. Returns the new user profile (passwords excluded).',
            examples=[
                OpenApiExample(
                    'Successful registration',
                    value={
                        'id': 5,
                        'username': 'john',
                        'email': 'john@example.com',
                        'phone': '',
                        'bio': '',
                        'is_tour_operator': False,
                        'date_joined': '2026-02-26T08:00:00Z',
                    },
                )
            ],
        ),
        400: OpenApiResponse(
            description='Validation error. Returned when required fields are missing, passwords do not match, or email/username is already taken.',
            examples=[
                OpenApiExample(
                    'Password mismatch',
                    value={'non_field_errors': ['Passwords do not match']},
                ),
                OpenApiExample(
                    'Missing fields',
                    value={
                        'username': ['This field is required.'],
                        'email': ['This field is required.'],
                        'password': ['This field is required.'],
                        'password_confirm': ['This field is required.'],
                    },
                ),
            ],
        ),
    },
    examples=[
        OpenApiExample(
            'Minimal registration',
            request_only=True,
            value={
                'username': 'john',
                'email': 'john@example.com',
                'password': 'Secure123!',
                'password_confirm': 'Secure123!',
            },
        ),
        OpenApiExample(
            'Full registration',
            request_only=True,
            value={
                'username': 'john',
                'email': 'john@example.com',
                'password': 'Secure123!',
                'password_confirm': 'Secure123!',
                'phone': '+255712345678',
                'bio': 'Safari enthusiast based in Arusha.',
            },
        ),
    ],
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=['Auth'],
    summary='Login — obtain JWT tokens',
    description=(
        'Authenticate with username and password. Returns a JWT `access` token (valid 60 min) '
        'and a `refresh` token (valid 24 h).\n\n'
        '**Note:** The login field is `username`, not `email`.\n\n'
        'Use the `access` token in subsequent requests as:\n'
        '```\nAuthorization: Bearer <access_token>\n```\n\n'
        '**curl example:**\n'
        '```bash\n'
        'curl -X POST https://xenohuru-o7ix53tg.b4a.run/api/v1/auth/login/ \\\n'
        '  -H "Content-Type: application/json" \\\n'
        '  -d \'{"username":"john","password":"Secure123!"}\'\n'
        '```'
    ),
    request={
        'application/json': {
            'type': 'object',
            'required': ['username', 'password'],
            'properties': {
                'username': {'type': 'string', 'example': 'john'},
                'password': {'type': 'string', 'example': 'Secure123!'},
            },
        }
    },
    responses={
        200: OpenApiResponse(
            description='Login successful. Returns access and refresh JWT tokens.',
            examples=[
                OpenApiExample(
                    'Token response',
                    value={
                        'access': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
                        'refresh': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
                    },
                )
            ],
        ),
        401: OpenApiResponse(
            description='Invalid credentials.',
            examples=[
                OpenApiExample(
                    'Bad credentials',
                    value={'detail': 'No active account found with the given credentials'},
                )
            ],
        ),
    },
    examples=[
        OpenApiExample(
            'Login request',
            request_only=True,
            value={'username': 'john', 'password': 'Secure123!'},
        )
    ],
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    serializer = CustomTokenObtainPairSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    return Response(serializer.validated_data, status=status.HTTP_200_OK)


@extend_schema(
    tags=['Auth'],
    summary='Get or update own profile',
    description=(
        'Retrieve (GET), fully replace (PUT), or partially update (PATCH) the authenticated user\'s profile.\n\n'
        '**Authentication required:** `Authorization: Bearer <access_token>`\n\n'
        '**curl example (GET):**\n'
        '```bash\n'
        'curl https://xenohuru-o7ix53tg.b4a.run/api/v1/auth/profile/ \\\n'
        '  -H "Authorization: Bearer <access_token>"\n'
        '```\n\n'
        '**curl example (PATCH):**\n'
        '```bash\n'
        'curl -X PATCH https://xenohuru-o7ix53tg.b4a.run/api/v1/auth/profile/ \\\n'
        '  -H "Authorization: Bearer <access_token>" \\\n'
        '  -H "Content-Type: application/json" \\\n'
        '  -d \'{"bio":"Updated bio"}\'\n'
        '```'
    ),
    request=UserSerializer,
    responses={
        200: OpenApiResponse(
            response=UserSerializer,
            description='User profile.',
            examples=[
                OpenApiExample(
                    'Profile response',
                    value={
                        'id': 5,
                        'username': 'john',
                        'email': 'john@example.com',
                        'phone': '+255712345678',
                        'bio': 'Safari enthusiast.',
                        'is_tour_operator': False,
                        'date_joined': '2026-02-26T08:00:00Z',
                    },
                )
            ],
        ),
        401: OpenApiResponse(description='Authentication credentials were not provided or are invalid.'),
    },
    examples=[
        OpenApiExample(
            'Partial update (PATCH)',
            request_only=True,
            value={'bio': 'Updated bio text', 'phone': '+255700000000'},
        )
    ],
)
@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    user = request.user
    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data)
    serializer = UserSerializer(user, data=request.data, partial=request.method == 'PATCH')
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
