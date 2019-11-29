from flask import current_app, render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse

from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, EditRegistrationForm, DeleteAccountForm
from app.models import User


@bp.route('/admin')
@login_required
def admin():
    if current_user.admin_type != "admin":
        return redirect(url_for('main.index'))
    current_app.logger.info('admin page')
    registered_users = User.query.all()
    return render_template('auth/admin.html', users=registered_users)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    current_app.logger.info('login')

    if current_user.is_authenticated:
        current_app.logger.info('login valid user')
        return redirect(url_for('main.index'))
    current_app.logger.info('login not logged in')
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html', title='Sign In', form=form)


@bp.route('/logout')
def logout():
    current_app.logger.info('logout')
    logout_user()
    return redirect(url_for('auth.login'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    current_app.logger.info('Register')
    # Create a default admin user if User table is empty
    registered_users = len(User.query.all())
    current_app.logger.info('There are {} registered users'.format(registered_users))
    if registered_users == 0:
        admin_user = User("admin", "admin@e.com", "admin")
        admin_user.set_password("admin")
        db.session.add(admin_user)
        db.session.commit()
        current_app.logger.info('Default admin user created')

    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, admin_type=form.admin_type.data)
        if not user.admin_type:
            user.admin_type = "none"
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Register', form=form)


@bp.route('/edit_registration', methods=['GET', 'POST'])
@login_required
def edit_registration():
    user_id = request.args.get("line")
    current_app.logger.info('edit registration information for user_id {}'.format(user_id))
    user = User.query.filter_by(id=user_id).first_or_404()
    current_app.logger.info('edit registration for {}'.format(user))

    form = EditRegistrationForm()
    if form.validate_on_submit():
        # todo need to prevent selection of an existing username, ugly constraint error
        if user.username != form.username.data:
            user.username = form.username.data
        if user.email != form.email.data:
            user.email = form.email.data
        if user.admin_type != form.admin_type.data:
            if form.admin_type.data is None:
                user.admin_type = "none"
            else:
                user.admin_type = form.admin_type.data
        if form.password.data != "":
            user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        current_app.logger.info('Updated User {} to {}'.format(user_id, user))

        flash('User profile has been updated')
        return redirect(url_for('auth.admin'))
    elif request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email
        # todo figure out how to pre-fill admin_type radio button
        # ??? setattr(form, attr, attr_value) ???
        # form.admin_type = user.admin_type

    current_app.logger.info('Edit User {} {}'.format(user_id, user))
    form_title = "Edit < {} >".format(user.username)
    return render_template('auth/edit_registration.html', title=form_title, user=user, form=form)


@bp.route('/delete_account', methods=['GET', 'POST'])
@login_required
def delete_account():
    # todo created new account, first time delete -> selected wrong line (not repeatable)
    # todo prevent deletion of current user account?
    if current_user.admin_type != "admin":
        return redirect(url_for('main.index'))
    user_id = request.args.get("line")
    user = User.query.filter_by(id=user_id).first_or_404()

    form = DeleteAccountForm()
    if form.validate_on_submit():
        if form.response.data == "yes":
            db.session.delete(user)
            db.session.commit()
            flash('Account <{}> has been deleted!'.format(user.username))
            current_app.logger.info('User Account {} {} deleted'.format(user_id, user))
        else:
            flash('Delete action canceled')
        return redirect(url_for('auth.admin'))
    return render_template('auth/delete_account.html', user=user, form=form)


@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('auth/user.html', user=user, posts=posts)
