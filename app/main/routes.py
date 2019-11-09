from flask import render_template, current_app
from flask_login import current_user, login_required

from app.main import bp


@bp.route('/')
@bp.route('/index')
@login_required
def index():
    current_app.logger.info('index')
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]

    return render_template('main/index.html', admin_type=current_user.admin_type,  posts=posts)
