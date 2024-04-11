from rest_framework import serializers

from backend.mixins import CustomValidationMixin
from backend.models import (
    Category,
    Contact,
    Order,
    OrderItem,
    Product,
    ProductInfo,
    ProductParameter,
    Shop,
    User,
)


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
        fields = ('id', 'first_name', 'last_name', 'email',
                  'company', 'position', 'contacts')
        read_only_fields = ('id',)

    def validate(self, attrs):
        self.is_alpha(
            attrs.get('first_name'),
            err_msg='В имени имеются недопустимые символы'
        )

        self.is_alpha(
            attrs.get('last_name'),
            err_msg='В фамилии имеются недопустимые символы'
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
                  'total_sum', 'contact', 'create_at')

        read_only_fields = ('id', 'created_at')
