from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired

from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms import BooleanField, RadioField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from wtforms.validators import ValidationError

from flask_login import current_user

from loki.models import User, Classifier

from loki.classifiers import pretrained_classifiers
from loki.attacks import attacks as set_attacks


class EmailField(StringField):
    email = StringField('Email',
                        validators=[DataRequired(),
                                    Email()])


class ClassifierField(SelectField):
    """Set options in the model selector to all classifiers.
    """
    def __init__(self, *args, **kwargs):
        super(ClassifierField, self).__init__(*args, **kwargs)
        user_models = Classifier.query.filter_by(user=current_user). \
            order_by(Classifier.upload_date.desc())

        pretrained_choices = [(i, item[0])
                              for i, item in enumerate(pretrained_classifiers)]

        offset = len(pretrained_choices)

        if not user_models:
            user_choices = [(user_models.count() + offset, 'None')]
        else:
            user_choices = [(model.id + offset - 1,
                             model.name) for model in user_models]

        self.choices = user_choices + pretrained_choices


class AttackField(RadioField):
    def __init__(self, *args, **kwargs):
        super(AttackField, self).__init__(*args, **kwargs)
        self.choices = [(i, item[0])
                        for i, item in enumerate(set_attacks)]


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(),
                                       Length(min=2, max=15)])
    email = EmailField()
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
    email = EmailField()
    password = PasswordField('Password',
                             validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Log in')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(),
                                       Length(min=2, max=15)])
    email = EmailField()
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


class UploadClassifierForm(FlaskForm):
    name = StringField('Name for the model',
                       validators=[DataRequired(),
                                   Length(min=2, max=15)])
    model = FileField('Upload a model',
                      validators=[FileAllowed(['h5', 'pb', '.pickle']),
                                  FileRequired()])
    submit = SubmitField('Submit')


class VisualizeAttackForm(FlaskForm):
    model = ClassifierField(label="Select a model")
    attacks = AttackField(label="Select attack(s)")
    image = FileField('Upload an image',
                      id='image',
                      validators=[FileAllowed(['jpg', 'jpeg', 'png']),
                                  FileRequired()])
    classify = BooleanField('Classify image')
    submit = SubmitField('Visualize attack')


class PredictForm(FlaskForm):
    model = ClassifierField()
    image = FileField('Upload an image.',
                      validators=[FileAllowed(['jpg', 'jpeg', 'png']),
                                  FileRequired()])
    submit = SubmitField('Classify image')
