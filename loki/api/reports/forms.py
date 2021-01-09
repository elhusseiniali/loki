from flask_wtf import FlaskForm
from wtforms import SubmitField
from loki.api.classifiers.forms import ClassifierField
from loki.api.attacks.forms import AttackField
from flask_wtf.file import FileAllowed
from wtforms import MultipleFileField


class ReportForm(FlaskForm):
    model = ClassifierField('Select the model for the report')
    images = MultipleFileField('Select Images',
                               validators=[FileAllowed(['jpg', 'jpeg'])])
    attacks = AttackField(label="Select attack(s)")
    submit = SubmitField('Launch new report')
