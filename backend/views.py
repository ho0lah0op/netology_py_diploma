from django.http import JsonResponse
from djoser.views import UserViewSet as BaseUserViewSet
from rest_framework import status, viewsets
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    AllowAny, IsAuthenticated,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import (
    ViewSet,
    ModelViewSet,
    ReadOnlyModelViewSet
)

from backend.models import (
    Category,
    ConfirmEmailToken,
    Contact,
    Shop,
    User,
)
from backend.permissions import IsAuthorOrReadOnly
from backend.serializers import (
    CategorySerializer,
    ContactSerializer,
    LoginAccountSerializer,
    PartnerUpdateSerializer,
    ShopSerializer,
    UserSerializer,
)
from backend.utils import validate_all_fields


class UserViewSet(BaseUserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    lookup_field = 'id'

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        obj = queryset.get(pk=self.request.user.id)
        self.check_object_permissions(self.request, obj)
        return obj

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class ContactViewSet(ViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get', 'post', 'patch', 'put', 'delete']

    def list(self, request):
        contacts = Contact.objects.filter(user=request.user)
        serializer = ContactSerializer(contacts, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(
                data={
                    'Status': True,
                    'Message': 'Контакт создан'
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            data={
                'Status': False,
                'Errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def destroy(self, request, pk=None):
        try:
            contact = Contact.objects.get(
                pk=pk,
                user=request.user
            )
            contact.delete()
            return Response({'Status': True})
        except Contact.DoesNotExist:
            return Response(
                data={
                    'Status': False,
                    'Error': 'Контакт не найден'
                },
                status=status.HTTP_404_NOT_FOUND
            )

    def update(self, request, pk=None):
        try:
            contact = Contact.objects.get(
                pk=pk,
                user=request.user
            )
            serializer = ContactSerializer(
                contact,
                data=request.data,
                partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(
                    data={
                        'Status': True,
                        'Message': 'Данные контакта обновлены'
                    },
                    status=status.HTTP_200_OK
                )
            return Response(
                data={
                    'Status': False,
                    'Errors': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Contact.DoesNotExist:
            return Response(
                data={
                    'Status': False,
                    'Error': 'Контакт не найден'
                },
                status=status.HTTP_404_NOT_FOUND
            )


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (AllowAny,)


class ShopViewSet(ReadOnlyModelViewSet):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
    permission_classes = (AllowAny,)


class ConfirmAccount(APIView):
    """Класс для подтверждения электронной почты."""

    def post(self, request, *args, **kwargs):
        validate_all_fields(('email', 'token'), request.data)
        token = ConfirmEmailToken.objects.filter(
            user__email=request.data.get('email'),
            key=request.data.get('token')
        ).first()

        if token:
            token.user.is_active = True
            token.user.save()
            token.delete()
            return JsonResponse({'Status': True})

        return JsonResponse(
            {
                'Status': False,
                'Errors': 'Неправильный токен подтверждения'
            }
        )


class LoginAccountViewSet(viewsets.ViewSet):
    """Класс для авторизации пользователей."""

    def create(self, request):
        serializer = LoginAccountSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            token = serializer.save()
            return Response(
                data={'Status': True, 'Token': token.key},
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class PartnerUpdateViewSet(viewsets.ViewSet):
    """Класс для обновления цены от поставщика."""

    def create(self, request):
        serializer = PartnerUpdateSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                data={'Status': True},
                status=status.HTTP_201_CREATED
            )
        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )