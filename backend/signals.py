from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.tokens import default_token_generator
from django.dispatch import Signal, receiver
from django_rest_passwordreset.signals import reset_password_token_created

from backend.constants import ORDER_STATUS
from backend.models import ConfirmEmailToken, User

new_user_registered = Signal()
new_order = Signal()
edit_order_state = Signal()
order_confirmed = Signal()


@receiver(new_order)
def send_order_confirmation_email(sender, user_id, **kwargs):
    """Отправляет письмо с токеном подтверждения заказа.

    Сигнал отправляется при создании нового заказа пользователем.
    Пользователю отправляется письмо с токеном подтверждения заказа.

    :param sender: Класс представления, который отправил сигнал.
    :param user_id: Идентификатор пользователя, для которого создан заказ.
    :param kwargs: Дополнительные аргументы.
    :return: Возвращает None.
    """
    user = User.objects.get(id=user_id)
    token = default_token_generator.make_token(user)
    email = EmailMultiAlternatives(
        subject='Подтверждение заказа',
        body=('Ваш заказ ожидает подтверждения.\n'
              f'Ваш токен: {token}'),
        from_email=settings.EMAIL_HOST_USER,
        to=[user.email]
    )
    email.send()


@receiver(order_confirmed)
def send_order_confirmed(sender, user_id, order_id, contact, **kwargs):
    """Отправляет письмо с подтверждением заказа.

    Сигнал отправляется при подтверждении заказа.
    Пользователю отправляется письмо с подтверждением заказа,
    содержащее информацию о заказе и контактных данных.

    :param sender: Класс представления, который отправил сигнал.
    :param user_id: Идентификатор пользователя, для которого создан заказ.
    :param order_id: Идентификатор подтвержденного заказа.
    :param contact: Контактные данные пользователя.
    :param kwargs: Дополнительные аргументы.
    :return: Возвращает None.
    """
    user = User.objects.get(id=user_id)
    body_content = (
        f'{user.first_name}, Спасибо за заказ! '
        f'Ваш заказ №{order_id} подтвержден!'
        f'\nАдрес: г.{contact.city}, ул.{contact.street} '
        f'{contact.house}\nНомер телефона: {contact.phone}'
    )

    msg = EmailMultiAlternatives(
        subject='Ваш заказ подтвержден',
        body=body_content,
        from_email=settings.EMAIL_HOST_USER,
        to=[user.email]
    )
    msg.send()


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
        body=f'{user.first_name}, Ваш заказ ожидает подтверждения!',
        from_email=settings.EMAIL_HOST_USER,
        to=[user.email]
    )
    msg.send()


@receiver(edit_order_state)
def custom_edit_order_state(sender, user_id, order_id, state, **kwargs):
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