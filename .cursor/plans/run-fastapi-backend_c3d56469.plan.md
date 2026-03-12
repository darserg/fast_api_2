---
name: run-fastapi-backend
overview: Пошаговая инструкция, как локально запустить этот FastAPI‑проект на macOS через виртуальное окружение Python и PostgreSQL.
todos:
  - id: env-and-deps
    content: Проверить/создать виртуальное окружение .venv и установить зависимости через pip install -r requirements.txt.
    status: pending
  - id: db-env-config
    content: Описать, какие переменные окружения POSTGRES_* нужны и как создать .env для src/core/config.py.
    status: pending
  - id: db-setup
    content: Кратко описать требуемые шаги по созданию пользователя и базы в PostgreSQL, соответствующих .env.
    status: pending
  - id: run-server
    content: Описать команды запуска приложения (python -m src.main, альтернативно uvicorn) и URL для проверки работы.
    status: pending
isProject: false
---

## Цель

Сделать так, чтобы ты мог(ла) локально поднять API‑сервер (FastAPI) из этого репозитория, знал(а) какие переменные окружения нужны, какие команды вводить в терминале и как проверить, что всё работает.

## Важные файлы проекта

- **Основная точка входа сервера**: `[src/main.py](src/main.py)`
- **Создание FastAPI‑приложения**: `[src/app.py](src/app.py)`
- **Маршруты API**: `[src/api/routes/users.py](src/api/routes/users.py)`, `[src/api/routes/posts.py](src/api/routes/posts.py)`
- **Настройка PostgreSQL и переменные окружения**: `[src/core/config.py](src/core/config.py)`
- **Подключение к БД и сессии**: `[src/core/db.py](src/core/db.py)`
- **Зависимости проекта**: `[requirements.txt](requirements.txt)`
- **Настройки Alembic (миграции)**: `[alembic.ini](alembic.ini)`, каталог `[migrations/](migrations/)`

## 1. Предусловия (что должно быть установлено)

- **Python** версии 3.11+ (у тебя уже, судя по структуре `.venv`, всё ок; но на всякий случай укажем)
- **PostgreSQL** (может быть установлен локально или запущен в Docker — в плане опишем абстрактно, без жёсткой привязки к способу)
- **Git / IDE** не обязательны для запуска, только для удобства работы.

## 2. Создание и активация виртуального окружения

В корне проекта `/Users/darserg/fastapi-backend` в терминале:

- **Создать виртуальное окружение (если ещё не создано)**:
  - Команда: `python -m venv .venv`
- **Активировать окружение (macOS, zsh)**:
  - Команда: `source .venv/bin/activate`
- **Проверить, что Python и pip идут из `.venv`**:
  - Команда: `which python` и `which pip` (должны указывать на путь внутри `.venv`).

Если окружение `.venv` у тебя уже настроено (оно есть в проекте), можно шаг с `python -m venv .venv` пропустить и сразу делать `source .venv/bin/activate`.

## 3. Установка зависимостей

В активированном виртуальном окружении:

- **Установить пакеты из `requirements.txt`**:
  - Команда: `pip install -r requirements.txt`

Это подтянет `fastapi`, `uvicorn[standard]`, `SQLAlchemy`, драйвер для PostgreSQL (`psycopg2-binary`), Alembic и т.д.

## 4. Настройка переменных окружения для PostgreSQL

Файл `[src/core/config.py](src/core/config.py)` ожидает переменные из `.env` в корне проекта:

- Обязательные переменные:
  - `POSTGRES_USER`
  - `POSTGRES_PASSWORD`
  - `POSTGRES_DB`
  - `POSTGRES_HOST`
  - `POSTGRES_PORT` (по умолчанию в коде 1301)

### 4.1. Создать файл `.env`

В корне проекта `/Users/darserg/fastapi-backend` создаём файл `.env` (обычный текстовый), со строками вида:

```bash
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=your_db
POSTGRES_HOST=localhost
POSTGRES_PORT=1301
```

- **Важно**: значения должны совпадать с настройками реально запущенного PostgreSQL.
- Порт по умолчанию в коде — **1301** (можно поменять либо в `.env`, либо в конфиге PostgreSQL, либо использовать проброс порта в Docker).

## 5. Поднять PostgreSQL и создать базу

Вариант зависит от того, как у тебя установлен PostgreSQL (через brew, Docker и т.п.). В общем виде шаги такие:

- **Убедиться, что сервер PostgreSQL запущен** (например, `pg_каisready` или просмотр в Docker Desktop / brew‑службах).
- **Создать пользователя и базу**, соответствующие значениям в `.env`:
  - Пример (консоль Postgres):
    - `CREATE USER your_user WITH PASSWORD 'your_password';`
    - `CREATE DATABASE your_db OWNER your_user;`

Конкретные команды могут отличаться в зависимости от установки, но суть: должен существовать пользователь и база, прописанные в `.env`.

## 6. (Опционально) Настройка и запуск миграций Alembic

В проекте уже есть базовая структура Alembic: `[alembic.ini](alembic.ini)` и каталог `[migrations/](migrations/)`. Пока там нет реальных версий миграций (каталога `migrations/versions`), но на будущее типичный рабочий цикл будет таким:

- **Сгенерировать первую миграцию** (после того, как у тебя будут ORM‑модели):
  - Команда: `alembic revision --autogenerate -m "init"`
- **Применить миграции к БД**:
  - Команда: `alembic upgrade head`

В рамках текущего вопроса для запуска сервера этот шаг можно пропустить, если код не требует существующих таблиц при старте.

## 7. Запуск FastAPI‑приложения

Основной запуск реализован в `[src/main.py](src/main.py)`, который создаёт приложение через `[src/app.py](src/app.py)` и поднимает `uvicorn`.

### Вариант 1: запуск через `python src/main.py`

Находясь в корне проекта (`/Users/darserg/fastapi-backend`) и с активированным виртуальным окружением:

- **Команда запуска**:
  - `python -m src.main`

или (так как в `src/main.py` есть `if __name__ == "__main__":`):

- `python src/main.py`

При этом внутри `main.py` создаётся конфиг uvicorn:

- приложение: `"main:app"` (модуль `main`, объект `app`)
- хост: `127.0.0.1`
- порт: `8000`
- `reload=False` (без авто‑перезагрузки)

### Вариант 2: запуск напрямую через `uvicorn`

Можно обойтись без `python src/main.py` и вызвать `uvicorn` напрямую, но надо указать правильный модуль и объект приложения (в `src/app.py` создаётся функция `create_app()`). Учитывая структуру, удобнее использовать уже подготовленный `main.py`, поэтому в плане основной вариант — первый.

Если очень нужно, альтернативный запуск (из корня проекта, с добавлением `src` в PYTHONPATH) мог бы выглядеть так:

- `uvicorn src.main:app --host 127.0.0.1 --port 8000`

Но он требует, чтобы Python нашёл модуль `src`, поэтому стандартнее использовать `python -m src.main`.

## 8. Проверка, что сервер работает

После запуска одной из команд из раздела 7:

- Открой браузер и перейди на `http://127.0.0.1:8000/api/v1/users` или `http://127.0.0.1:8000/api/v1/posts` (учитывай, что в `[src/app.py](src/app.py)` задан `root_path="/api/v1"`).
- Документация Swagger обычно доступна по адресу:
  - `http://127.0.0.1:8000/docs`

Если всё поднялось корректно, ты увидишь UI документации FastAPI и сможешь вызывать эндпоинты.

## 9. Краткий список команд

В одном месте, по шагам (предполагаем macOS, zsh, Python установлен, PostgreSQL настроен):

1. Перейти в папку проекта:
  - `cd /Users/darserg/fastapi-backend`
2. Активировать виртуальное окружение (если уже создано):
  - `source .venv/bin/activate`
  - (если нет виртуалки, сначала: `python -m venv .venv`)
3. Установить зависимости:
  - `pip install -r requirements.txt`
4. Создать `.env` с переменными `POSTGRES_`* (см. раздел 4).
5. Убедиться, что PostgreSQL запущен и база/пользователь созданы.
6. Запустить сервер:
  - `python -m src.main`
7. Открыть в браузере:
  - `http://127.0.0.1:8000/docs`
  - или `http://127.0.0.1:8000/api/v1/users` / `http://127.0.0.1:8000/api/v1/posts`.

На основе этого плана дальше можно будет отдельно расписать, как именно поднимать PostgreSQL (через Docker или brew), если это понадобится.