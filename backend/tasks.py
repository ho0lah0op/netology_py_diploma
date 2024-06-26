from io import BytesIO

from PIL import Image
from celery import shared_task
from django.core.files.uploadedfile import (
    SimpleUploadedFile
)
from django.db import transaction, IntegrityError

from backend.models import Order
from backend.signals import (
    edit_order_state,
    new_order,
    order_confirmed
)


@shared_task
def create_order_async(sender, user_id):
    try:
        new_order.send(sender=sender, user_id=user_id)
    except IntegrityError as err:
        return False, f'Неправильно указаны аргументы: {err}'
    return True, 'Заказ успешно создан!'


@shared_task
def confirm_order_async(sender, user_id, order_id, contact_id):
    try:
        order_confirmed.send(
            sender=sender,
            user_id=user_id,
            order_id=order_id,
            contact_id=contact_id
        )
    except Order.DoesNotExist:
        return False, f'Заказ №{order_id} уже подтвержден или отменён'
    return True, f'Заказ №{order_id} успешно подтвержден'


@shared_task()
def update_order_state_async(sender,
                             order_id,
                             user_id,
                             expected_state,
                             new_state):
    try:
        with transaction.atomic():
            order = Order.objects.select_for_update().get(
                id=order_id,
                user_id=user_id
            )
            if order.state != expected_state:
                return False, ('Невозможно выполнить операцию, '
                               f'заказ находится в состоянии {order.state}')

            order.state = new_state
            order.save()
            edit_order_state.send(
                sender=sender,
                user_id=user_id,
                order_id=order_id,
                state=new_state
            )

    except Order.DoesNotExist:
        return False, 'Заказ не найден'
    return True, (f'Заказ №{order.id} успешно переведен '
                  f'в состояние {new_state}')


@shared_task
def process_image_async(image_data,
                        model_name,
                        image_field,
                        obj_id):
    img = Image.open(BytesIO(image_data))
    img.thumbnail((100, 100))
    output = BytesIO()
    img.save(output, format='JPEG')
    output.seek(0)
    model = globals()[model_name]
    instance = model.objects.get(pk=obj_id)
    setattr(
        instance,
        image_field,
        SimpleUploadedFile(
            name='temp.png',
            content=output.getvalue()
        )
    )
    instance.save()