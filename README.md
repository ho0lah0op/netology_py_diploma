# Проект: "Автоматизация закупок"

## Описание проекта:

- Проект по автоматизации закупок в розничной сети создан с целью оптимизации процесса заказа и управления товарами.

**Возможности:**

- Регистрация как продавца или покупателя
- Добавление товаров в магазин продавцом
- Добавление товаров в корзину покупателем
- Оформление заказа

---

## Используемые технологии:

- [x] Python 3.10
- [x] Django 5.0
- [x] DRF (Django Rest Framework)
- [x] Docker
- [x] PostgreSQL 14

---

## Как запустить проект на локальной машине:

1. Установить `Docker` и `Docker Compose`:
2. Клонировать репозиторий:

```
https://github.com/ho0lah0op/netology_py_diploma.git
```

3. Перейти в директорию:

```
cd netology_py_diploma
```

4. Создать файл `.env` и заполнить данными из `.env.example`

```
touch .env
sudo nano .env
```

> ВАЖНО!
>> - Как получить ключи для `SOCIAL_AUTH_GOOGLE_OAUTH2_KEY`
     и `SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET` [здесь](https://zappycode.com/tutorials/integrating-google-auth-with-django-projects)
>> - Как получить ключ для `SENTRY_DSN` [здесь](https://docs.sentry.io/platforms/python/integrations/django/)
>> - Как получить необходимые ключи для отправки
     писем [здесь](https://dev.to/shubhamkshatriya25/how-to-send-email-using-smtp-server-in-django-131f)

5. Собрать `Docker` образ, в корне проекта запустить команду:

```
sudo docker build -t shop_project .
```

6. Запустить `Docker Compose`:

```
sudo docker compose up -d
```

7. Проверьте статус запущенных контейнеров:

```
sudo docker compose ps
```

8. Создать базу данных:

```
sudo docker exec -it shop-db-1 psql -U postgres -d postgres
```

```
CREATE DATABASE YourDBName;
```

```
\q
```

9. Запуск `Redis-сервера`:

```
sudo docker compose exec web redis-server
```

10. Запуск `Celery`:

```
sudo docker compose exec web celery -A orders worker

# Для получения подробной информации используйте следующую команду
sudo docker compose exec web celery -A orders worker -l info -E
```

11. Выполнить миграции:

```
sudo docker compose exec web python manage.py makemigrations
sudo docker compose exec web python manage.py migrate
```

12. Создать суперпользователя:

```
sudo docker compose exec web python manage.py createsuperuser
```

13.

```
Если необходимо реализовать отправку писем, раскомментируйте следующие строки в файле `settings.py`:
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Эту строку закомментируйте
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

14. Генерация документации `API`:

    - Запустите команду в корне проекта:
    - ```
      python3 manage.py spectacular --color --file schema.yml
      ```

    - Или перейдите по следующему адресу:
    - ```
        localhost:8000/api/v1/schema/
      ```

15. Запуск тестов:

```
sudo docker compose exec web coverage run manage.py test

# или 
sudo docker compose exec web python3 manage.py test tests
```

16. Информация о покрытии тестами проекта:

```
sudo docker compose exec web coverage report -m
```

17. Загрузка изображений в профиль пользователя:

```
localhost:8000/user_image/{id}/
```

18. Загрузка изображений для продукта:

```
localhost:8000/product_image/{id}/
```

---

## Примеры запросов и ответов:

### `GET` запросы:

Запрос:

```
http://127.0.0.1:8000/api/v1/user/details/2/
```

Ответ:

```
{
    "id": 2,
    "first_name": "имя",
    "last_name": "фамилия",
    "email": "a.iskakov1989@gmail.com",
    "company": "asdads",
    "position": "345345",
    "type": "buyer",
    "contacts": []
}
```

Запрос:

```
http://127.0.0.1:8000/api/v1/user/contact/
```

Ответ:

```
[
    {
        "id": 1,
        "city": "Almaty",
        "street": "Shashkin street 40",
        "house": "Apartament 28",
        "structure": "123",
        "building": "123",
        "apartment": "123",
        "phone": "+79564563242"
    }
]
```

Запрос:

```
http://127.0.0.1:8000/api/v1/categories/
```

Ответ:

```
{
    "count": 3,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "Flash-накопители"
        },
        {
            "id": 15,
            "name": "Аксессуары"
        },
        {
            "id": 224,
            "name": "Смартфоны"
        }
    ]
}
```

Запрос:

```
http://127.0.0.1:8000/api/v1/partner/state
```

Ответ:

```
{
    "detail": "У вас недостаточно прав для выполнения данного действия."
}
```

Запрос:

```
http://127.0.0.1:8000/api/v1/shops/
```

Ответ:

```
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "Связной",
            "state": true
        }
    ]
}
```

### `POST` запросы:

Запрос:

```
http://{{server_address}}:8000/api/v1/partner/update/
```

Ответ:

```
{
    "Status": true,
    "Message": "Данные успешно импортированы!"
}
```

Запрос:

```
http://127.0.0.1:8000/api/v1/products
```

Ответ:

```
[
    {
        "id": 4,
        "model": "apple/iphone/xr",
        "product": {
            "name": "Смартфон Apple iPhone XR 128GB (синий)",
            "category": "Смартфоны"
        },
        "shop": 1,
        "quantity": 7,
        "price": 60000.0,
        "price_rrc": 64990.0,
        "product_parameters": [
            {
                "parameter": "Диагональ (дюйм)",
                "value": "6.1"
            },
            {
                "parameter": "Разрешение (пикс)",
                "value": "1792x828"
            },
            {
                "parameter": "Встроенная память (Гб)",
                "value": "256"
            },
            {
                "parameter": "Цвет",
                "value": "синий"
            }
        ]
    }
]
```

Запрос:

```
http://127.0.0.1:8000/api/v1/basket/
```

Ответ:

```
{
    "Status": true,
    "Message": 2
}
```

Запрос:

```
http://127.0.0.1:8000/api/v1/user/contact/
```

Ответ:

```
{
    "Status": true,
    "Message": "Контакт создан"
}
```

Запрос:

```
http:///127.0.0.1:8000/api/v1/order/confirm/
```

Ответ:

```
{
    "Status": true,
    "Message": "Заказ успешно подтвержден"
}
```

Запрос:

```
http:///127.0.0.1:8000/api/v1/order/assemble/
```

Ответ:

```
{
    "Status": true,
    "Message": "Заказ успешно переведен в состояние assembled"
}
```

Запрос:

```
http://127.0.0.1:8000/api/v1/order/cancel/
```

Ответ:

```
{
    "Status": false,
    "Errors": "Невозможно выполнить операцию, так как заказ находится в состоянии delivered"
}
```

### `PUT` запросы:

Запрос:

```
http://127.0.0.1:8000/api/v1/user/contact/1/
```

Ответ:

```
{
    "Status": true,
    "Message": "Данные контакта обновлены"
}
```

### `DELETE` запросы:

Запрос:

```
http://127.0.0.1:8000/api/v1/user/contact/1/
```

Ответ:

```
{
    "Status": true,
    "Message": "Контакт удалён"
}
```

---

## Автор проекта:

GitHub: [ho0lah0op](https://github.com/ho0lah0op)