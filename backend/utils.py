from rest_framework import serializers, status


def validate_all_fields(fields, data):
    for field in fields:
        if field not in data:
            raise serializers.ValidationError(
                detail=f'Укажите обязательный аргумент {field}',
                code=status.HTTP_400_BAD_REQUEST
            )