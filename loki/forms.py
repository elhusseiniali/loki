from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from wtforms.validators import ValidationError

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
    
class ModelSelectField(SelectField):
	def __init__(self, *args, **kwargs):
		super(ModelSelectField, self).__init__(*args, **kwargs)
		models = FRS.query.filter_by(user=current_user).order_by(FRS.upload_date.desc())
		self.choices = [(model.id, model.name) for model in models]

class ReportForm(FlaskForm):
	#List of available attacks
	model = ModelSelectField(label='Choose your model !')
	attack1 = BooleanField(label='VirtualAdversarialAttack')
	attack2 = BooleanField(label='VirtualAdversarialAttack2')
	attack3 = BooleanField(label='VirtualAdversarialAttack3')
	attack4 = BooleanField(label='VirtualAdversarialAttack4')
	attack5 = BooleanField(label='VirtualAdversarialAttack5')
	attack6 = BooleanField(label='VirtualAdversarialAttack6')
	attack7 = BooleanField(label='VirtualAdversarialAttack7')
	submit = SubmitField('Launch new report')
			

    
class FRSForm(FlaskForm):
	name = StringField('Name for the model', validators=[DataRequired(),Length(min=2, max=15)])
	model = FileField('Upload a model', validators = [FileAllowed(['h5', 'pb']), FileRequired()])
	submit = SubmitField('Submit')