import json

from cacheops import cached, cached_as
from django.contrib.auth.tokens import default_token_generator
from django.db import IntegrityError, transaction
from django.db.models import F, Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from distutils.util import strtobool
from djoser.views import UserViewSet as BaseUserViewSet
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import (
    ModelViewSet,
    ReadOnlyModelViewSet,
    ViewSet
)

from backend.constants import CACHE_TIMEOUT
from backend.forms import ImageUploadForm
from backend.models import (
    Category,
    ConfirmEmailToken,
    Contact,
    Order,
    OrderItem,
    Product,
    ProductInfo,
    Shop,
    User,
)
from backend.permissions import (
    IsAuthorOrReadOnly,
    IsShopOnly
)
from backend.serializers import (
    CategorySerializer,
    ContactSerializer,
    LoginAccountSerializer,
    OrderSerializer,
    OrderItemSerializer,
    PartnerUpdateSerializer,
    ProductSerializer,
    ProductInfoSerializer,
    ShopSerializer,
    UserSerializer,
)
from backend.tasks import (
    confirm_order_async,
    create_order_async,
    process_image_async,
    update_order_state_async
)
from backend.utils import validate_all_fields


class UserViewSet(BaseUserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    lookup_field = 'id'
    parser_classes = (MultiPartParser, FormParser)

    @cached(timeout=CACHE_TIMEOUT)
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
    permission_classes = (IsAuthenticated, IsAuthorOrReadOnly)
    http_method_names = ['get', 'post', 'patch', 'put', 'delete']

    @cached_as(Contact, timeout=CACHE_TIMEOUT)
    def list_cached_contacts(self, request):
        contacts = Contact.objects.filter(user=request.user)
        serializer = ContactSerializer(contacts, many=True)
        return serializer.data

    def list(self, request):
        return Response(
            self.list_cached_contacts(request)
        )

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
            Contact.objects.get(
                pk=pk,
                user=request.user
            ).delete()
            return Response(
                data={
                    'Status': True,
                    'Message': 'Контакт удалён'
                },
                status=status.HTTP_204_NO_CONTENT
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
            serializer = ContactSerializer(
                Contact.objects.get(pk=pk, user=request.user),
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
    permission_classes = (IsAuthenticatedOrReadOnly,)


class ShopViewSet(ReadOnlyModelViewSet):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


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
            return JsonResponse(
                {
                    'Status': True,
                    'Messages': 'Ваш аккаунт подтвержден'
                }
            )

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
                data={
                    'Status': True,
                    'Message': 'Данные успешно импортированы!'
                },
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
                ).id
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

            if action == 'create':
                return Response(
                    data={
                        'Status': True,
                        'Message': f'Добавлено {result} позиции'
                    },
                    status=status.HTTP_201_CREATED
                )
            return Response(
                data={
                    'Status': True,
                    'Message': f'Обновлено {result} позиции'
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
        if not items:
            return Response(
                data={
                    'Status': False,
                    'Errors': 'Не указаны все необходимые аргументы'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        items = items.split(',')
        basket = self.get_or_create_basket(request)
        if not basket:
            return Response(
                data={
                    'Status': False,
                    'Errors': 'Не удалось создать корзину'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        query, removed = self.build_query(items, basket)
        if not removed:
            return Response(
                data={
                    'Status': True,
                    'Message': 'Ничего не было удалено'
                },
                status=status.HTTP_200_OK
            )

        removed_count = self.remove_items(query)
        if removed_count > 0:
            basket.save()

            # Если в корзине не остались позиции, она удаляется.
            if not basket.ordered_items.exists():
                basket.delete()
            return Response(
                data={
                    'Status': True,
                    'Message': f'Удалено объектов: {removed_count}'
                },
                status=status.HTTP_204_NO_CONTENT
            )

        return Response(
            data={
                'Status': True,
                'Message': 'Ничего не было удалено'
            },
            status=status.HTTP_200_OK
        )

    def get_or_create_basket(self, request):
        try:
            return Order.objects.get(
                user_id=request.user.id,
                state='basket'
            )
        except Order.DoesNotExist:
            contact_id = request.data.get('contact_id')
            get_object_or_404(Contact, id=contact_id)

            return Order.objects.create(
                user_id=request.user.id,
                state='basket',
                contact_id=contact_id
            )

    def build_query(self, items, basket):
        query = Q()
        removed = False
        for order_id in items:
            if order_id.isdigit():
                query = query | Q(
                    order_id=basket.id,
                    id=order_id
                )
                removed = True
        return query, removed

    def remove_items(self, query):
        with transaction.atomic():
            removed_count, _ = OrderItem.objects.filter(query).delete()
            return removed_count


class OrderViewSet(ViewSet):
    """Класс для получения и размещения заказов пользователями."""

    permission_classes = (IsAuthenticated,)

    def list(self, request):
        order = Order.objects.filter(
            user_id=request.user.id
        ).exclude(
            state='basket'
        ).prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter'
        ).select_related('contact').annotate(
            total_sum=Sum(
                F('ordered_items__quantity')
                * F('ordered_items__product_info__price')
            )
        ).distinct()

        serializer = OrderSerializer(order, many=True)
        return Response(serializer.data)

    def __all_fields_isdigit(self, fields):
        for field in fields:

            if not self.request.data.get(field).isdigit():
                raise ValidationError(
                    detail=f'Укажите корректное значение {field}',
                    code=status.HTTP_400_BAD_REQUEST
                )

    @transaction.atomic
    def create(self, request):
        validate_all_fields(('id', 'contact'), request.data)
        self.__all_fields_isdigit(('id', 'contact'))

        try:
            is_updated = Order.objects.filter(
                user_id=request.user.id,
                id=request.data.get('id')
            ).update(
                contact_id=request.data.get('contact'),
                state='new'
            )
        except IntegrityError as err:
            return JsonResponse(
                data={
                    'Status': False,
                    'Errors': f'Неправильно указаны аргументы: {err}'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if is_updated:
            result, message = create_order_async.delay(
                sender=self.__class__.__name__,
                user_id=request.user.id,
            ).get()

            return self.__result_handler(
                result,
                message,
                status=status.HTTP_201_CREATED
            )

        return JsonResponse(
            data={
                'Status': False,
                'Message': 'Корзина пуста'
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def confirm_order(self, request):
        validate_all_fields(
            ('email', 'token', 'order_id', 'contact_id'),
            request.data
        )
        user = User.objects.filter(
            email=request.data.get('email')
        ).first()
        if not user:
            return JsonResponse(
                data={
                    'Status': False,
                    'Errors': 'Пользователь не найден'
                },
                status=status.HTTP_404_NOT_FOUND
            )

        if not default_token_generator.check_token(
                user, request.data.get('token')
        ):
            return JsonResponse(
                data={
                    'Status': False,
                    'Errors': 'Неправильный токен подтверждения'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            order = Order.objects.get(
                id=request.data.get('order_id'),
                user=user,
                state='new'
            )
            contact = get_object_or_404(
                Contact,
                id=request.data.get('contact_id')
            )
        except Order.DoesNotExist:
            return JsonResponse(
                data={
                    'Status': False,
                    'Errors': 'Заказ уже подтвержден или отменён'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if order.state != 'new':
            return JsonResponse(
                data={
                    'Status': False,
                    'Errors': ('Невозможно подтвердить '
                               'заказ с текущим статусом')
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        order.state = 'confirmed'
        order.save()
        result, message = confirm_order_async.delay(
            sender=self.__class__.__name__,
            user_id=user.id,
            order_id=order.id,
            contact_id=contact.id
        ).get()

        return self.__result_handler(result, message)

    def __result_handler(self, result, msg, status=status.HTTP_200_OK):
        if result:
            return JsonResponse(
                data={'Status': True, 'Message': msg},
                status=status
            )

        return JsonResponse(
            data={'Status': False, 'Errors': msg},
            status=status.HTTP_400_BAD_REQUEST
        )

    def assemble_order(self, request):
        validate_all_fields(('order_id',), request.data)
        result, message = update_order_state_async.delay(
            self.__class__.__name__,
            request.data.get('order_id'),
            request.user.id,
            'confirmed',
            'assembled'
        ).get()

        return self.__result_handler(result, message)

    def send_order(self, request):
        validate_all_fields(('order_id',), request.data)
        result, message = update_order_state_async.delay(
            self.__class__.__name__,
            request.data.get('order_id'),
            request.user.id,
            'assembled',
            'sent'
        ).get()

        return self.__result_handler(result, message)

    def deliver_order(self, request):
        validate_all_fields(('order_id',), request.data)
        result, message = update_order_state_async.delay(
            self.__class__.__name__,
            request.data.get('order_id'),
            request.user.id,
            'sent',
            'delivered'
        ).get()

        return self.__result_handler(result, message)

    def cancel_order(self, request):
        validate_all_fields(('order_id',), request.data)
        result, message = update_order_state_async.delay(
            self.__class__.__name__,
            request.data.get('order_id'),
            request.user.id,
            'new',
            'canceled'
        ).get()

        return self.__result_handler(result, message)


class PartnerOrdersViewSet(ViewSet):
    """Класс для получения заказов поставщиками."""

    permission_classes = (IsAuthenticated & IsShopOnly,)

    def list(self, request):
        order = Order.objects.filter(
            ordered_items__product_info__shop__user_id=request.user.id
        ).exclude(
            state='basket'
        ).prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter'
        ).select_related('contact').annotate(
            total_sum=Sum(
                F('ordered_items__quantity')
                * F('ordered_items__product_info__price')
            )
        ).distinct()

        serializer = OrderSerializer(order, many=True)
        return Response(serializer.data)


class PartnerStateViewSet(ViewSet):
    """Класс для работы со статусом поставщика."""

    permission_classes = (IsAuthenticated & IsShopOnly,)

    def get(self, request):
        serializer = ShopSerializer(request.user.shop)
        return Response(serializer.data)

    def create(self, request):
        state = request.data.get('state')
        if state is not None:
            try:
                shop = Shop.objects.get(user_id=request.user.id)
                shop.state = strtobool(state)
                shop.save()
                return JsonResponse(
                    {
                        'Status': True,
                        'Message': 'Статус успешно изменён!'
                    }
                )
            except Shop.DoesNotExist:
                return JsonResponse(
                    data={
                        'Status': False,
                        'Errors': 'Магазин не найден'},
                    status=status.HTTP_404_NOT_FOUND
                )
            except ValueError as error:
                return JsonResponse(
                    {
                        'Status': False,
                        'Errors': str(error)
                    }
                )

        return JsonResponse(
            {
                'Status': False,
                'Errors': 'Не указаны все необходимые аргументы'
            }
        )


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


def home_page(request):
    return render(request, 'index.html')


def upload_user_image(request, pk):
    return upload_image(
        request,
        model_name=User,
        image_field='avatar',
        obj_id=pk
    )


def upload_product_image(request, pk):
    return upload_image(
        request,
        model_name=Product,
        image_field='image',
        obj_id=pk
    )


def upload_image(request, model_name, image_field, obj_id):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.cleaned_data['image']
            instance = model_name.objects.get(pk=obj_id)
            setattr(instance, image_field, image)
            instance.save()
            process_image_async.delay(
                image.read(),
                model_name.__name__,
                image_field,
                obj_id
            )
            return render(request, 'success.html')
    else:
        form = ImageUploadForm()
    return render(
        request,
        'upload.html',
        {'form': form}
    )