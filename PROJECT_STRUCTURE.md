# Структура проекта: Корпоративный сервис микроблогов

## Обзор

Проект построен на архитектуре **трёхслойного приложения** с разделением на представление (Nginx + статика), бизнес-логику (FastAPI) и данные (PostgreSQL).

---

## Корневая структура

```
python_advanced_diploma/
│
├── docker-compose.yml          # Оркестрация: nginx, app, postgres
├── Dockerfile                   # Образ Python приложения (multi-stage)
├── requirements.txt             # Prod зависимости (FastAPI, SQLAlchemy, bcrypt)
├── requirements-dev.txt         # Dev зависимости (pytest, flake8, mypy)
│
├── .gitignore                   # Игнорируемые файлы (venv, __pycache__, .env)
├── README.md                    # Основная документация
├── CHECKLIST.md                 # Чек-лист проверки ТЗ
├── PROJECT_STRUCTURE.md         # Этот файл
│
├── pyproject.toml               # Конфигурация линтеров (black, isort, pytest)
├── setup.cfg                    # Дополнительная конфигурация (flake8, mypy)
│
├── app/                         # Основное приложение
├── tests/                       # Автотесты (pytest)
├── migrations/                  # Alembic миграции БД
├── nginx/                       # Конфигурация Nginx
└── static/                      # Фронтенд (HTML, CSS, JS)
```

---

## Детальная структура приложения

### app/ — Основное приложение

```
app/
│
├── __init__.py                     # Фабрика приложения (create_app)
├── config.py                       # Настройки (Pydantic Settings)
├── main.py                         # Точка входа (для uvicorn)
│
├── api/                            # REST API endpoints
│   ├── __init__.py
│   ├── deps.py                     # Зависимости (get_current_user, auth)
│   ├── tweets.py                   # POST/GET/DELETE /api/tweets
│   ├── media.py                    # POST /api/medias
│   ├── users.py                    # GET /api/users/me, /api/users/{id}, POST /api/users
│   ├── likes.py                    # POST/DELETE /api/tweets/{id}/likes
│   └── follows.py                  # POST/DELETE /api/users/{id}/follow
│
├── models/                         # SQLAlchemy модели (БД)
│   ├── __init__.py
│   ├── base.py                     # Базовый класс (DeclarativeBase)
│   ├── user.py                     # User + followers_table (many-to-many)
│   ├── tweet.py                    # Tweet + likes_table (many-to-many)
│   ├── media.py                    # Media (связь с Tweet)
│   ├── like.py                     # Вспомогательные функции для лайков
│   └── follower.py                 # Вспомогательные функции для подписок
│
├── schemas/                        # 📋 Pydantic схемы (валидация)
│   ├── __init__.py
│   ├── base.py                     # SuccessResponse, ErrorResponse
│   ├── user.py                     # UserProfile, UserCreate, UserBase
│   ├── tweet.py                    # TweetCreate, TweetResponse, TweetFeed
│   └── media.py                    # MediaResponse
│
├── services/                       # Бизнес-логика (Service Layer)
│   ├── __init__.py
│   ├── user_service.py             # Работа с пользователями (auth, follow/unfollow)
│   ├── tweet_service.py            # Работа с твитами (CRUD, likes)
│   ├── media_service.py            # Работа с медиафайлами (upload, delete)
│   └── feed_service.py             # Формирование ленты твитов
│
├── db/                             # Работа с БД
│   ├── __init__.py
│   └── database.py                 # Подключение (AsyncEngine, sessions)
│
└── utils/                          # 🛠 Утилиты
    ├── __init__.py
    └── exceptions.py               # Кастомные исключения (HTTP exceptions)
```

---

## Модели базы данных

### ER-диаграмма

```
┌─────────────────┐       ┌──────────────────┐       ┌────────────────┐
│   User          │       │   Tweet          │       │   Media        │
├─────────────────┤       ├──────────────────┤       ├────────────────┤
│ id (PK)         │──┐    │ id (PK)          │    ┌──│ id (PK)        │
│ name            │  │    │ content (text)   │    │  │ filename       │
│ api_key (UQ)    │  └───>│ author_id (FK)   │    │  │ tweet_id (FK)  │
└─────────────────┘       │ created_at       │<───┘  └────────────────┘
      │                   └──────────────────┘
      │                         │
      │  ┌──────────────────────┘
      │  │
      ▼  ▼
┌─────────────────┐       ┌──────────────────┐
│ followers       │       │    likes         │
│ (many-to-many)  │       │  (many-to-many)  │
├─────────────────┤       ├──────────────────┤
│ follower_id(PK,FK)      │ user_id (PK, FK) │
│ followed_id(PK,FK)      │ tweet_id(PK, FK) │
└─────────────────┘       └──────────────────┘
```

### Таблицы PostgreSQL

| Таблица | Описание | Ключевые поля |
|---------|----------|---------------|
| `users` | Пользователи | id, name, api_key (хешированный) |
| `tweets` | Твиты | id, content, author_id, created_at |
| `media` | Медиафайлы | id, filename, tweet_id |
| `followers` | Подписки (M2M) | follower_id, followed_id |
| `likes` | Лайки (M2M) | user_id, tweet_id |

---

## API Endpoints

### Полный список

| Метод | Endpoint | Описание | Аутентификация |
|-------|----------|----------|----------------|
| `POST` | `/api/users` | Создать пользователя | ❌ Публичный |
| `GET` | `/api/users/me` | Мой профиль | ✅ Обязательна |
| `GET` | `/api/users/{id}` | Профиль пользователя | ❌ Публичный |
| `POST` | `/api/tweets` | Создать твит | ✅ Обязательна |
| `GET` | `/api/tweets` | Лента твитов | ✅ Обязательна |
| `DELETE` | `/api/tweets/{id}` | Удалить твит | ✅ Обязательна |
| `POST` | `/api/medias` | Загрузить изображение | ✅ Обязательна |
| `POST` | `/api/tweets/{id}/likes` | Поставить лайк | ✅ Обязательна |
| `DELETE` | `/api/tweets/{id}/likes` | Убрать лайк | ✅ Обязательна |
| `POST` | `/api/users/{id}/follow` | Подписаться | ✅ Обязательна |
| `DELETE` | `/api/users/{id}/follow` | Отписаться | ✅ Обязательна |

### Структура ответов

**Успешный ответ**:
```json
{
  "result": true,
  "tweet_id": 1
}
```

**Ошибка**:
```json
{
  "detail": {
    "result": false,
    "error_type": "UserNotFound",
    "error_message": "Пользователь с id=99 не найден"
  }
}
```

---

## Docker Compose архитектура

### Сервисы

```
┌────────────────┐      ┌────────────────┐      ┌────────────────┐
│     nginx      │─────>│      app       │─────>│       db       │
│   (port 80)    │      │   (port 8000)  │      │   (port 5432)  │
└────────────────┘      └────────────────┘      └────────────────┘
       │                        │                        │
       │                        │                        │
   Статика +              FastAPI +              PostgreSQL 15
   Прокси API             Uvicorn                + asyncpg
```

### Volumes (персистентность)

| Volume | Назначение | Путь в контейнере |
|--------|-----------|-------------------|
| `microblog_postgres_data` | База данных | `/var/lib/postgresql/data` |
| `microblog_media_data` | Загруженные изображения | `/app/static/media` |

---

## Тесты

### Структура тестов

```
tests/
├── __init__.py
├── conftest.py                     # Фикстуры (async_engine, client, test_user)
├── test_tweets.py                  # Тесты твитов (17 тестов)
├── test_users.py                   # Тесты пользователей (6 тестов)
├── test_media.py                   # Тесты медиафайлов (5 тестов)
├── test_likes.py                   # Тесты лайков (8 тестов)
└── test_follows.py                 # Тесты подписок (10 тестов)
```

### Статистика

- ✅ **39 тестов** — все проходят
- ✅ **Покрытие** — 65%
- ✅ **База** — SQLite in-memory (быстро)

---

## Миграции

### Alembic структура

```
migrations/
├── env.py                          # Конфигурация Alembic
├── script.py.mako                  # Шаблон миграций
├── README.md                       # Инструкция по использованию
└── versions/
    └── 001_initial.py              # Начальная миграция (создание таблиц)
```

### Команды

```bash
# Применить все миграции
alembic upgrade head

# Создать новую миграцию
alembic revision --autogenerate -m "описание"

# Откатить последнюю
alembic downgrade -1
```

---

## Nginx конфигурация

### Роли Nginx

```
┌─────────────────────────────────────────┐
│            nginx:80                     │
├─────────────────────────────────────────┤
│                                         │
│  GET /                                  │
│  └─> Статика: /usr/share/nginx/html     │
│                                         │
│  GET /api/*                             │
│  └─> Прокси: http://app:8000            │
│                                         │
│  GET /media/*                           │
│  └─> Статика: /app/static/media         │
│                                         │
└─────────────────────────────────────────┘
```

### Файлы

```
nginx/
├── Dockerfile                      # Образ Nginx
└── nginx.conf                      # Конфигурация (прокси + статика)
```

---

## Фронтенд

```
static/
├── index.html                      # Главная страница
├── favicon.ico
├── css/
│   └── *.css                       # Стили
├── js/
│   └── *.js                        # JavaScript
└── media/                          # Загруженные изображения
    └── .gitkeep
```

**Примечание**: Папка `static/` содержит готовый фронтенд и не включена в репозиторий из-за размера.

---

## Зависимости

### Production (requirements.txt)

| Пакет | Версия | Назначение |
|-------|--------|------------|
| fastapi | 0.109.2 | Веб-фреймворк |
| uvicorn | 0.27.1 | ASGI сервер |
| sqlalchemy | 2.0.25 | ORM (async) |
| asyncpg | 0.29.0 | PostgreSQL драйвер |
| pydantic | 2.6.1 | Валидация |
| bcrypt | 4.1.2 | Хеширование паролей |
| alembic | 1.13.1 | Миграции БД |
| aiofiles | 23.2.1 | Асинхронная работа с файлами |

### Development (requirements-dev.txt)

| Пакет | Назначение |
|-------|------------|
| pytest | Тестирование |
| pytest-asyncio | Асинхронные тесты |
| httpx | HTTP клиент для тестов |
| flake8 | Линтинг |
| black | Форматирование |
| mypy | Проверка типов |

---

## Потоки данных

### Создание твита

```
1. User → POST /api/tweets + {"tweet_data": "Hello"}
2. Nginx → Proxy → FastAPI (app:8000)
3. FastAPI → Валидация (Pydantic)
4. FastAPI → TweetService.create_tweet()
5. TweetService → SQLAlchemy → PostgreSQL
6. PostgreSQL → Вставка записи в tweets
7. FastAPI → Ответ {"result": true, "tweet_id": 1}
```

### Загрузка изображения

```
1. User → POST /api/medias + файл
2. Nginx → Proxy → FastAPI
3. FastAPI → MediaService.upload_file()
4. MediaService → Сохранение в /app/static/media/{uuid}.png
5. MediaService → Запись в БД (media)
6. FastAPI → Ответ {"result": true, "media_id": 1}
7. User → GET /media/{uuid}.png
8. Nginx → Раздача файла из /app/static/media
```

---

## Безопасность

### Аутентификация

```
┌──────────────────────────────────────────┐
│  Гибридная система                       │
├──────────────────────────────────────────┤
│                                          │
│  1. Bcrypt (POST /api/users)             │
│     api_key → bcrypt.hash() → $2b$...    │
│     Работает: API, Swagger               │
│     Не работает: Фронтенд                │
│                                          │
│  2. Plain text (SQL INSERT)              │
│     api_key → "test" (как есть)          │
│     Работает: Везде (API, фронтенд)      │
│                                          │
└──────────────────────────────────────────┘
```

### Проверка доступа

```python
# deps.py
async def get_current_user(api_key: str) -> User:
    user = await UserService.get_user_by_api_key(api_key)
    if not user:
        raise InvalidApiKeyException()
    return user
```

---

## Переменные окружения

### Файл .env

```bash
# База данных
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/microblog
DATABASE_ECHO=false

# Приложение
DEBUG=false

# Загрузка файлов
MAX_FILE_SIZE=5242880  # 5 MB
ALLOWED_EXTENSIONS_STR=jpg,jpeg,png,gif,webp
```

---

## Команды для разработки

### Docker

```bash
# Запуск
docker compose up -d

# Остановка
docker compose down

# Полный сброс
docker compose down -v

# Логи
docker compose logs -f app

# Зайти в контейнер
docker compose exec app bash
```

### База данных

```bash
# Подключиться к PostgreSQL
docker compose exec db psql -U postgres -d microblog

# Сделать дамп
docker compose exec db pg_dump -U postgres microblog > backup.sql
```

### Тестирование

```bash
# Все тесты
docker compose exec app pytest -v

# С покрытием
docker compose exec app pytest --cov=app --cov-report=html
```

---

## Производительность

### Оптимизации

- ✅ **Async/await** — асинхронная обработка запросов
- ✅ **Connection pooling** — пул соединений с PostgreSQL
- ✅ **Eager loading** — `selectinload()` для связей
- ✅ **Nginx caching** — кеширование статики (1 год)
- ✅ **Gzip compression** — сжатие ответов
- ✅ **Multi-stage build** — оптимизированный Docker образ

---