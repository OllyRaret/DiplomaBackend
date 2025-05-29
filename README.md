# 🔧 Backend платформы для поиска специалистов и инвесторов для стартапов

[![Run Postman Collections](https://github.com/OllyRaret/DiplomaBackend/actions/workflows/postman-tests.yml/badge.svg)](https://github.com/OllyRaret/DiplomaBackend/actions/workflows/postman-tests.yml)
[![Deploy Django Backend](https://github.com/OllyRaret/DiplomaBackend/actions/workflows/deploy.yml/badge.svg)](https://github.com/OllyRaret/DiplomaBackend/actions/workflows/deploy.yml)

Этот репозиторий содержит backend-часть веб-платформы, предназначенной для связи специалистов, инвесторов и стартаперов. Разработка выполнена с использованием Django и Django REST Framework.

🌐 Демо-домен: [https://prostarter.publicvm.com/](https://prostarter.publicvm.com/)

---

## 🖥️ Фронтенд

Frontend-часть платформы реализована в отдельном репозитории:

👉 [https://github.com/alenanish/GraduationThesis](https://github.com/alenanish/GraduationThesis)

---

## 📦 Функциональность

* Регистрация и авторизация пользователей (специалист, стартапер, инвестор)
* Профили пользователей с возможностью редактирования
* Создание и управление стартапами
* Поиск специалистов и стартапов по фильтрам
* Система избранного
* Приглашения специалистов в стартапы
* Встроенная система сообщений (чат)
* Автоматическое создание профилей по ролям
* Документация API с помощью Swagger (drf-yasg)

## 🚀 Стек технологий

* Python 3.12
* Django 5.2
* Django REST Framework
* PostgreSQL
* Djoser (регистрация и JWT-аутентификация)
* Gunicorn + Nginx (деплой)
* Docker + GitHub Actions (CI/CD)

## ⚙️ Установка и запуск

### 1. Клонируйте репозиторий

```bash
git clone https://github.com/your-username/your-backend-repo.git
cd your-backend-repo
```

### 2. Создайте и активируйте виртуальное окружение

```bash
python3 -m venv .venv
source .venv/bin/activate
```

(Для Windows: `.\.venv\Scripts\activate`)

### 3. Установите зависимости

```bash
pip install -r requirements.txt
```

Если возникает ошибка с `psycopg2`, установите:

```bash
sudo apt install libpq-dev
```

### 4. Примените миграции и создайте суперпользователя

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 5. Запустите сервер

```bash
python manage.py runserver
```

## 🧪 Документация API

После запуска перейдите на:

```
http://localhost:8000/redoc/
```

Или в продакшне:
[https://prostarter.publicvm.com/redoc/](https://prostarter.publicvm.com/redoc/)

Документация доступна благодаря \[drf-yasg].

## 📄 Переменные окружения

Создайте файл `.env` и укажите:

```env
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=127.0.0.1,localhost
```

## 📦 Docker

Поддерживается деплой с использованием Docker и CI/CD.

## 🤝 Авторы

Проект создан в рамках дипломной работы

👤 **Лакеева Ольга Александровна** (бэкенд + деплой)

👤 **Обрезкова Алина Андреевна** (дизайн + тестирование)

👤 **Нишнючкина Алёна Алексеевна** (фронтенд)

📚 НИУ ВШЭ, направление "Программная инженерия"
