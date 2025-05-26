import base64
import uuid

from django.core.files.base import ContentFile
from rest_framework import serializers


class Base64ImageField(serializers.ImageField):
    """
    Поле для поддержки base64-картинок в ImageField
    """

    def to_internal_value(self, data):
        # Проверка: строка начинается с base64
        if isinstance(data, str) and data.startswith('data:image'):
            # Разделение типа и base64-контента
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            if ext == 'jpeg':
                ext = 'jpg'
            name = f"{uuid.uuid4()}.{ext}"
            data = ContentFile(base64.b64decode(imgstr), name=name)

        return super().to_internal_value(data)
