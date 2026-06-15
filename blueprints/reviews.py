import bleach
from flask import (
    Blueprint, render_template, redirect, url_for,
    flash, request
)
from flask_login import login_required, current_user
from models import Review, Book, db

reviews_bp = Blueprint('reviews', __name__)

RATING_CHOICES = [
    (5, 'Отлично'),
    (4, 'Хорошо'),
    (3, 'Удовлетворительно'),
    (2, 'Неудовлетворительно'),
    (1, 'Плохо'),
    (0, 'Ужасно'),
]


def sanitize_md(text):
    """Strip all HTML tags from markdown text before storing."""
    return bleach.clean(str(text), tags=[], strip=True).strip()


@reviews_bp.route('/book/<int:book_id>/add', methods=['GET', 'POST'])
@login_required
def add(book_id):
    book = db.get_or_404(Book, book_id)

    # Check if user already reviewed this book
    existing = Review.query.filter_by(
        book_id=book_id, user_id=current_user.id
    ).first()
    if existing:
        flash('Вы уже оставили рецензию на эту книгу.', 'info')
        return redirect(url_for('books.view', book_id=book_id))

    if request.method == 'POST':
        rating   = request.form.get('rating', type=int)
        text_raw = request.form.get('text', '').strip()

        if rating is None or rating not in range(0, 6) or not text_raw:
            flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')
            return render_template('reviews/add.html',
                                   book=book,
                                   rating_choices=RATING_CHOICES,
                                   form_data=request.form)

        # Sanitize: strip HTML injections, store raw markdown
        text_clean = sanitize_md(text_raw)

        try:
            review = Review(
                book_id=book_id,
                user_id=current_user.id,
                rating=rating,
                text=text_clean,
            )
            db.session.add(review)
            db.session.commit()
            flash('Рецензия успешно добавлена!', 'success')
            return redirect(url_for('books.view', book_id=book_id))

        except Exception as e:
            db.session.rollback()
            flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')
            return render_template('reviews/add.html',
                                   book=book,
                                   rating_choices=RATING_CHOICES,
                                   form_data=request.form)

    return render_template('reviews/add.html',
                           book=book,
                           rating_choices=RATING_CHOICES,
                           form_data={})
