from flask import Flask
from extensions import db, login_manager, migrate
from config import Config
import os
import markdown as md_lib
import bleach


# Allowed tags for markdown rendering
MD_ALLOWED_TAGS = [
    'p', 'br', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'pre', 'code', 'blockquote', 'ul', 'ol', 'li',
    'strong', 'em', 'b', 'i', 'a', 'table', 'thead',
    'tbody', 'tr', 'th', 'td', 'hr', 'del', 'sup', 'sub',
]
MD_ALLOWED_ATTRS = {
    'a': ['href', 'title', 'target'],
    'img': ['src', 'alt', 'title'],
    'code': ['class'],
    'pre': ['class'],
}


def render_md(text):
    """Convert markdown text to sanitized HTML."""
    if not text:
        return ''
    try:
        html = md_lib.markdown(str(text), extensions=['extra'])
    except Exception:
        html = md_lib.markdown(str(text))
    return bleach.clean(html, tags=MD_ALLOWED_TAGS, attributes=MD_ALLOWED_ATTRS)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Для выполнения данного действия необходимо пройти процедуру аутентификации'
    login_manager.login_message_category = 'warning'

    # Register markdown Jinja2 filter
    app.jinja_env.filters['markdown'] = render_md

    from blueprints.auth import auth_bp
    from blueprints.books import books_bp
    from blueprints.reviews import reviews_bp
    from blueprints.collections import collections_bp
    from blueprints.main import main_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(books_bp, url_prefix='/books')
    app.register_blueprint(reviews_bp, url_prefix='/reviews')
    app.register_blueprint(collections_bp, url_prefix='/collections')
    app.register_blueprint(main_bp)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    return app


app = create_app()

from flask import send_from_directory
import os

@app.route('/demo_library.html')
def serve_demo():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'demo_library.html')

if __name__ == '__main__':
    app.run(debug=True, port=5100)
