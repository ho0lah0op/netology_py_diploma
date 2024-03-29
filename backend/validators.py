from django.core.validators import RegexValidator


class PhoneNumberValidator(RegexValidator):
    regex = r'^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$'
    message = 'Некорректный номер российского телефона.'

# ToDo: Добавить проверку на email (содержит ли @)
