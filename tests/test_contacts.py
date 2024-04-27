from django.test import TestCase
from rest_framework.test import (
    APIRequestFactory,
    force_authenticate
)

from backend.models import Contact, User
from backend.views import (
    ContactViewSet
)


class ContactViewSetTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username='test_user',
            email='test@example.com',
            password='test_password'
        )

    def test_create_contact(self):
        data = {
            'city': 'Test City',
            'street': 'Test Street',
            'house': '123',
            'phone': '+79134567890'
        }
        request = self.factory.post('/api/contacts/', data)
        force_authenticate(request, user=self.user)
        view = ContactViewSet.as_view({'post': 'create'})
        response = view(request)
        self.assertEqual(response.status_code, 201)
        created_contact = Contact.objects.get(user=self.user)
        self.assertIsNotNone(created_contact)
        self.assertEqual(created_contact.city, 'Test City')
        self.assertEqual(created_contact.street, 'Test Street')
        self.assertEqual(created_contact.house, '123')
        self.assertEqual(created_contact.phone, '+79134567890')

    def test_update_contact(self):
        contact = Contact.objects.create(
            user=self.user,
            city='Old City',
            street='Old Street',
            house='456',
            phone='+79001125547'
        )
        data = {
            'city': 'Updated City',
            'street': 'Updated Street',
            'house': '789',
            'phone': '+79155554444'
        }
        request = self.factory.patch(
            f'/api/contacts/{contact.pk}/',
            data
        )
        force_authenticate(request, user=self.user)
        view = ContactViewSet.as_view({'patch': 'update'})
        response = view(request, pk=contact.pk)
        self.assertEqual(response.status_code, 200)
        updated_contact = Contact.objects.get(pk=contact.pk)
        self.assertEqual(updated_contact.city, 'Updated City')
        self.assertEqual(updated_contact.street, 'Updated Street')
        self.assertEqual(updated_contact.house, '789')
        self.assertEqual(updated_contact.phone, '+79155554444')

    def test_delete_contact(self):
        contact = Contact.objects.create(
            user=self.user,
            city='Test City',
            street='Test Street',
            house='123',
            phone='+79134511888'
        )
        request = self.factory.delete('/api/contacts/', pk=contact.pk)
        force_authenticate(request, user=self.user)
        view = ContactViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=contact.pk)
        self.assertEqual(response.status_code, 204)
        with self.assertRaises(Contact.DoesNotExist):
            Contact.objects.get(pk=contact.pk)