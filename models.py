from datetime import datetime
from extensions import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


# Association table: books <-> genres
book_genres = db.Table(
    'book_genres',
    db.Column('book_id', db.Integer, db.ForeignKey('books.id', ondelete='CASCADE'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genres.id', ondelete='CASCADE'), primary_key=True)
)

# Association table: books <-> collections
book_collections = db.Table(
    'book_collections',
    db.Column('book_id', db.Integer, db.ForeignKey('books.id', ondelete='CASCADE'), primary_key=True),
    db.Column('collection_id', db.Integer, db.ForeignKey('collections.id', ondelete='CASCADE'), primary_key=True)
)


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)

    users = db.relationship('User', back_populates='role')

    def __repr__(self):
        return f'<Role {self.name}>'


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(256), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    middle_name = db.Column(db.String(100), nullable=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)

    role = db.relationship('Role', back_populates='users')
    reviews = db.relationship('Review', back_populates='user', cascade='all, delete-orphan')
    collections = db.relationship('Collection', back_populates='user', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def full_name(self):
        parts = [self.last_name, self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        return ' '.join(parts)

    @property
    def is_admin(self):
        return self.role.name == 'Администратор'

    @property
    def is_moderator(self):
        return self.role.name == 'Модератор'

    @property
    def is_user(self):
        return self.role.name == 'Пользователь'

    def __repr__(self):
        return f'<User {self.login}>'


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


class Cover(db.Model):
    __tablename__ = 'covers'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    mime_type = db.Column(db.String(100), nullable=False)
    md5_hash = db.Column(db.String(32), nullable=False, unique=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id', ondelete='CASCADE'), nullable=False)

    book = db.relationship('Book', back_populates='cover', uselist=False)

    def __repr__(self):
        return f'<Cover {self.filename}>'


class Genre(db.Model):
    __tablename__ = 'genres'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

    books = db.relationship('Book', secondary=book_genres, back_populates='genres')

    def __repr__(self):
        return f'<Genre {self.name}>'


class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    publisher = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    pages = db.Column(db.Integer, nullable=False)

    genres = db.relationship('Genre', secondary=book_genres, back_populates='books')
    cover = db.relationship('Cover', back_populates='book', uselist=False, cascade='all, delete-orphan')
    reviews = db.relationship('Review', back_populates='book', cascade='all, delete-orphan')
    collections = db.relationship('Collection', secondary=book_collections, back_populates='books')

    @property
    def average_rating(self):
        if not self.reviews:
            return None
        return sum(r.rating for r in self.reviews) / len(self.reviews)

    @property
    def reviews_count(self):
        return len(self.reviews)

    def __repr__(self):
        return f'<Book {self.title}>'


class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.TIMESTAMP, nullable=False, default=datetime.utcnow)

    book = db.relationship('Book', back_populates='reviews')
    user = db.relationship('User', back_populates='reviews')

    def __repr__(self):
        return f'<Review book={self.book_id} user={self.user_id}>'


class Collection(db.Model):
    __tablename__ = 'collections'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    user = db.relationship('User', back_populates='collections')
    books = db.relationship('Book', secondary=book_collections, back_populates='collections')

    def __repr__(self):
        return f'<Collection {self.name}>'
