from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django_rest_passwordreset.tokens import get_token_generator

from backend.constants import USERNAME_FIELD_LEN, COMPANY_FIELD_LEN, POSITION_FIELD_LEN, TYPE_FIELD_LEN, \
    SHOPNAME_FIELD_LEN, CATNAME_FIELD_LEN, PRNAME_FIELD_LEN, PARAMNAME_FIELD_LEN, \
    MODEL_FIELD_LEN, VALUE_FIELD_LEN, CITY_FIELD_LEN, \
    STREET_FIELD_LEN, HOUSE_FIELD_LEN, STRUCTURE_FIELD_LEN, BUILDING_FIELD_LEN, APARTMENT_FIELD_LEN, PHONE_FIELD_LEN, \
    STATE_FIELD_LEN, KEY_FIELD_LEN

STATE_CHOICES = (
    ("basket", "Статус корзины"),
    ("new", "Новый"),
    ("confirmed", "Подтвержден"),
    ("assembled", "Собран"),
    ("sent", "Отправлен"),
    ("delivered", "Доставлен"),
    ("canceled", "Отменен"),
)


class UserManager(BaseUserManager):
    """
    Миксин для управления пользователями
    """

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not email:
            raise ValueError("Адрес электронной почты не указан!")
        # TODO: 1. Английский на русский
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Супер-пользователь обязан иметь is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Супер-пользователь обязан иметь is_staff=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Стандартная модель пользователей
    """

    USER_TYPE_CHOICES = (
        ("shop", "Магазин"),
        ("buyer", "Покупатель"),
    )
    REQUIRED_FIELDS = ["username"]
    USERNAME_FIELD = "email"
    objects = UserManager()
    email = models.EmailField("Электронная почта", unique=True)
    # ToDo: 2. Вынести max_length в отдельные константы
    company = models.CharField(
        "Компания",
        max_length=COMPANY_FIELD_LEN,
        blank=True
    )
    position = models.CharField(
        "Должность",
        max_length=POSITION_FIELD_LEN,
        blank=True
    )
    username = models.CharField(
        "Имя пользователя",
        max_length=USERNAME_FIELD_LEN,
        help_text=(
            f"Обязательно: {USERNAME_FIELD_LEN} значений или меньше. "
            f"Только буквы, цифры и спецсимволы: @/./+/-/_"
        ),
        validators=[UnicodeUsernameValidator()],
        error_messages={
            "unique": "Пользователь с таким username уже существует.",
        },
    )
    is_active = models.BooleanField(
        "Активный",
        default=False,
        help_text=(
            "Указывает на то, что пользователь активный"
            "Снимите флажок, чтобы сделать пользователя неактивным."
        ),
    )
    type = models.CharField(
        "Тип пользователя",
        choices=USER_TYPE_CHOICES,
        max_length=TYPE_FIELD_LEN,
        default="buyer",
    )

    # ToDo: Дата создания и дата обновления пользователя

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Список пользователей"
        ordering = ("username", "email")


class Shop(models.Model):
    objects = models.manager.Manager()
    name = models.CharField(
        "Название",
        max_length=SHOPNAME_FIELD_LEN
    )
    url = models.URLField("Ссылка", null=True, blank=True)
    user = models.OneToOneField(
        User,
        verbose_name="Пользователь",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    state = models.BooleanField("Статус получения заказов", default=True)

    class Meta:
        verbose_name = "Магазин"
        verbose_name_plural = "Список магазинов"
        ordering = ("name",)

    def __str__(self):
        return self.name


class Category(models.Model):
    objects = models.manager.Manager()
    name = models.CharField(
        "Название",
        max_length=CATNAME_FIELD_LEN)
    shops = models.ManyToManyField(
        Shop,
        verbose_name="Магазины",
        related_name="categories",
        blank=True
    )

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Список категорий"
        ordering = ("name",)

    def __str__(self):
        return self.name


class Product(models.Model):
    objects = models.manager.Manager()
    name = models.CharField(
        "Название",
        max_length=PRNAME_FIELD_LEN
    )
    category = models.ForeignKey(
        Category,
        verbose_name="Категория",
        related_name="products",
        # blank=True,
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Список продуктов"
        ordering = ("name",)

    def __str__(self):
        return self.name


class ProductInfo(models.Model):
    objects = models.manager.Manager()
    model = models.CharField(
        "Модель",
        max_length=MODEL_FIELD_LEN,
        blank=True
    )
    # ToDo: Пересмотреть external id (нужно ли?)
    external_id = models.PositiveIntegerField("Внешний ИД")
    product = models.ForeignKey(
        Product,
        verbose_name="Продукт",
        # ToDo: Переименовать related name
        related_name="product_infos",
        # blank=True,
        on_delete=models.CASCADE,
    )
    shop = models.ForeignKey(
        Shop,
        verbose_name="Магазин",
        # ToDo: Переименовать related name
        related_name="product_infos",
        # blank=True,
        on_delete=models.CASCADE,
    )
    quantity = models.PositiveSmallIntegerField(
        "Количество",
        validators=[
            # ToDo: Валидация количества больше нуля
        ]
    )
    price = models.FloatField(
        "Цена",
        validators=[
            # ToDo: валидация минимальной цены (стоимости)
        ]
    )
    price_rrc = models.FloatField(
        "Рекомендуемая розничная цена",
        validators=[
            # ToDo: валидация минимальной цены (стоимости)
        ]
    )

    class Meta:
        verbose_name = "Информация о продукте"
        verbose_name_plural = "Информационный список о продуктах"
        constraints = [
            models.UniqueConstraint(
                fields=["product", "shop", "external_id"],
                name="unique_product_info"
            ),
        ]


class Parameter(models.Model):
    objects = models.manager.Manager()
    name = models.CharField(
        "Название",
        max_length=PARAMNAME_FIELD_LEN
    )

    class Meta:
        verbose_name = "Имя параметра"
        verbose_name_plural = "Список имен параметров"
        ordering = ("-name",)

    def __str__(self):
        return self.name


class ProductParameter(models.Model):
    objects = models.manager.Manager()
    product_info = models.ForeignKey(
        ProductInfo,
        verbose_name="Информация о продукте",
        related_name="product_parameters",
        # blank=True,
        on_delete=models.CASCADE,
    )
    parameter = models.ForeignKey(
        Parameter,
        verbose_name="Параметр",
        related_name="product_parameters",
        # blank=True,
        on_delete=models.CASCADE,
    )
    value = models.CharField(
        "Значение",
        max_length=VALUE_FIELD_LEN
    )

    class Meta:
        verbose_name = "Параметр"
        verbose_name_plural = "Список параметров"
        constraints = [
            models.UniqueConstraint(
                fields=["product_info", "parameter"],
                name="unique_product_parameter"
            ),
        ]


class Contact(models.Model):
    objects = models.manager.Manager()
    user = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        related_name="contacts",
        blank=True,
        on_delete=models.CASCADE,
    )
    city = models.CharField(
        "Город",
        max_length=CITY_FIELD_LEN
    )
    street = models.CharField(
        "Улица",
        max_length=STREET_FIELD_LEN
    )
    house = models.CharField(
        "Дом",
        max_length=HOUSE_FIELD_LEN
    )
    structure = models.CharField(
        "Корпус",
        max_length=STRUCTURE_FIELD_LEN,
        blank=True
    )
    building = models.CharField(
        "Строение",
        max_length=BUILDING_FIELD_LEN,
        blank=True
    )
    apartment = models.CharField(
        "Квартира",
        max_length=APARTMENT_FIELD_LEN,
        blank=True
    )
    phone = models.CharField(
        "Телефон",
        max_length=PHONE_FIELD_LEN,
        validators=[
            # ToDo: Валидация телефонных номеров
        ]
    )

    class Meta:
        verbose_name = "Контакты пользователя"
        verbose_name_plural = "Список контактов пользователя"

    def __str__(self):
        return f"{self.city} {self.street} {self.house}"


class Order(models.Model):
    objects = models.manager.Manager()
    user = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        related_name="orders",
        # blank=True,
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    state = models.CharField(
        "Статус",
        choices=STATE_CHOICES,
        max_length=STATE_FIELD_LEN
    )
    contact = models.ForeignKey(
        Contact,
        verbose_name="Контакт",
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Список заказ"
        ordering = ("-created_at",)

    def __str__(self):
        return str(self.created_at)

    # @property
    # def sum(self):
    #     return self.ordered_items.aggregate(total=Sum("quantity"))["total"]


class OrderItem(models.Model):
    objects = models.manager.Manager()
    order = models.ForeignKey(
        Order,
        verbose_name="Заказ",
        related_name="ordered_items",
        # blank=True,
        on_delete=models.CASCADE,
    )

    product_info = models.ForeignKey(
        ProductInfo,
        verbose_name="Информация о продукте",
        related_name="ordered_items",
        # blank=True,
        on_delete=models.CASCADE,
    )
    quantity = models.PositiveSmallIntegerField(
        "Количество",
        validators=[
            # ToDo: Валидация количества больше нуля
        ]
    )

    class Meta:
        verbose_name = "Заказанная позиция"
        verbose_name_plural = "Список заказанных позиций"
        constraints = [
            models.UniqueConstraint(
                fields=["order_id", "product_info"],
                name="unique_order_item"
            ),
        ]


class ConfirmEmailToken(models.Model):
    objects = models.manager.Manager()
    user = models.ForeignKey(
        User,
        related_name="confirm_email_tokens",
        on_delete=models.CASCADE,
        # ToDo: На русский
        verbose_name="The User which is associated to this password reset token",
    )
    created_at = models.DateTimeField(
        "Время генерации токена",
        auto_now_add=True,
    )
    key = models.CharField(
        "Код подтверждения",
        # ToDo: Константа
        max_length=KEY_FIELD_LEN,
        db_index=True,
        unique=True
    )

    class Meta:
        verbose_name = "Токен подтверждения Email"
        verbose_name_plural = "Токены подтверждения Email"

    @staticmethod
    def generate_key():
        """generates a pseudo random code
        using os.urandom and binascii.hexlify"""
        return get_token_generator().generate_token()

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(ConfirmEmailToken, self).save(*args, **kwargs)

    def __str__(self):
        return f"Password reset token for user {self.user}"
