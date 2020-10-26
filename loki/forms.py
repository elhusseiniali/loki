from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from wtforms.validators import ValidationError

from loki.models import User


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(),
                                       Length(min=2, max=15)])
    email = StringField('Email',
                        validators=[DataRequired(),
                                    Email()])
    password = PasswordField('Password',
                             validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(),
                                                 EqualTo('password')])
    submit = SubmitField('Submit')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()

        if user:
            raise ValidationError('Username already exists!')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()

        if user:
            raise ValidationError('Account with email already exists!')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(),
                                    Email()])
    password = PasswordField('Password',
                             validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Log in')

class ModelForm(FlaskForm):
	name = StringField('Name for the model',
                           validators=[DataRequired(),
                                       Length(min=2, max=15)])
	model = FileField('Upload a model', validators = [FileAllowed(['h5', 'pb']), FileRequired()])
	submit = SubmitField('Submit')


class RunReportForm(FlaskForm):
	submit = SubmitField('Run Report')
	
