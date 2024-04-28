# Generated by Django 5.0.3 on 2024-04-28 13:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("backend", "0004_alter_contact_phone"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="image",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to="product_images/",
                verbose_name="Изображение",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="avatar",
            field=models.ImageField(
                blank=True, null=True, upload_to="user_avatars/", verbose_name="Аватар"
            ),
        ),
    ]