import re

from django.db import models
from rest_framework import status
from rest_framework.exceptions import ValidationError


class TimeStampMixin(models.Model):
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)

    class Meta:
        abstract = True


class CustomValidationMixin:
    """Содержит кастомные валидации."""

    def is_alpha(self, value, err_msg='Error'):
        """Проверяет корректность строки.

        Состоит ли передаваемая строка только из букв, пробела и дефиса.

        :param value: Проверяемая строка.
        :param err_msg: Выводимое сообщение об ошибке. По умолчанию "Error".
        :rtype: None
        """
        if not re.match(r'^[a-zA-Zа-яА-Я- ]+$', value):
            raise ValidationError(
                detail=err_msg,
                code=status.HTTP_400_BAD_REQUEST
            )

    def is_valid_quantity(self, value, err_msg='Error'):
        """Проверяет, является ли переданное значение натуральным числом.
        :param value: Проверяемое значение.
        :param err_msg: Выводимое сообщение об ошибке. По умолчанию "Error".
        :rtype: None
        """
        if not value.isdigit():
            raise ValidationError(
                detail='Укажите числовое значение',
                code=status.HTTP_400_BAD_REQUEST
            )

        if int(value) <= 0:
            raise ValidationError(
                detail=err_msg,
                code=status.HTTP_400_BAD_REQUEST
            )

    def is_correct_price(
            self,
            data,
            err_msg='Стоимость должна быть больше 0.'
    ):
        """Проверяет, является ли передаваемое значение правильной ценой."""

        try:
            price = float(data)
        except ValueError:
            raise ValidationError(
                detail=('Некорректное значение! '
                        'Если дробное значение, укажите через точку'),
                code=status.HTTP_400_BAD_REQUEST
            )

        if price <= 0:
            raise ValidationError(
                detail=err_msg,
                code=status.HTTP_400_BAD_REQUEST
            )
