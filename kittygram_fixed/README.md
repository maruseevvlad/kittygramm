# Kittygram — Кото-ивенты

Серверная часть модуля «Кото-ивенты» проекта Kittygram. Поддерживает
создание событий (встречи, выставки, прогулки), регистрацию участников,
комментирование, гибкие фильтры и пагинацию.

## Стек технологий

- Python 3.11
- Django 4.2 + Django REST Framework 3.14
- PostgreSQL 15 (с фолбэком на SQLite для локальной разработки)
- django-filter, drf-spectacular (Swagger UI / Redoc)
- Docker + docker-compose, Nginx, Gunicorn

## Быстрый старт (локально, SQLite)

```bash
git clone https://github.com/<ваш-логин>/kittygram_events.git
cd kittygram_events

python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# В .env установить USE_SQLITE=True (значение по умолчанию для разработки)

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

После запуска приложение доступно по адресу `http://127.0.0.1:8000/`.

## Запуск через Docker (PostgreSQL)

```bash
cp .env.example .env
# В .env выставить USE_SQLITE=False (или просто оставить как есть в .env.example)

docker compose up -d --build
docker compose exec web python manage.py createsuperuser
```

Приложение будет доступно через Nginx на `http://localhost/`.
Миграции выполняются автоматически при старте контейнера `web`.

## Документация API

- Swagger UI: `http://127.0.0.1:8000/api/schema/swagger-ui/`
- Redoc: `http://127.0.0.1:8000/api/schema/redoc/`
- OpenAPI-схема: `http://127.0.0.1:8000/api/schema/`

## Эндпоинты

| Метод | URL | Описание | Права |
|------|------|----------|------|
| POST | `/api/api-token-auth/` | Получить токен | Любой |
| GET | `/api/events/` | Список событий | Авторизованный |
| POST | `/api/events/` | Создать событие | Авторизованный |
| GET | `/api/events/{id}/` | Детали события | Авторизованный |
| PUT/PATCH | `/api/events/{id}/` | Редактировать | Организатор |
| DELETE | `/api/events/{id}/` | Удалить | Организатор |
| POST | `/api/events/{id}/join/` | Записаться | Авторизованный |
| DELETE | `/api/events/{id}/leave/` | Отменить запись | Авторизованный |
| GET | `/api/events/{id}/participants/` | Участники | Авторизованный |
| GET | `/api/events/{id}/comments/` | Комментарии | Авторизованный |
| POST | `/api/events/{id}/comments/` | Добавить комментарий | Только участник |

## Пример запроса (curl)

```bash
# Получить токен
curl -X POST http://127.0.0.1:8000/api/api-token-auth/ \
  -H "Content-Type: application/json" \
  -d '{"username":"VladMaruseev","password":"<пароль>"}'

# Создать событие
curl -X POST http://127.0.0.1:8000/api/events/ \
  -H "Authorization: Token <ваш-токен>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Выставка котиков в парке Горького",
    "description": "Ежегодная выставка пушистых красавцев",
    "location": "Москва, парк Горького",
    "start_date": "2027-06-01T12:00:00Z",
    "end_date":   "2027-06-01T18:00:00Z",
    "max_participants": 50
  }'
```

## Структура проекта

```
kittygram_events/
├── events/                # Приложение «Кото-ивенты»
│   ├── models.py          # Event, Registration, EventComment
│   ├── serializers.py
│   ├── views.py           # EventViewSet
│   ├── permissions.py     # IsOrganizer, IsCommentAuthor
│   ├── filters.py
│   ├── urls.py
│   └── admin.py
├── kittygram/             # Конфигурация проекта
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── Dockerfile
├── docker-compose.yml
├── nginx.conf
├── requirements.txt
├── .env.example
└── manage.py
```

## Автор

Марусеев Владислав Вадимович, группа ПИ2у/24б, ВШКМиС,
курсовая работа по дисциплине «Интеграция и управление приложениями
на удалённом сервере», 2026 г.
