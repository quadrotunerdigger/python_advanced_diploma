# Корпоративный сервис микроблогов (Twitter Clone)

Дипломный проект курса "Python Advanced" — полнофункциональный бэкенд для корпоративного сервиса микроблогов с REST API, Docker-контейнеризацией и веб-интерфейсом.

---

## Содержание

- [Описание проекта](#описание-проекта)
- [Возможности](#возможности)
- [Технологии](#технологии)
- [Быстрый старт](#быстрый-старт)
- [Создание пользователей](#создание-пользователей)
- [API документация](#api-документация)
- [Структура проекта](#структура-проекта)
- [Тестирование](#тестирование)

---

## Описание проекта

Корпоративный сервис микроблогов — это REST API приложение, позволяющее сотрудникам компании обмениваться короткими сообщениями (твитами), подписываться друг на друга, ставить лайки и прикреплять изображения к публикациям.

### Ключевые особенности

- **Полный REST API** с автоматической документацией (Swagger)
- **Асинхронная архитектура** на базе FastAPI и SQLAlchemy 2.0
- **Безопасность** — хеширование API-ключей с bcrypt
- **Docker Compose** для простого развёртывания в одну команду
- **Веб-интерфейс** для удобной работы через браузер
- **Медиафайлы** — загрузка и хранение изображений
- **Подписки и лайки** — полная социальная функциональность
- **Тесты** — 39 автотестов с покрытием 65%

---

## Возможности

### Для пользователей

- **Твиты**: Создание, просмотр и удаление коротких сообщений
- **Медиа**: Прикрепление изображений (PNG, JPEG, GIF, WebP)
- **Подписки**: Подписка/отписка от других пользователей
- **Лайки**: Постановка и снятие лайков на твиты
- **Лента**: Просмотр твитов от пользователей в подписках (сортировка по популярности)
- **Профили**: Просмотр профилей с подписчиками и подписками

### Для администраторов

- **Регистрация пользователей** через API или напрямую в БД
- **Swagger UI** для тестирования и мониторинга
- **Docker** для простого развёртывания
- **Персистентное хранилище** данных (PostgreSQL + volumes)

---

## Технологии

| Категория | Технологии |
|-----------|------------|
| **Backend** | Python 3.11+, FastAPI, Uvicorn |
| **База данных** | PostgreSQL 15, SQLAlchemy 2.0 (async) |
| **Валидация** | Pydantic 2.0, Pydantic Settings |
| **Безопасность** | bcrypt (хеширование паролей) |
| **Файлы** | aiofiles (асинхронная работа) |
| **Тестирование** | pytest, pytest-asyncio, pytest-cov, httpx |
| **Линтинг** | flake8, black, isort, mypy |
| **Контейнеризация** | Docker, Docker Compose |
| **Веб-сервер** | Nginx (reverse proxy, статика) |

---

## Быстрый старт

### Требования

- Docker 20.10+
- Docker Compose 2.0+
- Git

### Установка и запуск

```bash
# 1. Клонировать репозиторий
git clone https://gitlab.skillbox.ru/iurii_shmyrev/python_advanced_diploma
cd python_advanced_diploma

# 2. Запустить приложение
docker compose up -d --build

# 3. Проверка работоспособности контейнеров
docker compose ps

# Все контейнеры должны быть в статусе "healthy"

# Ожидаемый результат:
# NAME                IMAGE              STATUS
# microblog_nginx     ...                Up (healthy)
# microblog_app       ...                Up (healthy)
# microblog_db        ...                Up (healthy)

# 4. Включить логирование 
docker compose logs -f app

```

### Доступ к приложению

- **Веб-интерфейс**: http://localhost
- **Swagger API**: http://localhost/api/docs

---

## Создание пользователей

Проект поддерживает **два способа создания пользователей** для максимальной гибкости демонстрации:

### Способ 1: Через API (безопасно, с хешированием)

**Когда использовать**: Для демонстрации правильной архитектуры API, безопасности

**Как создать**:

```bash
curl -X POST http://localhost/api/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Иван Петров", "api_key": "my_secret_key"}'
```

**Что происходит**:
- API-ключ хешируется с помощью bcrypt → `$2b$12$...`
- Пользователь сохраняется в БД с защищённым паролем

**Где работает**:
- Swagger UI (`http://localhost/api/docs`)
- curl и другие HTTP-клиенты
- **НЕ работает** в веб-интерфейсе (браузер)

**Почему не работает в браузере**: Фронтенд ожидает простой ключ для демонстрации, а API создаёт хешированный.

---

### Способ 2: Через SQL (для демонстрации фронтенда)

**Когда использовать**: Для работы через веб-интерфейс в браузере

**Как создать**:

```bash
# Подключиться к PostgreSQL
docker compose exec db psql -U postgres -d microblog
```

В консоли PostgreSQL выполните:

```sql
-- Очистить старые данные (опционально)
TRUNCATE users, tweets, media, likes, followers CASCADE;

-- Создать пользователей с простыми ключами
INSERT INTO users (id, name, api_key) VALUES 
(1, 'Иван Петров', 'test'),
(2, 'Мария Сидорова', 'user2'),
(3, 'Алексей Козлов', 'user3');

-- Сбросить счётчик ID
SELECT setval('users_id_seq', 3);

-- Выйти
\q
```

**Что происходит**:
- API-ключи сохраняются как есть (без хеширования)
- Пользователи готовы к работе везде

**Где работает**:
- Веб-интерфейс (браузер) — `http://localhost`
- Swagger UI
- curl

---

### Сравнительная таблица

| Способ | Безопасность | Браузер | Swagger | curl | Для демонстрации |
|--------|--------------|---------|---------|------|------------------|
| **POST /api/users** | 🔒 Высокая (bcrypt) | ❌ | ✅ | ✅ | API архитектуры |
| **SQL INSERT** | ⚠️ Низкая (plain text) | ✅ | ✅ | ✅ | Фронтенда |


---

## API документация

### Основные endpoints

| Метод | Endpoint | Описание |
|-------|----------|----------|
| `POST` | `/api/users` | Создать пользователя (с хешированием bcrypt) |
| `POST` | `/api/tweets` | Создать твит |
| `GET` | `/api/tweets` | Получить ленту твитов |
| `DELETE` | `/api/tweets/{id}` | Удалить твит |
| `POST` | `/api/medias` | Загрузить изображение |
| `POST` | `/api/tweets/{id}/likes` | Поставить лайк |
| `DELETE` | `/api/tweets/{id}/likes` | Убрать лайк |
| `POST` | `/api/users/{id}/follow` | Подписаться |
| `DELETE` | `/api/users/{id}/follow` | Отписаться |
| `GET` | `/api/users/me` | Мой профиль |
| `GET` | `/api/users/{id}` | Профиль пользователя |

### Аутентификация

Все защищённые endpoints требуют заголовок `api-key`:

```bash
curl -X GET "http://localhost/api/users/me" \
     -H "api-key: test"
```

**Swagger UI**: Нажмите кнопку 🔒 **Authorize** и введите свой API-ключ.

---

## Примеры использования

### 1. Создание пользователя через API

```bash
curl -X POST http://localhost/api/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Новый Пользователь", "api_key": "secure123"}'

# Ответ:
# {"result": true, "id": 4, "name": "Новый Пользователь"}
```

### 2. Создание твита

```bash
curl -X POST http://localhost/api/tweets \
  -H "api-key: test" \
  -H "Content-Type: application/json" \
  -d '{"tweet_data": "Привет, мир! 🚀"}'

# Ответ:
# {"result": true, "tweet_id": 1}
```

### 3. Загрузка изображения

```bash
curl -X POST http://localhost/api/medias \
  -H "api-key: test" \
  -F "file=@image.png"

# Ответ:
# {"result": true, "media_id": 1}
```

### 4. Подписка на пользователя

```bash
curl -X POST http://localhost/api/users/2/follow \
  -H "api-key: test"

# Ответ:
# {"result": true}
```

### 5. Получение ленты

```bash
curl http://localhost/api/tweets -H "api-key: test"

# Ответ: JSON со списком твитов от подписок
```

---

## Структура проекта

```
python_advanced_diploma/
├── app/                      # Основное приложение
│   ├── api/                  # API endpoints
│   │   ├── tweets.py         # Твиты (POST, GET, DELETE)
│   │   ├── users.py          # Пользователи (GET, POST)
│   │   ├── media.py          # Медиафайлы (POST)
│   │   ├── likes.py          # Лайки (POST, DELETE)
│   │   ├── follows.py        # Подписки (POST, DELETE)
│   │   └── deps.py           # Зависимости (auth)
│   ├── models/               # SQLAlchemy модели
│   │   ├── user.py           # User + followers_table
│   │   ├── tweet.py          # Tweet + likes_table
│   │   └── media.py          # Media
│   ├── schemas/              # Pydantic схемы
│   ├── services/             # Бизнес-логика
│   ├── db/                   # База данных
│   │   └── database.py       # Подключение, сессии
│   └── utils/                # Утилиты, исключения
├── tests/                    # 39 автотестов
├── nginx/                    # Конфигурация Nginx
├── static/                   # Фронтенд (HTML, CSS, JS)
├── docker-compose.yml        # Docker Compose конфигурация
├── Dockerfile                # Образ приложения
└── requirements.txt          # Python зависимости
```

---

## Тестирование

### Запуск тестов

```bash
# Все тесты
docker compose exec app pytest -v

# С покрытием
docker compose exec app pytest --cov=app --cov-report=html

# Конкретный файл
docker compose exec app pytest tests/test_tweets.py -v
```

### Результаты

- ✅ **39 тестов** — все проходят
- ✅ **Flake8** — 0 ошибок
- ✅ **Покрытие кода** — 65%
- ⚠️ **Mypy** — 14 предупреждений (типизация опциональна)

### Линтинг и форматирование

```bash
# Форматирование кода
docker compose exec app black app tests
docker compose exec app isort app tests

# Проверка стиля
docker compose exec app flake8 app

# Проверка типов (опционально)
docker compose exec app mypy app
```

---

## База данных

### Подключение к PostgreSQL

```bash
# Консоль PostgreSQL
docker compose exec db psql -U postgres -d microblog
```

### Полезные SQL команды

```sql
-- Список всех пользователей
SELECT id, name, api_key FROM users;

-- Список твитов с авторами
SELECT t.id, t.content, u.name 
FROM tweets t 
JOIN users u ON t.author_id = u.id;

-- Подписки
SELECT 
  u1.name AS follower,
  u2.name AS following
FROM followers f
JOIN users u1 ON f.follower_id = u1.id
JOIN users u2 ON f.followed_id = u2.id;

-- Выйти
\q
```

### Сброс данных

```bash
# Полный сброс (удаление volumes)
docker compose down -v

# Перезапуск
docker compose up -d

# Создать пользователей заново (см. раздел "Создание пользователей")
```

---

## Архитектура

### Docker Compose сервисы

```
┌────────────────┐      ┌────────────────┐      ┌────────────────┐
│     nginx      │──────>│      app       │──────>│       db       │
│   (port 80)    │      │   (port 8000)  │      │   (port 5432)  │
└────────────────┘      └────────────────┘      └────────────────┘
       │                        │                        │
   Статика +              FastAPI +              PostgreSQL 15
   Прокси API             Uvicorn                + asyncpg
```

### Volumes (персистентность)

- `microblog_postgres_data` — база данных
- `microblog_media_data` — загруженные изображения

---

## Управление проектом

### Просмотр логов

```bash
# Логи всех сервисов
docker compose logs -f

# Логи конкретного сервиса
docker compose logs -f app
```

### Остановка

```bash
# Остановить без удаления данных
docker compose down

# Остановить с удалением данных
docker compose down -v
```

### Перезапуск

```bash
# Перезапуск всех сервисов
docker compose restart

# Перезапуск конкретного сервиса
docker compose restart app
```

---

## Решение проблем

### Контейнеры не запускаются

```bash
# Пересобрать образы
docker compose down
docker compose up -d --build
```

### Порт 80 занят

```bash
# Изменить порт в docker-compose.yml
# ports:
#   - "8080:80"  # Вместо 80:80

# Перезапустить
docker compose up -d
```

### База данных не отвечает

```bash
# Проверить здоровье
docker compose ps

# Посмотреть логи
docker compose logs db
```

---

## Требования проекта (согласно ТЗ)

### Функциональные требования (8/8)

1. ✅ Добавление твита
2. ✅ Удаление твита
3. ✅ Подписка на пользователя
4. ✅ Отписка от пользователя
5. ✅ Лайк на твит
6. ✅ Снятие лайка
7. ✅ Лента твитов (сортировка по популярности)
8. ✅ Твиты с картинками

### Нефункциональные требования (3/3) ✅

1. ✅ Развёртывание через `docker-compose up -d`
2. ✅ Данные сохраняются между запусками (PostgreSQL + volumes)
3. ✅ Swagger документация доступна при запуске

### Технические требования

- ✅ PostgreSQL
- ✅ Swagger документация
- ✅ Docker Compose
- ✅ Unit-тесты (39 passed)
- ✅ Линтер (flake8: 0 ошибок)
- ✅ README с инструкциями

---

## Дополнительные возможности

Реализованные фичи, выходящие за рамки ТЗ:

- **Endpoint создания пользователей** (`POST /api/users`)
- **Безопасность** (bcrypt хеширование паролей)
- **Гибридная аутентификация** (поддержка plain text + bcrypt)
- **Асинхронная архитектура** (FastAPI + SQLAlchemy async)
- **Healthchecks** для всех сервисов

---

## Поддержка

1. [CHECKLIST.md](CHECKLIST.md) — примеры всех запросов
2. [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) — архитектура проекта
3. [Swagger](http://localhost/api/docs) — документация
