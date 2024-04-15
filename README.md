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

8. Выполнить миграции:

```
sudo docker compose exec web python manage.py makemigrations
sudo docker compose exec web python manage.py migrate
```

9. Создать суперпользователя:

```
sudo docker compose exec web python manage.py createsuperuser
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