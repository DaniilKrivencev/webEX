import os
import hashlib
import bleach
from flask import (
    Blueprint, render_template, redirect, url_for,
    flash, request, current_app, send_from_directory
)
from flask_login import current_user
from functools import wraps
from models import Book, Genre, Cover, db

books_bp = Blueprint('books', __name__)

SAFE_TAGS = [
    'p', 'br', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'pre', 'code', 'blockquote', 'ul', 'ol', 'li',
    'strong', 'em', 'b', 'i', 'a', 'table', 'thead',
    'tbody', 'tr', 'th', 'td', 'hr', 'del', 'sup', 'sub',
]


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Для выполнения данного действия необходимо пройти процедуру аутентификации', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        if not current_user.is_admin:
            flash('У вас недостаточно прав для выполнения данного действия', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated


def moderator_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Для выполнения данного действия необходимо пройти процедуру аутентификации', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        if not (current_user.is_admin or current_user.is_moderator):
            flash('У вас недостаточно прав для выполнения данного действия', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated


def sanitize_md(text):
    """Strip all HTML from raw markdown input before storing."""
    return bleach.clean(str(text), tags=[], strip=True).strip()


def get_cover_ext(filename):
    ext = os.path.splitext(filename or '')[1].lower()
    return ext if ext in ('.jpg', '.jpeg', '.png', '.gif', '.webp') else '.jpg'


@books_bp.route('/covers/<filename>')
def serve_cover(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)


@books_bp.route('/<int:book_id>')
def view(book_id):
    book = db.get_or_404(Book, book_id)

    user_review = None
    if current_user.is_authenticated:
        from models import Review
        user_review = Review.query.filter_by(
            book_id=book_id, user_id=current_user.id
        ).first()

    user_collections = []
    if current_user.is_authenticated and current_user.is_user:
        from models import Collection
        user_collections = Collection.query.filter_by(user_id=current_user.id).all()

    return render_template('books/view.html',
                           book=book,
                           user_review=user_review,
                           user_collections=user_collections)


@books_bp.route('/add', methods=['GET', 'POST'])
@admin_required
def add():
    genres = Genre.query.order_by(Genre.name).all()

    if request.method == 'POST':
        title       = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        year        = request.form.get('year', type=int)
        publisher   = request.form.get('publisher', '').strip()
        author      = request.form.get('author', '').strip()
        pages       = request.form.get('pages', type=int)
        genre_ids   = request.form.getlist('genres')
        cover_file  = request.files.get('cover')

        def _fail(msg=None):
            flash(msg or 'При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')
            return render_template('books/add.html', genres=genres,
                                   selected_genre_ids=genre_ids,
                                   form_data=request.form)

        if not all([title, description, year, publisher, author, pages, genre_ids]):
            return _fail()
        if not cover_file or not cover_file.filename:
            return _fail('Необходимо загрузить обложку книги.')

        # Read file bytes now before any DB operations
        file_bytes = cover_file.read()
        if not file_bytes:
            return _fail('Файл обложки пустой.')

        file_md5  = hashlib.md5(file_bytes).hexdigest()
        mime_type = cover_file.content_type or 'image/jpeg'
        ext       = get_cover_ext(cover_file.filename)

        try:
            book = Book(
                title=sanitize_md(title),
                description=sanitize_md(description),
                year=year,
                publisher=sanitize_md(publisher),
                author=sanitize_md(author),
                pages=pages,
            )
            for gid in genre_ids:
                g = db.session.get(Genre, int(gid))
                if g:
                    book.genres.append(g)

            db.session.add(book)
            db.session.flush()  # get book.id

            # MD5 dedup: check if this file is already stored
            existing = Cover.query.filter_by(md5_hash=file_md5).first()
            if existing:
                # Reuse the same file on disk; create a new Cover row for this book
                cover = Cover(
                    filename=existing.filename,
                    mime_type=existing.mime_type,
                    md5_hash=file_md5 + f'_{book.id}',  # unique key trick
                    book_id=book.id,
                )
                save_to_disk = False
            else:
                cover = Cover(
                    filename='',          # set after flush
                    mime_type=mime_type,
                    md5_hash=file_md5,
                    book_id=book.id,
                )
                db.session.add(cover)
                db.session.flush()
                cover.filename = f"{cover.id}{ext}"
                save_to_disk = True

            db.session.add(cover)
            db.session.commit()

            # Write file AFTER commit (safer)
            if save_to_disk:
                fpath = os.path.join(current_app.config['UPLOAD_FOLDER'], cover.filename)
                with open(fpath, 'wb') as fh:
                    fh.write(file_bytes)

            flash(f'Книга «{book.title}» успешно добавлена!', 'success')
            return redirect(url_for('books.view', book_id=book.id))

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'add book error: {e}')
            return _fail()

    return render_template('books/add.html', genres=genres,
                           selected_genre_ids=[], form_data={})


@books_bp.route('/<int:book_id>/edit', methods=['GET', 'POST'])
@moderator_required
def edit(book_id):
    book   = db.get_or_404(Book, book_id)
    genres = Genre.query.order_by(Genre.name).all()

    if request.method == 'POST':
        title       = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        year        = request.form.get('year', type=int)
        publisher   = request.form.get('publisher', '').strip()
        author      = request.form.get('author', '').strip()
        pages       = request.form.get('pages', type=int)
        genre_ids   = request.form.getlist('genres')

        def _fail():
            flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')
            return render_template('books/edit.html', book=book, genres=genres,
                                   selected_genre_ids=genre_ids,
                                   form_data=request.form)

        if not all([title, description, year, publisher, author, pages, genre_ids]):
            return _fail()

        try:
            book.title       = sanitize_md(title)
            book.description = sanitize_md(description)
            book.year        = year
            book.publisher   = sanitize_md(publisher)
            book.author      = sanitize_md(author)
            book.pages       = pages

            book.genres.clear()
            for gid in genre_ids:
                g = db.session.get(Genre, int(gid))
                if g:
                    book.genres.append(g)

            db.session.commit()
            flash(f'Книга «{book.title}» успешно обновлена!', 'success')
            return redirect(url_for('books.view', book_id=book.id))

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'edit book error: {e}')
            return _fail()

    selected_genre_ids = [str(g.id) for g in book.genres]
    return render_template('books/edit.html', book=book, genres=genres,
                           selected_genre_ids=selected_genre_ids, form_data={})


@books_bp.route('/<int:book_id>/delete', methods=['POST'])
@admin_required
def delete(book_id):
    book  = db.get_or_404(Book, book_id)
    title = book.title

    try:
        if book.cover:
            filename = book.cover.filename
            # Only delete file if no other cover row uses the same filename
            others = Cover.query.filter(
                Cover.filename == filename,
                Cover.id != book.cover.id
            ).count()
            if others == 0:
                fpath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                if os.path.exists(fpath):
                    os.remove(fpath)

        db.session.delete(book)
        db.session.commit()
        flash(f'Книга «{title}» успешно удалена!', 'success')

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'delete book error: {e}')
        flash('Ошибка при удалении книги.', 'danger')

    return redirect(url_for('main.index'))
