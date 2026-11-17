# Страйк & Пул

Учебный сайт боулинг- и бильярдного клуба на Django. Интерфейс собирается по [макету занятия 6](https://www.figma.com/design/3Umnb9IlotQspcCP82lTkr).

## Запуск

Нужен Python 3.12 или новее. Проект проверяется на Python 3.14.

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
.venv/Scripts/python.exe manage.py migrate
.venv/Scripts/python.exe manage.py runserver
```

В Linux и macOS используйте `.venv/bin/python` вместо `.venv/Scripts/python.exe`.

База SQLite создаётся локально после миграций. База, виртуальное окружение, `.env` и пользовательские файлы `media` в репозиторий не входят.

## Структура

- `config/` — настройки проекта и общие маршруты.
- `club/` — приложение клуба.
- `templates/` — шаблоны страниц.
- `static/` — стили и изображения интерфейса.

## Занятие 7

Первый этап: созданы проект и приложение, подключены шаблоны, статика и SQLite. Дальше — главная страница и маршруты.

```powershell
.venv/Scripts/python.exe manage.py check
```

Настройки предназначены для локальной разработки. `DJANGO_SECRET_KEY`, `DJANGO_DEBUG` и `DJANGO_ALLOWED_HOSTS` передаются через переменные окружения. Без заданного ключа при старте создаётся временный ключ; для постоянных сессий задайте свой ключ в окружении. Файл `.env` автоматически не загружается.
