from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from backend.models import User, Order, Shop, Product


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
# @admin.register(Shop)
# class ShopAdmin(admin.ModelAdmin):
#     list_display = ('name', 'url', 'user', 'state', 'created_at', 'updated_at')
#     list_filter = ('state', 'user')
#     files = ('name', 'url', 'user', 'state', 'created_at', 'updated_at')
#     search_fields = ('name', 'url', 'user')

admin.site.register(Product)
