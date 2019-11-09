from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse

from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, DeleteAccountForm
from app.models import User


@app.route('/')
@app.route('/index')
@login_required
def index():
    app.logger.info('index')
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

    return render_template('index.html', admin_type=current_user.admin_type,  posts=posts)


@app.route('/admin')
@login_required
def admin():
    if current_user.admin_type != "admin":
        return redirect(url_for('index'))
    app.logger.info('admin page')
    registered_users = User.query.all()
    return render_template('admin.html', users=registered_users)


@app.route('/login', methods=['GET', 'POST'])
def login():
    app.logger.info('login')
    if current_user.is_authenticated:
        app.logger.info('login valid user')
        return redirect(url_for('index'))
    app.logger.info('login not logged in')
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    app.logger.info('logout')
    logout_user()
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    app.logger.info('Register')
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, admin_type=form.admin_type.data)
        if not user.admin_type:
            user.admin_type = "none"
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if current_user.admin_type != "admin":
        return redirect(url_for('index'))
    user_id = request.args.get("line")
    user = User.query.filter_by(id=user_id).first_or_404()

    form = EditProfileForm()
    if form.validate_on_submit():
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
        app.logger.info('Updated User {} to {}'.format(user_id, user))

        flash('User profile has been updated')
        return redirect(url_for('admin'))

    app.logger.info('Edit User {} {}'.format(user_id, user))
    form_title = "Edit < {} >".format(user.username)
    return render_template('edit_profile.html', title=form_title, user=user, form=form)


@app.route('/delete_account', methods=['GET', 'POST'])
@login_required
def delete_account():
    if current_user.admin_type != "admin":
        return redirect(url_for('index'))
    user_id = request.args.get("line")
    user = User.query.filter_by(id=user_id).first_or_404()

    form = DeleteAccountForm()
    if form.validate_on_submit():
        if form.response.data == "yes":
            db.session.delete(user)
            db.session.commit()
            flash('Account <{}> has been deleted!'.format(user.username))
            app.logger.info('User Account {} {} deleted'.format(user_id, user))
        else:
            flash('Delete action canceled')
        return redirect(url_for('admin'))
    return render_template('delete_account.html', user=user, form=form)
