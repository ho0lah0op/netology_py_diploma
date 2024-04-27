from django.test import TestCase
from rest_framework.test import APIRequestFactory

from backend.models import Category
from backend.serializers import CategorySerializer
from backend.views import CategoryViewSet


class CategoryViewSetTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.category1 = Category.objects.create(name='Category 1')
        self.category2 = Category.objects.create(name='Category 2')

    def test_list_categories(self):
        request = self.factory.get('/api/categories/')
        view = CategoryViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        serializer = CategorySerializer(
            [self.category1,
             self.category2],
            many=True
        )
        self.assertEqual(
            list(response.data['results']),
            serializer.data
        )

    def test_retrieve_category(self):
        request = self.factory.get(
            f'/api/categories/{self.category1.id}/'
        )
        view = CategoryViewSet.as_view({'get': 'retrieve'})
        response = view(request, pk=self.category1.id)
        self.assertEqual(response.status_code, 200)
        serializer = CategorySerializer(self.category1)
        self.assertEqual(response.data, serializer.data)