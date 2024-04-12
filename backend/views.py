from django.http import JsonResponse
from djoser.views import UserViewSet as BaseUserViewSet
from rest_framework import status, viewsets
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    AllowAny,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import (
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
from backend.serializers import (
    CategorySerializer,
    ConfirmAccountSerializer,
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


class ContactViewSet(ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


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
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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