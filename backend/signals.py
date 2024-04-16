from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.dispatch import Signal, receiver
from django_rest_passwordreset.signals import reset_password_token_created

from backend.constants import ORDER_STATUS
from backend.models import ConfirmEmailToken, User

new_user_registered = Signal()
new_order = Signal()
edit_order_state = Signal()
export_order = Signal()


@receiver(reset_password_token_created)
def custome_reset_password_token_created(sender,
                                         instance,
                                         reset_password_token,
                                         **kwargs):
    """Отправляет письмо с токеном для сброса пароля.

    При создании токена для сброса пароля необходимо отправить
    электронное письмо пользователю с токеном для сброса пароля.

   :param sender: Класс представления, который отправил сигнал.
   :param instance: Экземпляр представления, который отправил сигнал.
   :param reset_password_token: Объект модели токена сброса пароля.
   :param kwargs: Дополнительные аргументы.
   :return: Возвращает None.
    """
    msg = EmailMultiAlternatives(
        subject='Сброс пароля',
        body=(f'Токен сброса пароля для {reset_password_token.user}'
              f'\n{reset_password_token.key}'),
        from_email=settings.EMAIL_HOST_USER,
        to=[reset_password_token.user.email]
    )
    msg.send()


@receiver(new_user_registered)
def custom_new_user_registered(user_id, **kwargs):
    """Функция, отправляющая письмо с подтверждением по электронной почте.

    При регистрации нового пользователя генерируется
    и отправляется токен подтверждения по электронной почте.

    :param user_id: Идентификатор нового пользователя.
    :param kwargs: Дополнительные аргументы.
    :return: Возвращает None.
    """
    token, _ = ConfirmEmailToken.objects.get_or_create(user_id=user_id)
    msg = EmailMultiAlternatives(
        subject='Подтверждение регистрации',
        body=(f'Токен подтверждения регистрации: {token.user.email}'
              f'\n{token.key}'),
        from_email=settings.EMAIL_HOST_USER,
        to=[token.user.email]
    )
    msg.send()


@receiver(new_order)
def custom_new_order(user_id, **kwargs):
    """
    Отправляет письмо при подтверждении заказа покупателем.

    При подтверждении нового заказа генерируется и отправляется
    письмо покупателю с подтверждением заказа.

    :param user_id: Идентификатор пользователя, оформившего заказ.
    :param kwargs: Дополнительные аргументы.
    :return: Возвращает None.
    """
    user = User.objects.get(id=user_id)
    msg = EmailMultiAlternatives(
        subject='Оформление заказа',
        body=f'{user.first_name}, Спасибо за заказ!',
        from_email=settings.EMAIL_HOST_USER,
        to=[user.email]
    )
    msg.send()


@receiver(edit_order_state)
def custom_edit_order_state(user_id, state, **kwargs):
    """Отправляет письмо при редактировании статуса заказа.

    При изменении статуса заказа пользователю отправляется
    уведомление по электронной почте о новом статусе его заказа.

   :param user_id: Идентификатор пользователя, чей заказ был изменен.
   :param state: Новый статус заказа.
   :param kwargs: Дополнительные аргументы.
   :return: Возвращает None.
    """
    user = User.objects.get(id=user_id)
    msg = EmailMultiAlternatives(
        subject='Обновление статуса заказа',
        body=f'Статус заказа {ORDER_STATUS.get(state)} обновлен!',
        from_email=settings.EMAIL_HOST_USER,
        to=[user.email]
    )
    msg.send()


@receiver(export_order)
def custom_export_order(user_id, order_id, **kwargs):
    """Экспортирует заказ.

    При подтверждении заказа пользователю отправляется уведомление
    по электронной почте о подтверждении его заказа.

   :param int user_id: Идентификатор пользователя, чей заказ был подтвержден.
   :param int order_id: Идентификатор заказа, который был подтвержден.
   :param kwargs: Дополнительные аргументы.
   :return: Возвращает None.
   """
    user = User.objects.get(id=user_id)
    msg = EmailMultiAlternatives(
        subject='Подтверждение заказа',
        body=f'Ваш заказ {order_id} подтвержден!',
        from_email=settings.EMAIL_HOST_USER,
        to=[user.email]
    )
    msg.send()