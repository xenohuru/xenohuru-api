from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Partner

User = get_user_model()


def make_partner(name='Tanzania Tourism Board', slug='tanzania-tourism-board', tier='gold'):
    return Partner.objects.create(
        name=name, slug=slug,
        description='Official tourism board of Tanzania.',
        tier=tier, is_active=True,
    )


class PartnersAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.list_url = '/api/v1/partners/'
        self.user = User.objects.create_user(username='partneruser', email='partner@example.com', password='Pass1234!')
        self.partner = make_partner()

    def test_list_partners_public(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_partner_detail_public(self):
        response = self.client.get(f'{self.list_url}tanzania-tourism-board/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Tanzania Tourism Board')

    def test_partner_detail_not_found(self):
        response = self.client.get(f'{self.list_url}nonexistent/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_filter_by_tier(self):
        response = self.client.get(f'{self.list_url}?tier=gold')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_create_partner_requires_auth(self):
        response = self.client.post(self.list_url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_partner_authenticated(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'name': 'Acacia Foundation', 'slug': 'acacia-foundation',
            'description': 'Conservation NGO.', 'tier': 'silver',
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_delete_partner_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f'{self.list_url}tanzania-tourism-board/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
