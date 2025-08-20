# 💬 WebChat (FastAPI + WebSocket)

Простой чат с комнатами, авторизацией через JWT и обменом сообщениями в реальном времени через WebSocket.

![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green)

---

## 🚀 Возможности
- 👤 Регистрация и вход через JWT (cookie или Bearer токен)
- 💬 Создание чатов и присоединение по инвайт-коду
- 🔗 Подключение через WebSocket (`/ws/{chat_id}`)
- 📌 Возможность закрепить сообщение командой `/pin`
- 🗄️ Хранение в базе (SQLite или PostgreSQL)
- 🔄 Миграции через Alembic

---

## ⚙️ Установка и запуск

### 1. Клонировать репозиторий
```bash
git clone https://github.com/aknur111/webchat_project.git
cd webchat_project

```
### 2. Создать виртуальное окружение и установить зависимости

```
python -m venv .venv

source .venv/bin/activate      # macOS / Linux
.venv\Scripts\Activate.ps1     # Windows

pip install -r requirements.txt

```
### 3. Создайте базу данных в PostgreSql под названием **webchat**


### 4. Настроить .env
```
JWT_SECRET_KEY= your_secret_key


POSTGRESQL_USERNAME=postgres
POSTGRESQL_PASSWORD=your_password
POSTGRESQL_SERVER=localhost
POSTGRESQL_PORT=5432
POSTGRESQL_DATABASE=webchat
ENVIRONMENT=local
DOMAIN=localhost
SECRET_KEY = your_secret_key


```

### 5. Применить миграции
```
alembic upgrade head
```
### 6. Запустить сервер
```
uvicorn main:app --reload
```

## 📍 Открыть:

http://127.0.0.1:8000/
 — фронт

http://127.0.0.1:8000/docs
 — Swagger API

## 📝 Использование

Зарегистрируй пользователя

Войди и получи cookie с JWT

Создай чат → получи invite code

Второй пользователь → "Join by code"

Общайтесь через WebSocket 🎉

> 💡 **Тест нескольких аккаунтов**
>
> Приложение использует cookie для аутентификации. В одном браузере активен только один логин.
> Чтобы зайти вторым пользователем одновременно, открой проект:
> - в **другом браузере** (например, Chrome + Firefox), или
> - в **режиме инкогнито** второго окна.

## 📂 Структура проекта
```
src/
  endpoints/     # REST и WebSocket ручки
  models/        # SQLAlchemy модели
  schemas/       # Pydantic схемы
  utils/         # JWT, bcrypt, хелперы
alembic/         # миграции
main.py          # входная точка (FastAPI app)
```

## 👩‍💻 Автор: 
@aknur111
