from django.test import TestCase
from rest_framework.test import APIRequestFactory

from backend.models import Shop
from backend.serializers import ShopSerializer
from backend.views import ShopViewSet


class ShopViewSetTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.shop1 = Shop.objects.create(name='Shop 1')
        self.shop2 = Shop.objects.create(name='Shop 2')

    def test_list_shops(self):
        request = self.factory.get('/api/shops/')
        view = ShopViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        serializer = ShopSerializer(
            [self.shop1,
             self.shop2],
            many=True
        )
        self.assertEqual(
            list(response.data['results']),
            serializer.data
        )

    def test_retrieve_shop(self):
        request = self.factory.get(
            f'/api/shops/{self.shop1.id}/'
        )
        view = ShopViewSet.as_view({'get': 'retrieve'})
        response = view(request, pk=self.shop1.id)
        self.assertEqual(response.status_code, 200)
        serializer = ShopSerializer(self.shop1)
        self.assertEqual(response.data, serializer.data)