from flask import Blueprint, render_template, request
from models import Book
from flask import current_app

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BOOKS_PER_PAGE']

    pagination = Book.query.order_by(Book.year.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    books = pagination.items

    return render_template('main/index.html', books=books, pagination=pagination)
