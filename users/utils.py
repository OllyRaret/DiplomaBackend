import os


def update_user_fields(user, data):
    user_data = data.get('user', {})

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
