from djoser.views import UserViewSet as BaseUserViewSet
from rest_framework import status
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    AllowAny,
    IsAuthenticated
)
from rest_framework.response import Response
from rest_framework.viewsets import (
    ModelViewSet,
    ReadOnlyModelViewSet
)

from backend.models import (
    ConfirmEmailToken,
    Contact,
    User, Category, Shop
)
from backend.serializers import (
    ContactSerializer,
    UserSerializer, CategorySerializer, ShopSerializer
)


class UserViewSet(BaseUserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class ConfirmUserViewSet(BaseUserViewSet):

    def activation(self, request, *args, **kwargs):
        token_obj = ConfirmEmailToken.objects.filter(
            user__email=kwargs.get('email'),
            key=kwargs.get('token')
        ).first()

        if token_obj:
            token_obj.user.is_active = True
            token_obj.user.save()
            token_obj.delete()
            return Response(
                {'status': 'ok'},
                status=status.HTTP_200_OK
            )

        return Response(
            {'status': 'error',
             'message': 'Неправильный токен подтверждения'},
            status=status.HTTP_400_BAD_REQUEST
        )


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