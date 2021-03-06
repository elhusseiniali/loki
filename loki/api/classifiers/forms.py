from loki.models import User, Classifier

from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, StringField
from wtforms.validators import DataRequired, Length

from flask_wtf.file import FileField, FileAllowed, FileRequired

from flask_login import current_user

from loki.api.classifiers.models import pretrained_classifiers


class ClassifierField(SelectField):
    """Set options in the model selector to all classifiers.
    """
    def __init__(self, *args, **kwargs):
        super(ClassifierField, self).__init__(*args, **kwargs)
        # For user_model support, just uncomment the two next lines
        # and comment the third; this would require some
        # extra work in api/classifiers/models
        # user_models = Classifier.query.filter_by(user=current_user). \
        #    order_by(Classifier.upload_date.desc())
        user_models = None

        pretrained_choices = [(i, item.name)
                              for i, item in enumerate(pretrained_classifiers)]
        pretrained_choices.reverse()
        offset = len(pretrained_choices)

        if not user_models:
            # user_choices = [(user_models.count() + offset, 'None')]
            user_choices = []
        else:
            user_choices = [(model.id + offset - 1,
                             model.name) for model in user_models]

        self.choices = user_choices + pretrained_choices


class PredictForm(FlaskForm):
    model = ClassifierField()
    image = FileField('Upload an image.',
                      validators=[FileAllowed(['jpg', 'jpeg', 'png']),
                                  FileRequired()])
    submit = SubmitField('Classify image')


class UploadClassifierForm(FlaskForm):
    name = StringField('Name for the model',
                       validators=[DataRequired(),
                                   Length(min=2, max=15)])
    model = FileField('Upload a model',
                      validators=[FileAllowed(['h5', 'pb', 'pickle']),
                                  FileRequired()])
    submit = SubmitField('Submit')
