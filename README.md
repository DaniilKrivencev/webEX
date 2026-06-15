# Электронная библиотека

АИС «Электронная библиотека» на Flask + MySQL.

## Быстрый старт

### 1. Установить зависимости
```bash
pip install -r requirements.txt
```

### 2. Настроить MySQL
Создайте БД:
```sql
CREATE DATABASE library_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

При необходимости измените строку подключения в `config.py`:
```python
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@localhost/library_db'
```

### 3. Инициализировать БД и заполнить начальными данными
```bash
python seed.py
```

### 4. Запустить приложение
```bash
python app.py
```
Откройте http://127.0.0.1:5000

## Учётные записи

| Логин   | Пароль    | Роль            |
|---------|-----------|-----------------|
| admin   | Admin123! | Администратор   |
| moder   | Moder123! | Модератор       |
| user    | User1234! | Пользователь    |

## Структура проекта

```
webEX/
├── app.py              # Точка входа
├── config.py           # Конфигурация
├── extensions.py       # Flask extensions
├── models.py           # Модели SQLAlchemy
├── seed.py             # Начальные данные
├── blueprints/
│   ├── auth.py         # Аутентификация
│   ├── books.py        # Книги (CRUD)
│   ├── reviews.py      # Рецензии
│   ├── collections.py  # Подборки
│   └── main.py         # Главная страница
├── templates/
│   ├── base.html
│   ├── auth/login.html
│   ├── main/index.html
│   ├── books/ (view, add, edit, _form_macro)
│   ├── reviews/add.html
│   └── collections/ (index, view)
└── static/
    ├── css/style.css
    ├── js/app.js
    └── covers/         # Загруженные обложки
```
