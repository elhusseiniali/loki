from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired

from wtforms import StringField, PasswordField, SubmitField, \
                                 BooleanField, RadioField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from wtforms.validators import ValidationError

from flask_login import current_user

from loki.models import User, FRS


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


class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(),
                                       Length(min=2, max=15)])
    email = StringField('Email',
                        validators=[DataRequired(),
                                    Email()])
    image = FileField('Update Profile Picture',
                      validators=[FileAllowed(['jpg', 'jpeg', 'png'])])

    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username already taken!')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Account with email already exists!')


class FRSForm(FlaskForm):
    name = StringField('Name for the model',
                       validators=[DataRequired(),
                                   Length(min=2, max=15)])
    model = FileField('Upload a model',
                      validators=[FileAllowed(['h5', 'pb', '.pickle']),
                                  FileRequired()])
    submit = SubmitField('Submit')


class DisplayAttackForm(FlaskForm):
    attacks = RadioField('Attacks', coerce=bool,
                         choices=[('attack1', 'attack1'),
                                  ('attack2', 'attack2'),
                                  ('attack3', 'attack3'),
                                  ('attack4', 'attack4'),
                                  ('attack5', 'attack5'),
                                  ('attack6', 'attack6')])
    image = FileField('Upload the image to attack',
                      validators=[FileAllowed(['jpg', 'jpeg', 'png']),
                                  FileRequired()])
    submit = SubmitField('Launch the attack !')
