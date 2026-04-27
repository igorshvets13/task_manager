# Task Manager API


## Запуск

### Локально

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Через Docker

```bash
docker-compose up --build
```

API будет доступен на `http://localhost:8000`

Документация: `http://localhost:8000/docs`

## API Эндпоинты

### Аутентификация

| Метод | URL | Описание |
|-------|-----|----------|
| POST | `/auth/register` | Регистрация |
| POST | `/auth/login` | Вход, получение токена |

### Задачи (требуют токен)

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/tasks/` | Все задачи пользователя |
| GET | `/tasks/?status=pending` | Фильтрация по статусу |
| GET | `/tasks/?priority=high` | Фильтрация по приоритету |
| POST | `/tasks/` | Создать задачу |
| GET | `/tasks/{id}` | Получить задачу по ID |
| PUT | `/tasks/{id}` | Обновить задачу |
| DELETE | `/tasks/{id}` | Удалить задачу |

## Примеры запросов

### Регистрация
```json
POST /auth/register
{
  "username": "igor",
  "email": "igor@example.com",
  "password": "mypassword"
}
```

### Создание задачи
```json
POST /tasks/
Authorization: Bearer <token>

{
  "title": "Выучить FastAPI",
  "description": "Прочитать документацию",
  "priority": "high",
  "deadline": "2025-06-01T00:00:00"
}
```

### Возможные значения

- **priority**: `low`, `medium`, `high`
- **status**: `pending`, `in_progress`, `done`

## Тесты

```bash
pytest tests/ -v
```

