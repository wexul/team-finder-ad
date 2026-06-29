# TeamFinder — backend на Django

TeamFinder — платформа для поиска участников в pet-проекты. Реализован вариант 3: **необходимые навыки проектов и фильтрация проектов по навыкам**.

## Автор

[Полошков Ярослав Витальевич](https://t.me/wexul)

## Технологический стек

- Python 3.11+
- Django 5.2
- PostgreSQL
- Docker Compose
- Pillow
- python-decouple
- HTML-шаблоны, CSS и JavaScript из стартового набора TeamFinder

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

## Клонирование проекта

```bash
git clone https://github.com/wexul/team-finder-ad.git
cd team-finder-ad
```

## Быстрый запуск на Windows / macOS / Linux

Создайте виртуальное окружение:

```bash
python -m venv venv
```

Активируйте его:

```bash
# Windows PowerShell
venv\Scripts\Activate.ps1

# Windows cmd
venv\Scripts\activate.bat

# macOS / Linux
source venv/bin/activate
```

Установите зависимости:

```bash
pip install -r requirements.txt
```

Создайте файл переменных окружения:

```bash
# Windows
copy .env_example .env

# macOS / Linux
cp .env_example .env
```

## Запуск с PostgreSQL

Запустите базу данных:

```bash
docker compose up -d
```

В `.env` оставьте настройки PostgreSQL:

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

Откройте сайт:

```text
http://127.0.0.1:8000/
```

Админка доступна по адресу:

```text
http://127.0.0.1:8000/admin/
```

Демо-аккаунт после команды `seed_demo`:

```text
email: maria@example.com
password: password
```

## Быстрый запуск без Docker

Этот режим нужен только для локальной проверки, если PostgreSQL или Docker пока не настроены.

В `.env` поставьте:

```env
DB_ENGINE=sqlite
```

Затем выполните:

```bash
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

## Проверка качества

```bash
python manage.py check
python manage.py test
```

## Основные URL

```text
/                                      -> редирект на /projects/list/
/admin/                                -> админка
/projects/list/                        -> список проектов
/projects/<id>/                        -> страница проекта
/projects/create-project/              -> создание проекта
/projects/<id>/edit/                   -> редактирование проекта
/projects/<id>/complete/               -> завершение проекта, POST
/projects/<id>/toggle-participate/      -> участие/отказ, POST
/projects/skills/                      -> автодополнение навыков
/projects/<id>/skills/add/             -> добавление навыка, POST
/projects/<id>/skills/<skill_id>/remove/ -> удаление навыка, POST
/users/register/                       -> регистрация
/users/login/                          -> вход
/users/logout/                         -> выход
/users/list/                           -> список пользователей
/users/<id>/                           -> профиль пользователя
/users/edit-profile/                   -> редактирование профиля
/users/change-password/                -> смена пароля
```
