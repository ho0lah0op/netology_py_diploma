# Константы User
USERNAME_FIELD_LEN = 150
COMPANY_FIELD_LEN = 40
POSITION_FIELD_LEN = 40
TYPE_FIELD_LEN = 5
USER_TYPE_CHOICES = {
    'shop': 'Магазин',
    'buyer': 'Покупатель',
}

CACHE_TIMEOUT = 60

# Константы Shop
SHOPNAME_FIELD_LEN = 50

# Константы Category
CATNAME_FIELD_LEN = 40

# Константы Product
PRNAME_FIELD_LEN = 80

# Константы ProductInfo
MODEL_FIELD_LEN = 80
MIN_QUANTITY_VALUE = 1
MIN_PRICE_VALUE = 0.1

# Константы Parameter
PARAMNAME_FIELD_LEN = 40

# Константы ProductParameter
VALUE_FIELD_LEN = 100

# Константы Contact
CITY_FIELD_LEN = 50
STREET_FIELD_LEN = 100
HOUSE_FIELD_LEN = 15
STRUCTURE_FIELD_LEN = 15
BUILDING_FIELD_LEN = 15
APARTMENT_FIELD_LEN = 15
PHONE_FIELD_LEN = 20

# Константы Order
STATE_FIELD_LEN = 15
MIN_ORDER_QUANTITY_VALUE = 1

# Константы ConfirmEmailToken
KEY_FIELD_LEN = 64

# Статусы заказа
ORDER_STATUS = {
    'basket': 'Статус корзины',
    'new': 'Новый',
    'confirmed': 'Подтвержден',
    'assembled': 'Собран',
    'sent': 'Отправлен',
    'delivered': 'Доставлен',
    'canceled': 'Отменен',
}