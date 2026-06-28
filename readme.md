# TeamFinder — учебная версия backend на Django

TeamFinder — платформа для поиска участников в pet-проекты. Реализован вариант 3: **необходимые навыки проектов и фильтрация проектов по навыкам**.

## Возможности

- регистрация и вход по email;
- публичные профили пользователей;
- редактирование профиля;
- смена пароля;
- список пользователей с пагинацией;
- создание, редактирование и завершение проектов;
- участие в чужих открытых проектах;
- необходимые навыки проекта;
- AJAX-добавление, удаление и автодополнение навыков;
- фильтрация проектов по навыкам;
- PostgreSQL через Docker Compose;
- тестовый режим на SQLite;
- базовые автоматические тесты.

## Быстрый запуск на Windows / macOS / Linux

```bash
python -m venv venv
```

Активация:

```bash
# Windows PowerShell
venv\Scripts\Activate.ps1

# Windows cmd
venv\Scripts\activate.bat

# macOS / Linux
source venv/bin/activate
```

Установка зависимостей:

```bash
pip install -r requirements.txt
```

Создайте `.env`:

```bash
cp .env_example .env
```

## Запуск с PostgreSQL

Запустите базу:

```bash
docker compose up -d
```

В `.env` оставьте:

```env
DB_ENGINE=postgresql
POSTGRES_DB=teamfinder
POSTGRES_USER=teamfinder
POSTGRES_PASSWORD=teamfinder
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

Примените миграции:

```bash
python manage.py migrate
```

Создайте суперпользователя:

```bash
python manage.py createsuperuser
```

По желанию создайте демо-данные:

```bash
python manage.py seed_demo
```

Запустите сервер:

```bash
python manage.py runserver
```

Откройте:

```text
http://127.0.0.1:8000/
```

Демо-аккаунт после `seed_demo`:

```text
email: maria@example.com
password: password
```

## Быстрый запуск без Docker, только для тестов

В `.env` поставьте:

```env
DB_ENGINE=sqlite
```

Затем:

```bash
python manage.py migrate
python manage.py test
python manage.py runserver
```

## Проверка качества

```bash
python manage.py check
python manage.py test
```

## Основные URL

```text
/                         -> редирект на /projects/list/
/projects/list/           -> список проектов
/projects/<id>/           -> страница проекта
/projects/create-project/ -> создание проекта
/projects/<id>/edit/      -> редактирование проекта
/projects/<id>/complete/  -> завершение проекта, POST
/projects/<id>/toggle-participate/ -> участие/отказ, POST
/projects/skills/         -> автодополнение навыков
/projects/<id>/skills/add/ -> добавление навыка, POST
/projects/<id>/skills/<skill_id>/remove/ -> удаление навыка, POST
/users/register/          -> регистрация
/users/login/             -> вход
/users/logout/            -> выход
/users/list/              -> список пользователей
/users/<id>/              -> профиль пользователя
/users/edit-profile/      -> редактирование профиля
/users/change-password/   -> смена пароля
```
