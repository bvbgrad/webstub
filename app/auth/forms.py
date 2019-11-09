from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, RadioField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

from app.models import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
# todo remember me OBE?
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    admin_type = RadioField('Account Type', default='none',
            choices=[('none', 'User'), ('admin', 'Administrator')])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Submit')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username already exists.')

    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email is not None:
            raise ValidationError('Email address already being used.')


class EditRegistrationForm(FlaskForm):
    username = StringField('Username')
    email = StringField('Email', validators=[Email()])
    admin_type = RadioField('Account Type', default='none',
            choices=[('none', 'User'), ('admin', 'Administrator')])
    password = PasswordField('Password')
    password2 = PasswordField(
        'Repeat Password', validators=[EqualTo('password')])
    submit = SubmitField('Submit')


class DeleteAccountForm(FlaskForm):
    response = RadioField(default='no', choices=[('yes', 'Yes'), ('no', 'No')])
    submit = SubmitField('Confirm')
