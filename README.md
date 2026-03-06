# Kittygram — Кото-ивенты (встречи)

Расширение проекта Kittygram: REST API для организации кото-событий (выставки, прогулки, встречи котовладельцев).

## Технологии

- Python 3.11
- Django 4.2
- Django REST Framework 3.14
- django-filter
- drf-spectacular (Swagger / Redoc)
- SQLite (разработка) / PostgreSQL (Docker)
- Docker + Docker Compose
- Nginx + Gunicorn

## Быстрый старт (локально)

```bash
# 1. Клонировать репозиторий
git clone <URL_РЕПОЗИТОРИЯ>
cd kittygram_events

# 2. Создать и активировать виртуальное окружение
python -m venv venv
source venv/bin/activate    # Linux/Mac
# venv\Scripts\activate     # Windows

# 3. Установить зависимости
pip install -r requirements.txt

# 4. Настроить переменные окружения
cp .env.example .env

# 5. Применить миграции
python manage.py migrate

# 6. Создать суперпользователя
python manage.py createsuperuser

# 7. Запустить сервер
python manage.py runserver
```

Сервер будет доступен: http://127.0.0.1:8000/

## Документация API

После запуска сервера:

| Документация | URL |
|---|---|
| Swagger UI | http://127.0.0.1:8000/api/schema/swagger-ui/ |
| Redoc | http://127.0.0.1:8000/api/schema/redoc/ |
| OpenAPI Schema | http://127.0.0.1:8000/api/schema/ |

## Получение токена

```bash
# Создать токен
curl -X POST http://127.0.0.1:8000/api/api-token-auth/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your_password"}'

# Ответ: {"token": "abc123..."}
```

## Эндпоинты API

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/events/` | Список событий (фильтры, пагинация) |
| POST | `/api/events/` | Создать событие |
| GET | `/api/events/{id}/` | Детали события |
| PUT/PATCH | `/api/events/{id}/` | Редактировать (только организатор) |
| DELETE | `/api/events/{id}/` | Удалить (только организатор) |
| POST | `/api/events/{id}/join/` | Записаться на событие |
| DELETE | `/api/events/{id}/leave/` | Отменить запись |
| GET | `/api/events/{id}/participants/` | Список участников |
| GET | `/api/events/{id}/comments/` | Комментарии к событию |
| POST | `/api/events/{id}/comments/` | Добавить комментарий |

## Примеры запросов

### Создать событие
```bash
curl -X POST http://127.0.0.1:8000/api/events/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Выставка котиков в парке Горького",
    "description": "Ежегодная выставка пушистых красавцев",
    "location": "Москва, парк Горького",
    "start_date": "2025-04-01T12:00:00Z",
    "end_date": "2025-04-01T18:00:00Z",
    "max_participants": 50
  }'
```

### Записаться на событие
```bash
curl -X POST http://127.0.0.1:8000/api/events/1/join/ \
  -H "Authorization: Token YOUR_TOKEN"
```

### Список с фильтрами
```bash
curl "http://127.0.0.1:8000/api/events/?location=Москва&limit=5" \
  -H "Authorization: Token YOUR_TOKEN"
```

## Фильтрация и поиск

| Параметр | Описание | Пример |
|----------|----------|--------|
| `location` | По месту (содержит) | `?location=Москва` |
| `start_date_after` | Начало от даты | `?start_date_after=2025-04-01` |
| `start_date_before` | Начало до даты | `?start_date_before=2025-05-01` |
| `search` | Поиск по названию и описанию | `?search=выставка` |
| `limit` | Количество на странице | `?limit=10` |
| `offset` | Смещение | `?offset=20` |

## Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|-------------|
| `SECRET_KEY` | Секретный ключ Django | dev-ключ |
| `DEBUG` | Режим отладки | `True` |
| `ALLOWED_HOSTS` | Разрешённые хосты | `localhost,127.0.0.1` |

## Docker

```bash
# Запуск
docker compose up -d --build

# Миграции
docker compose exec web python manage.py migrate

# Суперпользователь
docker compose exec web python manage.py createsuperuser

# Сбор статики
docker compose exec web python manage.py collectstatic --no-input
```
