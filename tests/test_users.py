import json

from django.test import TestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import (
    APIRequestFactory,
    force_authenticate
)

from backend.models import (
    ConfirmEmailToken,
    User
)
from backend.views import (
    ConfirmAccount,
    LoginAccountViewSet,
    UserViewSet
)


class UserViewSetTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username='test_user',
            email='test@example.com',
            password='test_password'
        )

    def test_create_user(self):
        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'username': 'new_user',
            'email': 'new_user@example.com',
            'password': 'new_password',
            'company': 'TestCompany',
            'position': 'TestPosition',
            'type': 'buyer',
            'phone': '+79101234567'
        }
        request = self.factory.post('/api/user/register', data)
        force_authenticate(request, user=self.user)
        view = UserViewSet.as_view({'post': 'create'})

        response = view(request)
        self.assertEqual(response.status_code, 201)

        created_user = User.objects.get(email='new_user@example.com')
        self.assertIsNotNone(created_user)
        self.assertEqual(created_user.company, 'TestCompany')
        self.assertEqual(created_user.position, 'TestPosition')

    def test_update_user(self):
        user = User.objects.create(
            username='existing_user',
            email='existing_user@example.com',
            password='existing_password'
        )
        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'username': 'new_user',
            'email': 'test2@example.com',
            'company': 'UpdatedCompany',
            'position': 'UpdatedPosition',
            'password': 'strong_password',
        }

        request = self.factory.put(
            f'/api/user/details/{user.id}/',
            data
        )
        force_authenticate(request, user=self.user)
        view = UserViewSet.as_view({'put': 'update'})
        response = view(request, **{'id': user.id})
        self.assertEqual(response.status_code, 200)

        updated_user = User.objects.get(id=user.id)
        self.assertEqual(updated_user.company, 'UpdatedCompany')
        self.assertEqual(updated_user.position, 'UpdatedPosition')


class ConfirmAccountTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username='test_user',
            email='test@example.com',
            password='test_password',
            is_active=False
        )
        self.token = ConfirmEmailToken.objects.create(
            user=self.user,
            key='test_token'
        )

    def test_confirm_account_success(self):
        data = {
            'email': 'test@example.com',
            'token': 'test_token'
        }
        request = self.factory.post(
            '/api/confirm-account/',
            data
        )
        view = ConfirmAccount.as_view()

        response = view(request)
        self.assertEqual(response.status_code, 200)

        response_data = json.loads(
            response.content.decode('utf-8')
        )
        self.assertEqual(
            response_data,
            {
                'Status': True,
                'Messages': 'Ваш аккаунт подтвержден'
            }
        )
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
        self.assertFalse(
            ConfirmEmailToken.objects.filter(user=self.user).exists()
        )

    def test_confirm_account_invalid_token(self):
        data = {
            'email': 'test@example.com',
            'token': 'invalid_token'
        }
        request = self.factory.post(
            '/api/confirm-account/',
            data
        )
        view = ConfirmAccount.as_view()
        response = view(request)

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(
            response.content.decode('utf-8')
        )

        self.assertEqual(
            response_data,
            {
                'Status': False,
                'Errors': 'Неправильный токен подтверждения'
            }
        )
        self.assertFalse(self.user.is_active)


class LoginAccountViewSetTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='test_password',
            is_active=True
        )

    def test_login_user_success(self):
        data = {
            'email': 'test@example.com',
            'password': 'test_password'
        }
        request = self.factory.post(
            '/api/login/',
            data
        )
        view = LoginAccountViewSet.as_view({'post': 'create'})
        response = view(request)

        self.assertEqual(response.status_code, 201)
        token = Token.objects.get(user=self.user)
        self.assertEqual(response.data['Token'], token.key)

    def test_login_user_invalid_credentials(self):
        data = {
            'email': 'invalid@example.com',
            'password': 'invalid_password'
        }
        request = self.factory.post(
            '/api/login/',
            data
        )
        view = LoginAccountViewSet.as_view({'post': 'create'})
        response = view(request)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )