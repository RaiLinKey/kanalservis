# kanalservis
Тестовое задание для устройства на работу в компанию ООО «Каналсервис» сделанное Еремеевым Романом Александровичем.
Ссылка на таблицу Google Sheets:
https://docs.google.com/spreadsheets/d/1gv6K3S_gltFpsH4xsYGYKjYGEx1hj3eSFWX5e8xPrK4
## Инструкция по запуску разработанных скриптов
### **1. Запуск PostgreSQL**
Прежде всего необходимо запустить PostgreSQL и подготовить к работе. Создайте пользователя, убедитесь в работспособности.
### **2. Установка необходимых библиотек для Python**
Для установки всех библиотек, которые понадобятся находясь в корневой директории напишите команду:  
**Windows:**
```
pip install -r requirements.txt
```
**Linuux:**
```
pip3 install -r requirements.txt
```
### **3. Настройка и запуск Django**
Перейдите в директорию `.kanalservis/kanalservis` и в файле `settings.py` отредактируйте параметры DATABASES. Значения по умолчанию:
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'kanalservis',
        'USER': 'postgres',
        'PASSWORD': '1234',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```
Далее вернитесь в директорию `.kanalservis`, где находится файл `manage.py`. Отсюда запустите команды:  
**Windows:**
```
python manage.py makemigration
python manage.py migrate
```
**Linux:**
```
python3 manage.py makemigration
python3 manage.py migrate
```
После завершения миграции можно запустить Django и проверить его работспособность командой:  
**Windows:**
```
python manage.py runserver
```
**Linux:**
```
python3 manage.py runserver
```
### **4. Добавление таблиц в ЬД, необходимых для работы Telegram бота**
В корневой директории находится папка `sql`. В ней находится файл `tlegram_tables.sql` с SQL-скриптами, которые создают нужные таблицы и процедуру. Запустите их в PostgreSQL.
### **5. Запуск основного скрипта**
Находясь в корневой директории в отдельном окне терминала (для Linux можно воспользоваться утилитами screen или tmux) напишите команду:  
**Windows:**
```
python main.py
```
**Linux:**
```
python3 main.py
```
### **6. Запуск Telegram-бота**
Находясь в корневой директории в отдельном окне терминала (для Linux можно воспользоваться утилитами screen или tmux) напишите команду:  
**Windows:**
```
python notification_bot.py
```
**Linux:**
```
python3 notification_bot.py
```
При включении по умолчанию работает бот по ссылке t.me/rlk_bot. Чтобы использовать собственного бота в переменную `TOKEN` установите его токен.
### **7. Запуск Django**
Теперь можно окончательно запустить Django находясь в директории `.kanalservis` напишите команду:  
**Windows:**
```
python manage.py runserver
```
**Linux:**
```
python3 manage.py runserver
```
