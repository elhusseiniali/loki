from flask_wtf import FlaskForm
from wtforms import SubmitField
from loki.api.classifiers.forms import ClassifierField
from loki.api.attacks.forms import AttackField


class ReportForm(FlaskForm):
    model = ClassifierField('Select the model for the report')
    attacks = AttackField(label="Select attack(s)")
    submit = SubmitField('Launch new report')
