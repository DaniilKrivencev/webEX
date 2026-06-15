"""
Seed script: creates tables, inserts initial data including default books and covers.
"""
from app import create_app
from extensions import db
from models import Role, User, Genre, Book, Cover
import os

app = create_app()

books_seed_data = [{'title': 'Мастер и Маргарита', 'author': 'Михаил Булгаков', 'year': 1967, 'publisher': 'Художественная литература', 'pages': 480, 'description': 'Роман Михаила Афанасьевича Булгакова, работа над которым началась в конце 1920-х годов и продолжалась вплоть до смерти писателя. Роман относится к незавершённым произведениям; редактирование и сведение воедино черновых записей осуществляла после смерти мужа вдова писателя, Елена Сергеевна.', 'genres': ['Роман', 'Философия'], 'image_file': 'Мастер и Маргарита.jpg', 'cover_filename': 'ce8c50e59d329bc7d996e6c4307f5755.jpg', 'cover_md5': 'ce8c50e59d329bc7d996e6c4307f5755', 'cover_mime': 'image/jpeg'}, {'title': '1984', 'author': 'Джордж Оруэлл', 'year': 1949, 'publisher': 'Secker & Warburg', 'pages': 328, 'description': 'Роман-антиутопия Джорджа Оруэлла, изданный в 1949 году. Название романа, его терминология и имя автора стали нарицательными и употребляются для обозначения общественного уклада, напоминающего описанный в романе тоталитарный режим.', 'genres': ['Роман', 'Фантастика'], 'image_file': '1984.jpg', 'cover_filename': '0b600d9e489199015366f605793295da.jpg', 'cover_md5': '0b600d9e489199015366f605793295da', 'cover_mime': 'image/jpeg'}, {'title': 'Преступление и наказание', 'author': 'Фёдор Достоевский', 'year': 1866, 'publisher': 'Русский вестник', 'pages': 600, 'description': 'Социально-психологический и социально-философский роман Фёдора Михайловича Достоевского, над которым писатель работал в 1865—1866 годах. Впервые опубликован в 1866 году в журнале «Русский вестник».', 'genres': ['Роман', 'Психология', 'Философия'], 'image_file': 'Преступление и наказание.jpg', 'cover_filename': '5d7bb9b5493c9e1287f3b71603f15a01.jpg', 'cover_md5': '5d7bb9b5493c9e1287f3b71603f15a01', 'cover_mime': 'image/jpeg'}, {'title': 'Война и мир', 'author': 'Лев Толстой', 'year': 1869, 'publisher': 'Русский вестник', 'pages': 1225, 'description': 'Роман-эпопея Льва Николаевича Толстого, описывающий русское общество в эпоху войн против Наполеона в 1805—1812 годах. Одно из самых масштабных и известных произведений мировой литературы.', 'genres': ['Роман', 'История'], 'image_file': 'Война и мир.jpg', 'cover_filename': '309f5051f23480b2e7a90b0e358370e3.jpg', 'cover_md5': '309f5051f23480b2e7a90b0e358370e3', 'cover_mime': 'image/jpeg'}, {'title': 'Маленький принц', 'author': 'Антуан де Сент-Экзюпери', 'year': 1943, 'publisher': 'Reynal & Hitchcock', 'pages': 96, 'description': 'Аллегорическая повесть-сказка, наиболее известное произведение Антуана де Сент-Экзюпери. Рисунки в книге выполнены самим автором и не менее знамениты, чем сама книга.', 'genres': ['Приключения', 'Философия'], 'image_file': 'Маленький принц.jpg', 'cover_filename': 'c28a11396a299fb1fc3d6e7aecfd0fec.jpg', 'cover_md5': 'c28a11396a299fb1fc3d6e7aecfd0fec', 'cover_mime': 'image/jpeg'}]

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
    genres_cache = {}
    for gname in genre_names:
        g = Genre.query.filter_by(name=gname).first()
        if not g:
            g = Genre(name=gname)
            db.session.add(g)
            db.session.flush()
            print(f"  Genre added: {gname}")
        genres_cache[gname] = g
    db.session.commit()

    # Books & Covers
    for b in books_seed_data:
        existing_book = Book.query.filter_by(title=b["title"]).first()
        if not existing_book:
            new_book = Book(
                title=b["title"],
                author=b["author"],
                year=b["year"],
                publisher=b["publisher"],
                pages=b["pages"],
                description=b["description"]
            )
            # Link genres
            for gname in b["genres"]:
                if gname in genres_cache:
                    new_book.genres.append(genres_cache[gname])
            
            db.session.add(new_book)
            db.session.flush() # get new_book.id
            
            # Create cover if exists
            if b.get("cover_filename"):
                cover = Cover(
                    filename=b["cover_filename"],
                    mime_type=b["cover_mime"],
                    md5_hash=b["cover_md5"],
                    book_id=new_book.id
                )
                db.session.add(cover)
            
            print(f"  Book added: {b['title']}")
    db.session.commit()

    print("\nSeed complete!")
    print("  admin  / Admin123!")
    print("  moder  / Moder123!")
    print("  user   / User1234!")
