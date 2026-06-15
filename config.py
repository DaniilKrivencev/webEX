import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'very-secret-key-change-in-production')

    # SQLite connection (works out of the box without MySQL setup)
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(basedir, 'library.db')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'covers')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

    BOOKS_PER_PAGE = 10

    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
