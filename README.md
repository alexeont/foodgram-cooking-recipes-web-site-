![workflow](https://github.com/alexeont/foodgram-project-react/actions/workflows/main.yml/badge.svg?event=push)

##  Описание проекта Foodgram:

Сайт кулинарных рецептов. Неавторизованным пользователям доступен просмотр выложенных рецептов. Для публикации своего, добавления в избранное и список покупок, подписки на автора -- необходима регистрация.

## Cтек технологий:

- Python 3.9 as programming language
- Django 3.2 as web framework
- Django REST framework 3.12 as toolkit for building Web APIs
- POSTGRESQL as database
- GitHub as repo and workflows manager
- Docker as deploy and containerization service
- Reportlab 4.0.9 as pdf-generation software

## Установка:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/alexeont/foodgram-project-react
cd foodgram-project-react
```

Cоздать и активировать виртуальное окружение:

```
cd backend/foodgram/
python -m venv venv
```

```
source venv/Scripts/activate
```

```
python -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Создать файл зависимостей среды .env в корне проекта. Образец -- `.env.example`


## Запуск проекта на удаленном сервере:

1. В своем репозитории на GitHub в разделе настроек добавить необходимые секреты для файла `.github/workflows/main.yml`
2. Перенести в папку проекта на сервере файл `.env`
3. Установить докер на сервер
4. Запушить проект на гит, чтобы запустить процесс автоматического деплоя

Автор проекта: Александр Леонтьев
