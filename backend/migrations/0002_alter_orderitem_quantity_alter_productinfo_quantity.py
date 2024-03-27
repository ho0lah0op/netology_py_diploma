# Generated by Django 5.0.3 on 2024-03-27 15:05

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("backend", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="orderitem",
            name="quantity",
            field=models.PositiveSmallIntegerField(
                validators=[
                    django.core.validators.MinValueValidator(
                        1, message="Количество должно быть больше или равно 1"
                    )
                ],
                verbose_name="Количество",
            ),
        ),
        migrations.AlterField(
            model_name="productinfo",
            name="quantity",
            field=models.PositiveSmallIntegerField(
                validators=[
                    django.core.validators.MinValueValidator(
                        1, message="Количество должно быть больше или равно 1"
                    )
                ],
                verbose_name="Количество",
            ),
        ),
    ]
