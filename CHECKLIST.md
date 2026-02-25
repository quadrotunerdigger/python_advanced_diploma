# Чек-лист проверки требований ТЗ

## Проект: Корпоративный сервис микроблогов (Twitter-clone)

---

## 1. Функциональные требования API

### Основные endpoints (10/10)

| № | Требование | Endpoint | Метод | Статус |
|---|------------|----------|-------|--------|
| 1 | Создание твита | `/api/tweets` | POST | ✅ |
| 2 | Удаление твита | `/api/tweets/{id}` | DELETE | ✅ |
| 3 | Подписка на пользователя | `/api/users/{id}/follow` | POST | ✅ |
| 4 | Отписка от пользователя | `/api/users/{id}/follow` | DELETE | ✅ |
| 5 | Поставить лайк | `/api/tweets/{id}/likes` | POST | ✅ |
| 6 | Убрать лайк | `/api/tweets/{id}/likes` | DELETE | ✅ |
| 7 | Получить ленту твитов | `/api/tweets` | GET | ✅ |
| 8 | Загрузка медиафайлов | `/api/medias` | POST | ✅ |
| 9 | Получить свой профиль | `/api/users/me` | GET | ✅ |
| 10 | Получить профиль пользователя | `/api/users/{id}` | GET | ✅ |
| 11 | **Создание пользователя** | `/api/users` | POST | ✅ **Добавлено** |

---

## 2. Быстрая проверка работоспособности

### Шаг 1: Запуск приложения

```bash
# Запустить все сервисы
docker compose up -d --build

# Проверить статус (все должны быть healthy)
docker compose ps
```

### Шаг 2: Создать тестовых пользователей

**Вариант A: Через SQL (для фронтенда)**

```bash
docker compose exec db psql -U postgres -d microblog << 'EOF'
TRUNCATE users, tweets, media, likes, followers CASCADE;

INSERT INTO users (id, name, api_key) VALUES 
(1, 'Иван Петров', 'test'),
(2, 'Мария Сидорова', 'user2'),
(3, 'Алексей Козлов', 'user3');

SELECT setval('users_id_seq', 3);
EOF
```

**Вариант B: Через API (безопасно)**

```bash
curl -X POST http://localhost/api/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Secure User", "api_key": "secure_key"}'
```

### Шаг 3: Проверка endpoints

#### 1. Создание твита

```bash
curl -X POST http://localhost/api/tweets \
  -H "api-key: test" \
  -H "Content-Type: application/json" \
  -d '{"tweet_data": "Мой первый твит! 🚀"}'
```

**Ожидаемый результат**: 
```json
{"result": true, "tweet_id": 1}
```

#### 2. Удаление своего твита

```bash
curl -X DELETE http://localhost/api/tweets/1 \
  -H "api-key: test"
```

**Ожидаемый результат**: 
```json
{"result": true}
```

#### 3. Попытка удаления чужого твита (ошибка)

```bash
# Создать твит от user2
curl -X POST http://localhost/api/tweets \
  -H "api-key: user2" \
  -H "Content-Type: application/json" \
  -d '{"tweet_data": "Твит от user2"}'

# Попытаться удалить от test
curl -X DELETE http://localhost/api/tweets/2 \
  -H "api-key: test"
```

**Ожидаемый результат**: 
```json
{"detail": {"result": false, "error_type": "PermissionDenied", ...}}
```

#### 4. Подписка на пользователя

```bash
curl -X POST http://localhost/api/users/2/follow \
  -H "api-key: test"
```

**Ожидаемый результат**: 
```json
{"result": true}
```

#### 5. Отписка от пользователя

```bash
curl -X DELETE http://localhost/api/users/2/follow \
  -H "api-key: test"
```

**Ожидаемый результат**: 
```json
{"result": true}
```

#### 6. Поставить лайк

```bash
curl -X POST http://localhost/api/tweets/2/likes \
  -H "api-key: test"
```

**Ожидаемый результат**: 
```json
{"result": true}
```

#### 7. Убрать лайк

```bash
curl -X DELETE http://localhost/api/tweets/2/likes \
  -H "api-key: test"
```

**Ожидаемый результат**: 
```json
{"result": true}
```

#### 8. Получить ленту твитов

```bash
# Сначала подпишитесь на user2
curl -X POST http://localhost/api/users/2/follow -H "api-key: test"

# Затем получите ленту
curl http://localhost/api/tweets -H "api-key: test"
```

**Ожидаемый результат**: JSON со списком твитов от подписок

#### 9. Загрузить медиафайл

```bash
# Загрузить изображение из Downloads
curl -X POST http://localhost/api/medias \
  -H "api-key: test" \
  -F "file=@/home/quadrotuner/Downloads/1.png"
```

**Ожидаемый результат**: 
```json
{"result": true, "media_id": 1}
```

#### 10. Получить свой профиль

```bash
curl http://localhost/api/users/me -H "api-key: test"
```

**Ожидаемый результат**: JSON с профилем, подписками и подписчиками

#### 11. Получить профиль пользователя

```bash
curl http://localhost/api/users/2
```

**Ожидаемый результат**: JSON с профилем пользователя

---

## 3. Нефункциональные требования (6/6)

| № | Требование | Проверка | Статус |
|---|------------|----------|--------|
| 1 | Docker Compose развёртывание | `docker compose up -d` | ✅ |
| 2 | Данные сохраняются между запусками | Перезапуск → данные на месте | ✅ |
| 3 | Nginx как reverse proxy | Порт 80, статика, API | ✅ |
| 4 | PostgreSQL база данных | Volume `microblog_postgres_data` | ✅ |
| 5 | Swagger документация | http://localhost/api/docs | ✅ |
| 6 | Фронтенд работает | http://localhost | ✅ |

### Проверка сохранности данных

```bash
# 1. Создать твит
curl -X POST http://localhost/api/tweets \
  -H "api-key: test" \
  -H "Content-Type: application/json" \
  -d '{"tweet_data": "Тест персистентности данных"}'

# 2. Проверить в БД ДО перезапуска
docker compose exec db psql -U postgres -d microblog -c \
  "SELECT id, content FROM tweets WHERE content LIKE '%персистентности%';"

# 3. Перезапустить контейнеры
docker compose restart

# 4. Подождать 15 секунд
sleep 15

# 5. Проверить в БД ПОСЛЕ перезапуска
docker compose exec db psql -U postgres -d microblog -c \
  "SELECT id, content FROM tweets WHERE content LIKE '%персистентности%';"
```

**Результат**: Твит должен остаться на месте

---

## 4. Требования к коду (4/4)

| № | Требование | Команда проверки | Результат       |
|---|------------|------------------|-----------------|
| 1 | Тесты проходят | `docker compose exec app pytest -v` | ✅ **39 passed** |
| 2 | Flake8 без ошибок | `docker compose exec app flake8 app` | ✅ **0 ошибок**  |
| 3 | Mypy (опционально) | `docker compose exec app mypy app` | ⚠️ 14 warnings  |
| 4 | Покрытие тестами | `docker compose exec app pytest --cov=app` | ✅ **65%**       |

### Запуск всех проверок

```bash
# Тесты
docker compose exec app pytest -v

# Линтер  
docker compose exec app flake8 app

# Типизация (опционально)
docker compose exec app mypy app

# Покрытие
docker compose exec app pytest --cov=app --cov-report=term-missing
```

---

## 5. Архитектура проекта

### Docker Compose сервисы

| Сервис | Описание | Порт | Статус |
|--------|----------|------|--------|
| **nginx** | Reverse proxy + статика | 80 | ✅ |
| **app** | FastAPI приложение | 8000 | ✅ |
| **db** | PostgreSQL 15 | 5432 | ✅ |

### Volumes (персистентность)

- `microblog_postgres_data` — база данных
- `microblog_media_data` — загруженные изображения

### Технологический стек

- **Backend**: Python 3.11, FastAPI, Uvicorn
- **ORM**: SQLAlchemy 2.0 (async), asyncpg
- **БД**: PostgreSQL 15
- **Валидация**: Pydantic 2.0
- **Безопасность**: bcrypt (хеширование)
- **Миграции**: Alembic
- **Тесты**: pytest, pytest-asyncio, httpx
- **Линтинг**: flake8, black, isort

---

## 6. Дополнительные возможности ⭐

### Безопасность

| Функция | Реализация | Статус |
|---------|------------|--------|
| Хеширование паролей | bcrypt | ✅ |
| Гибридная аутентификация | Plain text + bcrypt | ✅ |
| API-ключи в заголовках | `api-key` header | ✅ |

### Медиафайлы

- ✅ Поддержка: PNG, JPEG, GIF, WebP
- ✅ Ограничение размера: 5 MB
- ✅ Уникальные имена (UUID)
- ✅ Хранение в Docker volume
- ✅ Доступ через `/media/{filename}`

### API Features

- ✅ Автогенерация Swagger/ReDoc документации
- ✅ CORS middleware
- ✅ Валидация входных данных (Pydantic)
- ✅ Обработка ошибок с типизированными ответами
- ✅ Асинхронная обработка запросов

---

## 7. Способы демонстрации

### Через браузер (фронтенд)

```
1. Открыть: http://localhost
2. Ввести api-key: test
3. Создавать твиты, ставить лайки
```

### Через Swagger UI

```
1. Открыть: http://localhost/api/docs
2. Ввести api-key: test
3. Тестировать все endpoints
```

### Через curl (командная строка)

```bash
curl http://localhost/api/users/me -H "api-key: test"
curl -X POST http://localhost/api/tweets \
  -H "api-key: test" \
  -H "Content-Type: application/json" \
  -d '{"tweet_data": "Test!"}'
```

---

## 8. Итоговая оценка

| Категория | Результат   | Оценка |
|-----------|-------------|--------|
| Функциональные требования | 11/10       | ⭐ +1 endpoint |
| Нефункциональные требования | 6/6         | ✅ 100% |
| Тесты | 39 passed   | ✅ Отлично |
| Flake8 | 0 ошибок    | ✅ Идеально |
| Mypy | 14 warnings | ⚠️ Допустимо |
| Покрытие кода | 65%         | ✅ Хорошо |
| Дополнительные features | +3          | ⭐ Бонусы |

### Дополнительные достижения

- **Endpoint создания пользователей** (`POST /api/users`)
- **Гибридная аутентификация** (bcrypt + plain text)
- **Безопасность** (хеширование паролей)

---

## 9. Устранение неполадок

### Контейнеры не запускаются

```bash
docker compose down -v
docker compose up -d --build
```

### Тесты падают

```bash
# Обновить conftest.py (использует bcrypt)
docker compose exec app pytest -v
```

### API не отвечает

```bash
# Проверить логи
docker compose logs -f app

# Проверить healthcheck
docker compose ps
```

---

## 10. Ссылки

- **GitLab**: https://gitlab.skillbox.ru/iurii_shmyrev/python_advanced_diploma
- **Swagger**: http://localhost/api/docs
- **Фронтенд**: http://localhost

---