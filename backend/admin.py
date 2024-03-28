from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from backend.models import (
    User, Order, Shop, Product, Category, ProductInfo, Parameter,
    ProductParameter, Contact, OrderItem, ConfirmEmailToken
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'company', 'position', 'type', 'created_at', 'updated_at')
    list_filter = ('type', 'position', 'company')
    files = ('username', 'first_name', 'last_name', 'email', 'company', 'position', 'type', 'created_at', 'updated_at')
    search_fields = ('username', 'email', 'first_name', 'last_name')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'state', 'created_at', 'updated_at')
    list_filter = ('state', 'user')
    files = ('user', 'state', 'created_at', 'updated_at')
    search_fields = ('user', 'state')


# ToDo: Зарегистрировать все остальные модели
@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'user', 'state')
    list_filter = ('state', 'user')
    files = ('name', 'url', 'user', 'state')
    search_fields = ('name', 'url', 'user')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'created_at', 'updated_at')
    list_filter = ('name', 'category')
    files = ('name', 'category', 'created_at', 'updated_at')
    search_fields = ('name', 'category')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('name',)
    files = ('name', 'shops')
    search_fields = ('name',)


@admin.register(ProductInfo)
class ProductInfoAdmin(admin.ModelAdmin):
    list_display = ('product', 'model', 'quantity', 'price')
    list_filter = ('product', 'model')
    files = ('product', 'model', 'quantity', 'price')
    search_fields = ('product', 'model')


@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('name',)
    files = ('name',)
    search_fields = ('name',)


@admin.register(ProductParameter)
class ProductParameterAdmin(admin.ModelAdmin):
    list_display = ('product_info', 'parameter', 'value')
    list_filter = ('product_info', 'parameter')
    files = ('product_info', 'parameter', 'value')
    search_fields = ('product_info', 'parameter')


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('user', 'city', 'street', 'house', 'structure', 'building', 'apartment', 'phone')
    list_filter = ('user', 'city', 'phone')
    files = ('user', 'city', 'street', 'house', 'structure', 'building', 'apartment', 'phone')
    search_fields = ('user',)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product_info', 'quantity')
    list_filter = ('order', 'product_info')
    files = ('order', 'product_info', 'quantity')
    search_fields = ('order', 'product_info')


@admin.register(ConfirmEmailToken)
class ConfirmEmailAdmin(admin.ModelAdmin):
    list_display = ('user', 'key', 'created_at')
    list_filter = ('user',)
    files = ('user', 'key', 'created_at')
    search_fields = ('user',)
