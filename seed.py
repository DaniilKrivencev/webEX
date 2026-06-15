"""
Seed script: creates tables and inserts initial data.
Run once: python seed.py
"""
from app import create_app
from extensions import db
from models import Role, User, Genre

app = create_app()

with app.app_context():
    db.create_all()
    print("Tables created.")

    # Roles
    roles_data = [
        ('Администратор', 'Суперпользователь с полным доступом, включая создание и удаление книг'),
        ('Модератор',     'Может редактировать данные книг и модерировать рецензии'),
        ('Пользователь',  'Может оставлять рецензии и создавать подборки'),
    ]
    roles = {}
    for name, desc in roles_data:
        r = Role.query.filter_by(name=name).first()
        if not r:
            r = Role(name=name, description=desc)
            db.session.add(r)
            db.session.flush()
            print(f"  Role added: {name}")
        roles[name] = r
    db.session.commit()

    # Default users
    users_data = [
        ('admin',    'Admin123!',  'Администратов', 'Алексей',    'Иванович',  'Администратор'),
        ('moder',    'Moder123!',  'Модераторов',   'Михаил',     'Петрович',  'Модератор'),
        ('user',     'User1234!',  'Пользователев', 'Павел',      'Сергеевич', 'Пользователь'),
    ]
    for login, pw, ln, fn, mn, role_name in users_data:
        u = User.query.filter_by(login=login).first()
        if not u:
            u = User(
                login=login, last_name=ln, first_name=fn,
                middle_name=mn, role=roles[role_name]
            )
            u.set_password(pw)
            db.session.add(u)
            print(f"  User added: {login} ({role_name})")
    db.session.commit()

    # Genres
    genre_names = [
        'Роман', 'Фантастика', 'Детектив', 'Приключения',
        'История', 'Биография', 'Наука', 'Философия',
        'Поэзия', 'Ужасы', 'Фэнтези', 'Психология',
    ]
    for gname in genre_names:
        if not Genre.query.filter_by(name=gname).first():
            db.session.add(Genre(name=gname))
            print(f"  Genre added: {gname}")
    db.session.commit()

    print("\nSeed complete!")
    print("  admin  / Admin123!")
    print("  moder  / Moder123!")
    print("  user   / User1234!")
