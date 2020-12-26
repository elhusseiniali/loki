from flask_wtf import FlaskForm
from wtforms import RadioField, BooleanField, SubmitField
from flask_wtf.file import FileField, FileAllowed, FileRequired


from loki.attacks.models import attacks as set_attacks
from loki.classifiers.forms import ClassifierField


class AttackField(RadioField):
    """A field for attacks to be used in any WTForm.
    """
    def __init__(self, *args, **kwargs):
        super(AttackField, self).__init__(*args, **kwargs)
        self.choices = [(i, item[0])
                        for i, item in enumerate(set_attacks)]


class VisualizeAttackForm(FlaskForm):
    model = ClassifierField(label="Select a model")
    attacks = AttackField(label="Select attack(s)")
    image = FileField('Upload an image',
                      id='image',
                      validators=[FileAllowed(['jpg', 'jpeg', 'png']),
                                  FileRequired()])
    classify = BooleanField('Classify image')
    submit = SubmitField('Visualize attack')
