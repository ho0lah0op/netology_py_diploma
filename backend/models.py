from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import MinValueValidator
from django.db import models
from django_rest_passwordreset.tokens import get_token_generator

from backend.constants import (
    APARTMENT_FIELD_LEN,
    BUILDING_FIELD_LEN,
    CATNAME_FIELD_LEN,
    CITY_FIELD_LEN,
    COMPANY_FIELD_LEN,
    HOUSE_FIELD_LEN,
    KEY_FIELD_LEN,
    MIN_ORDER_QUANTITY_VALUE,
    MIN_QUANTITY_VALUE,
    MIN_PRICE_VALUE,
    MODEL_FIELD_LEN,
    ORDER_STATUS,
    PARAMNAME_FIELD_LEN,
    POSITION_FIELD_LEN,
    PHONE_FIELD_LEN,
    PRNAME_FIELD_LEN,
    SHOPNAME_FIELD_LEN,
    STATE_FIELD_LEN,
    STREET_FIELD_LEN,
    STRUCTURE_FIELD_LEN,
    TYPE_FIELD_LEN,
    USERNAME_FIELD_LEN,
    USER_TYPE_CHOICES,
    VALUE_FIELD_LEN,
)
from backend.mixins import TimeStampMixin
from backend.validators import PhoneNumberValidator


class UserManager(BaseUserManager):
    """Базовый класс для управления пользователями."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Создает и сохраняет пользователя.

        С указанным именем пользователя,
        адресом электронной почты и паролем."""
        if not email:
            raise ValueError('Адрес электронной почты не указан!')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(
                'Супер-пользователь обязан иметь is_staff=True.'
            )
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(
                'Супер-пользователь обязан иметь is_staff=True.'
            )

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser, TimeStampMixin):
    """Стандартная модель пользователей."""

    REQUIRED_FIELDS = ['username']
    USERNAME_FIELD = 'email'
    objects = UserManager()
    email = models.EmailField('Электронная почта', unique=True)
    company = models.CharField(
        'Компания',
        max_length=COMPANY_FIELD_LEN,
        blank=True
    )
    position = models.CharField(
        'Должность',
        max_length=POSITION_FIELD_LEN,
        blank=True
    )
    username = models.CharField(
        'Имя пользователя',
        max_length=USERNAME_FIELD_LEN,
        help_text=(
            f'Обязательно: {USERNAME_FIELD_LEN} значений или меньше. '
            'Только буквы, цифры и спецсимволы: @/./+/-/_'
        ),
        validators=[UnicodeUsernameValidator()],
        error_messages={
            'unique': 'Пользователь с таким username уже существует.',
        },
    )
    is_active = models.BooleanField(
        'Активный',
        default=False,
        help_text=(
            'Указывает на то, что пользователь активный'
            'Снимите флажок, чтобы сделать пользователя неактивным.'
        ),
    )
    type = models.CharField(
        'Тип пользователя',
        choices=tuple(USER_TYPE_CHOICES.items()),
        max_length=TYPE_FIELD_LEN,
        default='buyer',
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Список пользователей'
        ordering = ('username', 'email')

    def __str__(self):
        return self.username


class Shop(models.Model):
    objects = models.manager.Manager()
    name = models.CharField(
        'Название',
        max_length=SHOPNAME_FIELD_LEN
    )
    url = models.URLField('Ссылка', null=True, blank=True)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name='Пользователь'
    )
    state = models.BooleanField(
        'Статус получения заказов',
        default=True
    )

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = 'Список магазинов'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Category(models.Model):
    objects = models.manager.Manager()
    name = models.CharField(
        'Название',
        max_length=CATNAME_FIELD_LEN
    )
    shops = models.ManyToManyField(
        Shop,
        related_name='categories',
        blank=True,
        verbose_name='Магазины'
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Список категорий'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Product(TimeStampMixin):
    objects = models.manager.Manager()
    name = models.CharField(
        'Название',
        max_length=PRNAME_FIELD_LEN
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='Категория',
    )

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Список продуктов'
        ordering = ('name',)

    def __str__(self):
        return self.name


class ProductInfo(models.Model):
    objects = models.manager.Manager()
    model = models.CharField(
        'Модель',
        max_length=MODEL_FIELD_LEN,
        blank=True
    )
    external_id = models.PositiveIntegerField('Внешний ИД')
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='product_infos',
        null=True,
        blank=True,
        verbose_name='Продукт',
    )
    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        related_name='product_infos',
        blank=True,
        verbose_name='Магазин',
    )
    quantity = models.PositiveSmallIntegerField(
        'Количество',
        validators=[
            MinValueValidator(
                MIN_QUANTITY_VALUE,
                message=('Количество должно быть '
                         f'больше или равно {MIN_QUANTITY_VALUE}')
            )
        ]
    )
    price = models.FloatField(
        'Цена',
        validators=[
            MinValueValidator(
                MIN_PRICE_VALUE,
                message=f'Цена должна быть больше {MIN_PRICE_VALUE}'
            )
        ]
    )
    price_rrc = models.FloatField(
        'Рекомендуемая розничная цена',
        validators=[
            MinValueValidator(
                MIN_PRICE_VALUE,
                message=('Рекомендуемая розничная цена '
                         f'должна быть больше {MIN_PRICE_VALUE}')
            )
        ]
    )

    class Meta:
        verbose_name = 'Информация о продукте'
        verbose_name_plural = 'Информационный список о продуктах'
        constraints = [
            models.UniqueConstraint(
                fields=['product', 'shop', 'external_id'],
                name='unique_product_info'
            ),
        ]


class Parameter(models.Model):
    objects = models.manager.Manager()
    name = models.CharField(
        'Название',
        max_length=PARAMNAME_FIELD_LEN
    )

    class Meta:
        verbose_name = 'Имя параметра'
        verbose_name_plural = 'Список имен параметров'
        ordering = ('-name',)

    def __str__(self):
        return self.name


class ProductParameter(models.Model):
    objects = models.manager.Manager()
    product_info = models.ForeignKey(
        ProductInfo,
        on_delete=models.CASCADE,
        related_name='product_parameters',
        verbose_name='Информация о продукте',
    )
    parameter = models.ForeignKey(
        Parameter,
        on_delete=models.CASCADE,
        related_name='product_parameters',
        verbose_name='Параметр',
    )
    value = models.CharField(
        'Значение',
        max_length=VALUE_FIELD_LEN
    )

    class Meta:
        verbose_name = 'Параметр'
        verbose_name_plural = 'Список параметров'
        constraints = [
            models.UniqueConstraint(
                fields=['product_info', 'parameter'],
                name='unique_product_parameter'
            ),
        ]


class Contact(models.Model):
    objects = models.manager.Manager()
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='contacts',
        blank=True,
        verbose_name='Пользователь'
    )
    city = models.CharField(
        'Город',
        max_length=CITY_FIELD_LEN
    )
    street = models.CharField(
        'Улица',
        max_length=STREET_FIELD_LEN
    )
    house = models.CharField(
        'Дом',
        max_length=HOUSE_FIELD_LEN
    )
    structure = models.CharField(
        'Корпус',
        max_length=STRUCTURE_FIELD_LEN,
        blank=True
    )
    building = models.CharField(
        'Строение',
        max_length=BUILDING_FIELD_LEN,
        blank=True
    )
    apartment = models.CharField(
        'Квартира',
        max_length=APARTMENT_FIELD_LEN,
        blank=True
    )
    phone = models.CharField(
        'Телефон',
        max_length=PHONE_FIELD_LEN,
        unique=True,
        validators=[PhoneNumberValidator()]
    )

    class Meta:
        verbose_name = 'Контакты пользователя'
        verbose_name_plural = 'Список контактов пользователя'

    def __str__(self):
        return f'{self.city} {self.street} {self.house}'


class Order(TimeStampMixin):
    objects = models.manager.Manager()
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='Пользователь'
    )
    state = models.CharField(
        'Статус',
        choices=tuple(ORDER_STATUS.items()),
        max_length=STATE_FIELD_LEN
    )
    contact = models.ForeignKey(
        Contact,
        on_delete=models.CASCADE,
        verbose_name='Контакт',
    )

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Список заказ'
        ordering = ('-created_at',)

    def __str__(self):
        return f'Заказ №{self.pk} - {ORDER_STATUS.get(self.state)}'


class OrderItem(models.Model):
    objects = models.manager.Manager()
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='ordered_items',
        verbose_name='Заказ',
    )

    product_info = models.ForeignKey(
        ProductInfo,
        on_delete=models.CASCADE,
        related_name='ordered_items',
        verbose_name='Информация о продукте',
    )
    quantity = models.PositiveSmallIntegerField(
        'Количество',
        validators=[
            MinValueValidator(
                MIN_ORDER_QUANTITY_VALUE,
                message=('Количество должно быть '
                         f'больше или равно {MIN_ORDER_QUANTITY_VALUE}')
            )
        ]
    )

    class Meta:
        verbose_name = 'Заказанная позиция'
        verbose_name_plural = 'Список заказанных позиций'
        constraints = [
            models.UniqueConstraint(
                fields=['order_id', 'product_info'],
                name='unique_order_item'
            ),
        ]


class ConfirmEmailToken(models.Model):
    objects = models.manager.Manager()
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='confirm_email_tokens',
        verbose_name='Владелец токена',
    )
    created_at = models.DateTimeField(
        'Дата генерации токена',
        auto_now_add=True,
    )
    key = models.CharField(
        'Код подтверждения',
        max_length=KEY_FIELD_LEN,
        db_index=True,
        unique=True
    )

    class Meta:
        verbose_name = 'Токен подтверждения Email'
        verbose_name_plural = 'Токены подтверждения Email'

    @staticmethod
    def generate_key():
        """Генерирует псевдослучайный код.

        Использует os.urandom и binascii.hexlify."""
        return get_token_generator().generate_token()

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(ConfirmEmailToken, self).save(*args, **kwargs)

    def __str__(self):
        return f'Токен сброса пароля для: {self.user}'