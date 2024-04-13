import requests
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import transaction
from rest_framework import serializers, status
from rest_framework.authtoken.models import Token
from yaml import load as load_yaml, Loader

from backend.mixins import CustomValidationMixin
from backend.models import (
    Category,
    ConfirmEmailToken,
    Contact,
    Order,
    OrderItem,
    Parameter,
    Product,
    ProductInfo,
    ProductParameter,
    Shop,
    User,
)
from backend.signals import new_user_registered
from backend.utils import validate_all_fields


class ContactSerializer(CustomValidationMixin,
                        serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ('id', 'city', 'street', 'house', 'structure',
                  'building', 'apartment', 'user', 'phone')
        read_only_fields = ('id',)
        extra_kwargs = {
            'user': {'write_only': True}
        }

    def validate_city(self, value):
        self.is_alpha(
            value,
            err_msg=('Название города может содержать '
                     'только буквы и дефис')
        )
        return value


class UserSerializer(CustomValidationMixin,
                     serializers.ModelSerializer):
    contacts = ContactSerializer(read_only=True, many=True)

    class Meta:
        model = User
        fields = (
            'id', 'first_name', 'last_name', 'email', 'company',
            'position', 'type', 'contacts', 'password'
        )
        read_only_fields = ('id',)
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        try:
            validate_password(validated_data.get('password'))
        except ValidationError as password_error:
            raise serializers.ValidationError(
                {'password': password_error.messages}
            )

        with transaction.atomic():
            user = User.objects.create_user(
                email=validated_data['email'],
                first_name=validated_data['first_name'],
                last_name=validated_data['last_name'],
                company=validated_data['company'],
                position=validated_data['position'],
                password=validated_data['password'],
            )

        new_user_registered.send(
            sender=self.__class__,
            user_id=user.id
        )
        return user

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            try:
                validate_password(validated_data['password'])
            except ValidationError as password_error:
                raise serializers.ValidationError(
                    {'password': password_error.messages}
                )

            instance.set_password(
                validated_data['password']
            )

        instance.first_name = validated_data.get(
            'first_name', instance.first_name
        )
        instance.last_name = validated_data.get(
            'last_name', instance.last_name
        )
        instance.email = validated_data.get(
            'email', instance.email
        )
        instance.company = validated_data.get(
            'company', instance.company
        )
        instance.position = validated_data.get(
            'position',
            instance.position
        )

        instance.save()
        return instance

    def validate(self, attrs):
        self.is_alpha(
            attrs.get('first_name'),
            err_msg='В имени имеются недопустимые символы'
        )

        self.is_alpha(
            attrs.get('last_name'),
            err_msg='В фамилии имеются недопустимые символы'
        )

        if attrs.get('password') is None:
            raise ValidationError(
                code=status.HTTP_400_BAD_REQUEST,
                message='Укажите пароль'
            )

        return attrs


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name',)
        read_only_fields = ('id',)

        def validate_name(self, value):
            """Проверяет существование категории по имени.

            :param str value: Название категории.
            :return: Название категории, если она существует.
            :raises serializers.ValidationError: Если категория
            с указанным именем не существует.
            """
            if not Category.objects.filter(name=value).exists():
                raise serializers.ValidationError(
                    'Категория с таким названием не существует.'
                )
            return value


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ('id', 'name', 'state',)
        read_only_fields = ('id',)


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()

    class Meta:
        model = Product
        fields = ('name', 'category',)

    def validate_name(self, value):
        """Проверяет существование продукта.

         Проверяет существование продукта с таким
         же именем в данной категории.

         :param str value: Название продукта.
         :return: Название продукта, если оно уникально в рамках категории.
         :raises serializers.ValidationError: Если продукт с указанным
         именем уже существует в данной категории.
        """

        category = self.context.get('category')
        if Product.objects.filter(
                name=value,
                category=category
        ).exists():
            raise serializers.ValidationError(
                'Продукт с таким же названием '
                'уже существует в данной категории.'
            )
        return value


class ProductParameterSerializer(serializers.ModelSerializer):
    parameter = serializers.StringRelatedField()

    class Meta:
        model = ProductParameter
        fields = ('parameter', 'value',)


class ProductInfoSerializer(CustomValidationMixin,
                            serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_parameters = ProductParameterSerializer(
        read_only=True,
        many=True
    )

    class Meta:
        model = ProductInfo
        fields = ('id', 'model', 'product', 'shop', 'quantity',
                  'price', 'price_rrc', 'product_parameters',)
        read_only_fields = ('id',)

    def validate(self, attrs):
        self.is_valid_quantity(
            attrs.get('quantity'),
            err_msg='Укажите корректное количество'
        )
        self.is_correct_price(attrs.get('price'))
        self.is_correct_price(attrs.get('price_rrc'))

        return attrs


class OrderItemSerializer(CustomValidationMixin,
                          serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('id', 'product_info', 'quantity', 'order',)
        read_only_fields = ('id',)
        extra_kwargs = {
            'order': {'write_only': True}
        }
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=OrderItem.objects.all(),
                fields=['order', 'product_info'],
                message='Позиция уже существует в корзине'
            )
        ]

    def validate_quantity(self, value):
        self.is_valid_quantity(
            value,
            err_msg='Укажите корректное количество'
        )
        return value


class OrderItemCreateSerializer(OrderItemSerializer):
    product_info = ProductInfoSerializer(read_only=True)


class OrderSerializer(serializers.ModelSerializer):
    ordered_items = OrderItemCreateSerializer(
        read_only=True,
        many=True
    )
    total_sum = serializers.IntegerField()
    contact = ContactSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'ordered_items', 'state',
                  'total_sum', 'contact')

        read_only_fields = ('id',)


class LoginAccountSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        validate_all_fields(('email', 'password'), data)
        user = authenticate(
            self.context.get('request'),
            username=data.get('email'),
            password=data.get('password')
        )
        if user is None or not user.is_active:
            raise serializers.ValidationError(
                'Не удалось авторизовать'
            )

        return data

    def save(self):
        user = authenticate(
            self.context.get('request'),
            username=self.validated_data.get('email'),
            password=self.validated_data.get('password')
        )
        token, _ = Token.objects.get_or_create(user=user)
        return token


class PartnerUpdateSerializer(serializers.Serializer):
    url = serializers.URLField()

    def validate_url(self, value):
        url_validator = URLValidator()
        try:
            url_validator(value)
        except serializers.ValidationError as err:
            raise serializers.ValidationError(str(err))
        return value

    def create(self, validated_data):
        user = self.context.get('request').user
        if not user.is_authenticated:
            raise serializers.ValidationError(
                code=status.HTTP_403_FORBIDDEN,
                detail='Требуется войти в систему'
            )

        if user.type != 'shop':
            raise serializers.ValidationError(
                code=status.HTTP_403_FORBIDDEN,
                detail='Только для магазинов'
            )

        data = load_yaml(
            requests.get(validated_data.get('url')).content,
            Loader=Loader
        )

        shop, _ = Shop.objects.get_or_create(
            name=data.get('shop'),
            user=user
        )
        for category in data.get('categories', []):
            category_obj, _ = Category.objects.get_or_create(
                id=category.get('id'),
                name=category.get('name')
            )
            category_obj.shops.add(shop)
            category_obj.save()

        ProductInfo.objects.filter(shop=shop).delete()
        for item in data.get('goods'):
            product, _ = Product.objects.get_or_create(
                name=item.get('name'),
                category_id=item.get('category')
            )

            product_info = ProductInfo.objects.create(
                product=product,
                external_id=item.get('id'),
                model=item.get('model'),
                price=item.get('price'),
                price_rrc=item.get('price_rrc'),
                quantity=item.get('quantity'),
                shop=shop
            )
            for name, value in item.get('parameters').items():
                parameter_object, _ = Parameter.objects.get_or_create(
                    name=name
                )
                ProductParameter.objects.create(
                    product_info=product_info,
                    parameter=parameter_object,
                    value=value
                )

        return {'Status': True}