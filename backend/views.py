import json

from django.db.models import F, Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as BaseUserViewSet
from rest_framework import status
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
    Order,
    OrderItem,
    ProductInfo,
    Shop,
    User
)
from backend.permissions import IsAuthorOrReadOnly
from backend.serializers import (
    CategorySerializer,
    ContactSerializer,
    LoginAccountSerializer,
    OrderSerializer,
    OrderItemSerializer,
    PartnerUpdateSerializer,
    ProductInfoSerializer,
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
        obj = get_object_or_404(
            queryset,
            pk=self.kwargs.get('id')
        )
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
            return Response(
                {
                    'Status': True,
                    'Message': 'Контакт удалён'
                }
            )
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


class LoginAccountViewSet(ViewSet):
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


class PartnerUpdateViewSet(ViewSet):
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


class ProductInfoViewSet(ViewSet):
    """Класс для поиска и вывода списка товаров."""

    def list(self, request):
        query = Q(shop__state=True)
        shop_id = request.query_params.get('shop_id')
        category_id = request.query_params.get('category_id')

        if shop_id:
            query &= Q(shop_id=shop_id)
        if category_id:
            query &= Q(product__category_id=category_id)

        queryset = ProductInfo.objects.filter(
            query
        ).select_related(
            'shop', 'product__category'
        ).prefetch_related(
            'product_parameters__parameter'
        ).distinct()
        serializer = ProductInfoSerializer(queryset, many=True)

        return Response(serializer.data)


class BasketViewSet(ViewSet):
    """Класс для работы с корзиной пользователя."""

    permission_classes = (IsAuthenticated,)
    http_method_names = ['get', 'post', 'patch', 'put', 'delete']

    def _get_basket(self, user_id):
        return Order.objects.filter(
            user_id=user_id, state='basket'
        ).prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter'
        ).annotate(
            total_sum=Sum(
                F('ordered_items__quantity')
                * F('ordered_items__product_info__price')
            )
        ).distinct()

    def _parse_items(self, items):
        try:
            return json.loads(items)
        except ValueError as err:
            return {
                'Status': False,
                'Errors': f'Неверный формат запроса {err}'
            }

    def _create_order_items(self, basket, items):
        created_count = 0
        for order_data in items:
            order_data['order'] = basket.id
            serializer = OrderItemSerializer(data=order_data)
            if serializer.is_valid():
                serializer.save()
                created_count += 1
            else:
                return {
                    'Status': False,
                    'Errors': serializer.errors
                }
        return created_count

    def _update_order_items(self, basket, items):
        updated_count = 0
        for order_data in items:
            order_id = order_data.get('id')
            quantity = order_data.get('quantity')
            try:
                order_item = OrderItem.objects.get(
                    order=basket,
                    id=order_id
                )
                order_item.quantity = quantity
                order_item.save()
                updated_count += 1
            except OrderItem.DoesNotExist:
                return {
                    'Status': False,
                    'Errors': f'Позиция корзины с id {order_id} не найдена'
                }

        return updated_count

    def _handle_items(self, request, action):
        items = request.data.get('items')

        if items:
            items = self._parse_items(items)
            basket, _ = Order.objects.get_or_create(
                user_id=request.user.id,
                state='basket',
                contact_id=get_object_or_404(
                    Contact, id=request.data.get('contact_id')
                )
            )

            if action == 'create':
                result = self._create_order_items(basket, items)
            elif action == 'update':
                result = self._update_order_items(basket, items)
            else:
                result = 0

            if isinstance(result, dict):
                return Response(
                    data=result,
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                data={
                    'Status': True,
                    'Message': result
                },
                status=status.HTTP_200_OK
            )

        return Response(
            data={
                'Status': False,
                'Errors': 'Не указаны все необходимые аргументы'
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def list(self, request):
        basket = self._get_basket(request.user.id)
        serializer = OrderSerializer(basket, many=True)
        return Response(serializer.data)

    def create(self, request):
        return self._handle_items(request, 'create')

    def update(self, request, pk=None):
        return self._handle_items(request, 'update')

    def destroy(self, request, pk=None):
        items = request.data.get('items')
        if items:
            items = items.split(',')
            basket, _ = Order.objects.get_or_create(
                user_id=request.user.id,
                state='basket'
            )
            query = Q()
            removed = False
            for order_id in items:
                if order_id.isdigit():
                    query = query | Q(order_id=basket.id, id=order_id)
                    removed = True

            if removed:
                removed_count, _ = OrderItem.objects.filter(query).delete()
                return Response(
                    data={
                        'Status': True,
                        'Message': f'Удалено объектов: {removed_count}'
                    },
                    status=status.HTTP_204_NO_CONTENT
                )

        return Response(
            data={
                'Status': False,
                'Errors': 'Не указаны все необходимые аргументы'
            },
            status=status.HTTP_400_BAD_REQUEST
        )