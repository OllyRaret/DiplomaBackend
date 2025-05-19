from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

get_current_user_profile_doc = swagger_auto_schema(
    operation_summary='Получение текущего профиля пользователя',
    operation_description='Возвращает профиль текущего пользователя '
                          'в зависимости от его роли '
                          '(специалист, инвестор, основатель стартапа).',
    responses={
        200: openapi.Response(
            description='Успешно',
            schema=openapi.Schema(type=openapi.TYPE_OBJECT)
        ),
        401: 'Неавторизован',
        404: 'Профиль не найден'
    }
)

put_current_user_profile_doc = swagger_auto_schema(
    operation_summary='Обновление текущего профиля пользователя',
    operation_description='Обновляет профиль текущего пользователя. '
                          'Поля зависят от роли.',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        description='Тело запроса зависит от роли '
                    '(см. SpecialistProfileSerializer, '
                    'FounderProfileSerializer, InvestorProfileSerializer)',
    ),
    responses={
        200: openapi.Response(description='Успешно обновлено'),
        400: 'Ошибка валидации',
        401: 'Неавторизован',
        404: 'Профиль не найден'
    }
)

get_public_user_profile_doc = swagger_auto_schema(
    operation_summary='Просмотр чужого профиля по ID',
    operation_description='Возвращает профиль пользователя по ID. '
                          'Только для чтения. '
                          'В зависимости от роли — разная структура данных.',
    responses={
        200: openapi.Response(description='Успешно'),
        404: 'Профиль не найден'
    }
)
