from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from app.regions.models import Region
from app.attractions.models import Attraction
from .models import TourOperator

User = get_user_model()


def make_operator(name='Kilimanjaro Guides', slug='kilimanjaro-guides'):
    return TourOperator.objects.create(
        name=name, slug=slug,
        description='Expert mountain guides.',
        short_description='Expert guides.',
        tier='mid', is_active=True,
    )


class OperatorsAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.list_url = '/api/v1/operators/'
        self.user = User.objects.create_user(username='opuser', email='op@example.com', password='Pass1234!')
        self.region = Region.objects.create(
            name='Kilimanjaro', slug='kilimanjaro',
            description='Home of Africa\'s highest peak.',
            latitude='-3.0674', longitude='37.3556',
        )
        self.operator = make_operator()

    def test_list_operators_public(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_operator_detail_public(self):
        response = self.client.get(f'{self.list_url}kilimanjaro-guides/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Kilimanjaro Guides')

    def test_operator_detail_not_found(self):
        response = self.client.get(f'{self.list_url}nonexistent/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_filter_by_tier(self):
        response = self.client.get(f'{self.list_url}?tier=mid')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_by_attraction_missing_param(self):
        response = self.client.get(f'{self.list_url}by_attraction/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_by_attraction(self):
        attraction = Attraction.objects.create(
            name='Kilimanjaro', slug='kilimanjaro-peak', region=self.region,
            category='mountain', description='Highest peak in Africa.',
            short_description='Highest peak.', latitude='-3.0674', longitude='37.3556',
            difficulty_level='difficult', access_info='By foot.',
            best_time_to_visit='Jan-Mar', seasonal_availability='Year-round',
            estimated_duration='7 days', created_by=self.user, is_active=True,
        )
        self.operator.attractions.add(attraction)
        response = self.client.get(f'{self.list_url}by_attraction/?attraction=kilimanjaro-peak')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_operator_requires_auth(self):
        response = self.client.post(self.list_url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_operator_authenticated(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'name': 'Safari Stars', 'slug': 'safari-stars',
            'description': 'Top safari operator.', 'short_description': 'Top safari.', 'tier': 'luxury',
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_delete_operator_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f'{self.list_url}kilimanjaro-guides/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
