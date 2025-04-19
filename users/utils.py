import os
import re

from rest_framework import serializers


def update_user_fields(user, data):
    user_data = data.get('user', {})

    validate_phone_format(user_data.get('contact_phone'))

    # Удаляем аватар, если пришёл null и раньше он был установлен
    if 'avatar' in user_data and user_data['avatar'] is None and user.avatar:
        # Сохраняем путь до удаления, чтобы потом убедиться, что файл есть
        avatar_path = user.avatar.path
        user.avatar.delete(save=False)  # Удалить файл, но не сохранять пока
        if os.path.isfile(avatar_path):
            os.remove(avatar_path)

    for field in ['full_name', 'bio', 'contact_phone', 'contact_email', 'avatar']:
        setattr(user, field, user_data.get(field, getattr(user, field)))
    user.save()


def validate_phone_format(phone):
    phone_regex = r'^\+?[\d\s\-()]{7,20}$'
    if phone and not re.match(phone_regex, phone):
        raise serializers.ValidationError("Введите корректный номер телефона.")
