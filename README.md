# YaTube
### Описание
Социальная сеть для блогеров, публикация личных дневников.
### Технологии
- Python 3.7
- Django 2.2.19
### Запуск проекта в dev-режиме
Клонировать репозиторий и перейти в него в командной строке:
```
git clone https://github.com/Alisacalm/Yatube.git
```
```
cd api_final_yatube
```
Cоздать и активировать виртуальное окружение:
```
python/python3 -m venv env
```
* Если у вас Linux/macOS
```
source env/bin/activate
```
* Если у вас windows
```
source env/scripts/activate
```
```
python/python3 -m pip install --upgrade pip
```
Установить зависимости из файла requirements.txt:
```
pip install -r requirements.txt --use-pep517
```
Выполнить миграции:
```
python/python3 manage.py migrate
```
Запустить проект:
```
python/python3 manage.py runserver
```
