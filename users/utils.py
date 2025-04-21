import os
import re

from rest_framework import serializers


def update_user_fields(user, data):
    user_data = data.get('user', {})

    validate_phone_format(user_data.get('contact_phone'))

    new_avatar = user_data.get('avatar', None)
    old_avatar = user.avatar

    # Удаление старого аватара, если передан null или новый аватар
    if 'avatar' in user_data and old_avatar and (
            new_avatar is None or new_avatar != old_avatar
    ):
        avatar_path = old_avatar.path
        user.avatar.delete(save=False)
        if os.path.isfile(avatar_path):
            os.remove(avatar_path)

    for field in ['full_name', 'bio', 'contact_phone', 'contact_email', 'avatar']:
        setattr(user, field, user_data.get(field, getattr(user, field)))
    user.save()


def validate_phone_format(phone):
    phone_regex = r'^\+?[\d\s\-()]{7,20}$'
    if phone and not re.match(phone_regex, phone):
        raise serializers.ValidationError("Введите корректный номер телефона.")
