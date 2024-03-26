from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django_rest_passwordreset.tokens import get_token_generator

from backend.constants import USERNAME_FIELD_LEN

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
            raise ValueError("The given email must be set")
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
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

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
    company = models.CharField("Компания", max_length=40, blank=True)
    position = models.CharField("Должность", max_length=40, blank=True)
    username = models.CharField(
        "Имя пользователя",
        max_length=USERNAME_FIELD_LEN,
        help_text=(
            f"Required. {USERNAME_FIELD_LEN} characters or fewer. "
            f"Letters, digits and @/./+/-/_ only."
        ),
        validators=[UnicodeUsernameValidator()],
        error_messages={
            "unique": "A user with that username already exists.",
        },
    )
    is_active = models.BooleanField(
        "Активный",
        default=False,
        help_text=(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    type = models.CharField(
        "Тип пользователя",
        choices=USER_TYPE_CHOICES,
        # ToDo: Константа
        max_length=5,
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
    # ToDo: Константа
    name = models.CharField("Название", max_length=50)
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
    # ToDo: Константа
    name = models.CharField("Название", max_length=40)
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
    # ToDo: Константа, verbose name
    name = models.CharField(max_length=80, verbose_name="Название")
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
    # ToDo: Константа, verbose name
    model = models.CharField(
        max_length=80,
        verbose_name="Модель",
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
    # ToDo: Константа
    name = models.CharField("Название", max_length=40)

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
    # ToDo: Константа
    value = models.CharField("Значение", max_length=100)

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
    # ToDo: Константа, verbose name
    city = models.CharField(max_length=50, verbose_name="Город")
    street = models.CharField(max_length=100, verbose_name="Улица")
    house = models.CharField(
        max_length=15,
        verbose_name="Дом"
    )
    structure = models.CharField(max_length=15, verbose_name="Корпус", blank=True)
    building = models.CharField(max_length=15, verbose_name="Строение", blank=True)
    apartment = models.CharField(max_length=15, verbose_name="Квартира", blank=True)
    phone = models.CharField(
        "Телефон",
        max_length=20,
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
        # ToDo: Константа
        "Статус", choices=STATE_CHOICES, max_length=15
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
        "When was this token generated",
        auto_now_add=True,
    )
    key = models.CharField(
        "Код подтверждения",
        # ToDo: Константа
        max_length=64,
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
