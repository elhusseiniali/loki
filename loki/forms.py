from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired

from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms import BooleanField, RadioField
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


class ModelSelectField(SelectField):
    """Set options in the model selector to all user-uploaded models.

    TODO
    ----
    -   Add all pre-trained models (currently only InceptionResnetV1).
    """
    def __init__(self, *args, **kwargs):
        super(ModelSelectField, self).__init__(*args, **kwargs)
        models = FRS.query.filter_by(user=current_user). \
            order_by(FRS.upload_date.desc())
        self.choices = [(models.count() + 1, 'None')] + \
            [(model.id, model.name) for model in models]


class VisualizeAttackForm(FlaskForm):
    model = ModelSelectField(label='Select a model.')
    attacks = RadioField('Attacks',
                         choices=[('attack1', 'attack1'),
                                  ('attack2', 'attack2'),
                                  ('attack3', 'attack3'),
                                  ('attack4', 'attack4'),
                                  ('attack5', 'attack5'),
                                  ('attack6', 'attack6')])
    image = FileField('Upload an image.',
                      id='image',
                      validators=[FileAllowed(['jpg', 'jpeg', 'png']),
                                  FileRequired()])
    classify = BooleanField('Add Classifications')
    submit = SubmitField('Visualize attack')


class PredictForm(FlaskForm):
    model = SelectField(label='Select a model.',
                        choices=[('1', 'Inception'),
                                 ('2', 'ResNet'),
                                 ('3', 'Model3')])
    image = FileField('Upload an image.',
                      validators=[FileAllowed(['jpg', 'jpeg', 'png']),
                                  FileRequired()])
    submit = SubmitField('Classify image')
