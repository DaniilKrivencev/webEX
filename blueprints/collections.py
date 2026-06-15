from flask import (
    Blueprint, render_template, redirect, url_for,
    flash, request, abort
)
from flask_login import login_required, current_user
from models import Collection, Book, db
from functools import wraps

collections_bp = Blueprint('collections', __name__)


def user_only(f):
    """Accessible only to role='Пользователь'."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Для выполнения данного действия необходимо пройти процедуру аутентификации', 'warning')
            return redirect(url_for('auth.login'))
        if not current_user.is_user:
            flash('У вас недостаточно прав для выполнения данного действия', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated


@collections_bp.route('/')
@user_only
def index():
    collections = Collection.query.filter_by(user_id=current_user.id).order_by(Collection.id.desc()).all()
    return render_template('collections/index.html', collections=collections)


@collections_bp.route('/<int:collection_id>')
@user_only
def view(collection_id):
    collection = db.get_or_404(Collection, collection_id)
    if collection.user_id != current_user.id:
        abort(403)
    return render_template('collections/view.html', collection=collection)


@collections_bp.route('/add', methods=['POST'])
@user_only
def add():
    name = request.form.get('name', '').strip()
    if not name:
        flash('Название подборки не может быть пустым.', 'danger')
        return redirect(url_for('collections.index'))

    try:
        collection = Collection(name=name, user_id=current_user.id)
        db.session.add(collection)
        db.session.commit()
        flash(f'Подборка «{name}» успешно создана!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Ошибка при создании подборки.', 'danger')

    return redirect(url_for('collections.index'))


@collections_bp.route('/add-book', methods=['POST'])
@user_only
def add_book():
    book_id       = request.form.get('book_id', type=int)
    collection_id = request.form.get('collection_id', type=int)

    if not book_id or not collection_id:
        flash('Некорректные данные запроса.', 'danger')
        return redirect(url_for('main.index'))

    book       = db.get_or_404(Book, book_id)
    collection = db.get_or_404(Collection, collection_id)

    if collection.user_id != current_user.id:
        abort(403)

    try:
        if book not in collection.books:
            collection.books.append(book)
            db.session.commit()
            flash(f'Книга «{book.title}» добавлена в подборку «{collection.name}»!', 'success')
        else:
            flash('Эта книга уже есть в выбранной подборке.', 'info')
    except Exception as e:
        db.session.rollback()
        flash('Ошибка при добавлении книги в подборку.', 'danger')

    return redirect(url_for('books.view', book_id=book_id))
