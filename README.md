# IT Lab Test

## Описание

Тестовое задание: Telegram-бот для управления списком задач с Django-бэкендом.

Стек: Django 5, Django REST Framework, Celery + Redis, PostgreSQL, Aiogram 3 + aiogram-dialog, Docker Compose.

Архитектура: Clean Architecture (Domain / Application / Infrastructure / Presentation).

---

- Модели Task и Category с ULID-первичными ключами (без UUID, автоинкремента и случайных значений)
- CRUD REST API на Django REST Framework
- Django Admin с поддержкой ULID
- Celery: уведомления в Telegram точно в срок задачи через `apply_async(eta=due_date)`
- Aiogram-dialog: пошаговый FSM-диалог создания задачи в Telegram-боте
- Часовой пояс сервера: America/Adak (UTC-10)
- Начальные данные в миграциях: пользователи `admin` / `test_user`, категория `Test`

---

## Запуск

1. Клонировать репозиторий и перейти в директорию:

```bash
git clone https://github.com/PavelBackend/it_lab_test.git && cd it_lab_test
```

2. Скопировать конфиги и запустить все сервисы:

```bash
cp backend/.env.example backend/.env && cp bot/.env.example bot/.env && docker-compose up --build -d
```

Миграции (включая создание тестовых данных) применяются автоматически при старте backend-контейнера.

## Тестирование

Django Admin: http://localhost:8000/admin/

```
Логин: admin
Пароль: admin
```

REST API: http://localhost:8000/api/v1/

```
Эндпоинты: /tasks/, /tasks/<id>/, /categories/, /categories/<id>/
Basic Auth: test_user / test_user_password
```

Telegram-бот: https://t.me/ai_lab_test_pavel_bot

```
Аутентификация бота: test_user / test_user_password
Команды:
  /start      - приветствие
  /list       - список задач с датой создания и сроком
  /create     - создать задачу (пошаговый диалог: название, описание, категория, срок)
  /categories - список категорий

Срок задачи вводится в часовом поясе America/Adak (UTC-10).
Celery отправляет уведомление в Telegram точно в указанное время.
```

## Остановка

```bash
docker-compose down
```

Добавьте `-v` чтобы удалить тома с данными базы данных:

```bash
docker-compose down -v
```
