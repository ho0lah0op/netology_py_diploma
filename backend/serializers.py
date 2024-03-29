from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError

from backend.models import User, Category, Shop, ProductInfo, Product, ProductParameter, OrderItem, Order, Contact


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ('id', 'city', 'street', 'house', 'structure',
                  'building', 'apartment', 'user', 'phone')
        read_only_fields = ('id',)
        extra_kwargs = {
            'user': {'write_only': True}
        }

    def validate_city(self, value):
        if not value.replace('-', '').replace(' ', '').isalpha():
            raise ValidationError(
                detail='Название города не может '
                       'содержать символы, кроме букв и дефиса',
                code=status.HTTP_400_BAD_REQUEST)
        return value


class UserSerializer(serializers.ModelSerializer):
    contacts = ContactSerializer(read_only=True, many=True)

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email',
                  'company', 'position', 'contacts')
        read_only_fields = ('id',)

    def validate_first_name(self, value):
        if not self.__is_alpha(value):
            raise ValidationError(
                detail='В имени имеются недопустимые символы',
                code=status.HTTP_400_BAD_REQUEST)
        return value

    def validate_last_name(self, value):
        if not self.__is_alpha(value):
            raise ValidationError(
                detail='В фамилии имеются недопустимые символы',
                code=status.HTTP_400_BAD_REQUEST)
        return value

    def __is_alpha(self, data):
        return data.replace('-', '').replace(' ', '').isalpha()


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name',)
        read_only_fields = ('id',)
        # ToDo: Валидатор на существование категории


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ('id', 'name', 'state',)
        read_only_fields = ('id',)


class ProductSerializer(serializers.ModelSerializer):
    # ToDo: Пересмотреть на то, что это лишний атрибут
    # ToDo: Валидатор на совпадения продуктов
    category = serializers.StringRelatedField()

    class Meta:
        model = Product
        fields = ('name', 'category',)


class ProductParameterSerializer(serializers.ModelSerializer):
    parameter = serializers.StringRelatedField()

    class Meta:
        model = ProductParameter
        fields = ('parameter', 'value',)


class ProductInfoSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_parameters = ProductParameterSerializer(read_only=True, many=True)

    class Meta:
        model = ProductInfo
        fields = ('id', 'model', 'product', 'shop',
                  'quantity', 'price', 'price_rrc', 'product_parameters',)
        read_only_fields = ('id',)

    def validate_quantity(self, value):
        if value.isdigit() and int(value) <= 0:
            raise ValidationError(
                detail='Укажите корректное количество',
                code=status.HTTP_400_BAD_REQUEST
            )
        return value

    def validate_price(self, value):
        self.__is_correct_price(value)
        return value

    def validate_price_rrc(self, value):
        self.__is_correct_price(value)
        return value

    def __is_correct_price(self, data):
        if not data.replace('.', '', 1).isdigit():
            raise ValidationError(
                detail='Некорректное значение! '
                       'Если дробное значение, укажите через точку',
                code=status.HTTP_400_BAD_REQUEST)

        if float(data) <= 0:
            raise ValidationError(
                detail='Стоимость должна быть больше 0.',
                code=status.HTTP_400_BAD_REQUEST)


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('id', 'product_info', 'quantity', 'order',)
        read_only_fields = ('id',)
        extra_kwargs = {
            'order': {'write_only': True}
        }

    def validate_quantity(self, value):
        if value.isdigit() and int(value) <= 0:
            raise ValidationError(
                detail='Укажите корректное количество',
                code=status.HTTP_400_BAD_REQUEST
            )
        return value


class OrderItemCreateSerializer(OrderItemSerializer):
    product_info = ProductInfoSerializer(read_only=True)


class OrderSerializer(serializers.ModelSerializer):
    ordered_items = OrderItemCreateSerializer(read_only=True, many=True)
    total_sum = serializers.IntegerField()
    contact = ContactSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'ordered_items', 'state',
                  # 'total_sum',
                  'contact', 'create_at')

        read_only_fields = ('id', 'created_at')
