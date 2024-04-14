import yaml
from django.core.management.base import BaseCommand

from backend.models import (
    Category,
    Product,
    ProductInfo,
    Shop
)


class Command(BaseCommand):
    help = 'Импортировать данные из файла YAML'

    def add_arguments(self, parser):
        parser.add_argument('--path', type=str)

    def handle(self, *args, **options):
        file_path = options.get('path')
        with open(file=file_path, mode='r') as file:
            data = yaml.safe_load(file)
            shop = self._create_or_get_shop(data.get('shop'))
            self._create_categories(shop, data.get('categories'))
            self._create_products(data.get('goods'))
        self.stdout.write(
            self.style.SUCCESS('Данные успешно импортированы!')
        )

    def _create_or_get_shop(self, shop_name):
        shop, _ = Shop.objects.get_or_create(name=shop_name)
        return shop

    def _create_categories(self, shop, categories_data):
        for category_data in categories_data:
            category, _ = Category.objects.get_or_create(
                id=category_data.get('id'),
                name=category_data.get('name')
            )
            category.shops.add(shop)

    def _create_products(self, products_data):
        for item in products_data:
            category_id = item.get('category')
            category = Category.objects.get(id=category_id)
            product, _ = Product.objects.get_or_create(
                name=item.get('name'),
                category=category
            )
            product_info, _ = ProductInfo.objects.get_or_create(
                external_id=item.get('id'),
                product=product,
                shop=category.shops.first(),
                defaults={
                    'model': item.get('model'),
                    'price': item.get('price'),
                    'price_rrc': item.get('price_rrc'),
                    'quantity': item.get('quantity')
                }
            )
            self._update_product_parameters(
                product_info, item.get('parameters')
            )

    def _update_product_parameters(self, product, parameters_data):
        for name, value in parameters_data.items():
            setattr(product, name, value)
        product.save()