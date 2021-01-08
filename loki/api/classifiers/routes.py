from flask import (Blueprint,
                   render_template, flash, url_for,
                   abort, redirect,
                   send_file)

from loki import db

from flask_login import login_required, current_user
from PIL import Image

from loki.api.classifiers.models import pretrained_classifiers
from loki.api.classifiers.forms import PredictForm, UploadClassifierForm
from loki.api.classifiers.utils import save_model, remove_model

from loki.utils import save_image

from loki.models import Classifier, Report

from flask_restx import Namespace, Resource, reqparse

import base64
import io


classifiers = Blueprint('classifiers', __name__)
api = Namespace('classifiers', description='All operations on classifiers.')


@api.route('/all')
class ClassifierList(Resource):
    @api.doc('Get a list of the names of all the available classifiers.')
    def get(self):
        return [
            {
                "name": classifier["name"],
                "paper": classifier["paper"]
            } for classifier in pretrained_classifiers
        ]


@api.route('/<classifier_id>')
@api.param('classifier_id', 'Classifier identifier')
@api.response(200, 'Success: Classifier found')
@api.response(404, 'Error: Classifier not found')
class ClassifierID(Resource):
    def get(self, classifier_id):
        try:
            return pretrained_classifiers[int(classifier_id)]["name"]
        except Exception:
            api.abort(404)


parser = reqparse.RequestParser()
parser.add_argument('image_data', required=True)
parser.add_argument('classifier_id')


@api.route('/classify')
class Classify(Resource):
    @api.expect(parser)
    def put(self):
        args = parser.parse_args()
        im_b64 = args['image_data']
        im_binary = base64.b64decode(im_b64)

        buf = io.BytesIO(im_binary)
        img = Image.open(buf)

        classifier_id = args['classifier_id']
        label = predict(img, classifier_id)

        return [{"index": elem[0].item(),
                 "label": elem[1],
                 "percentage": elem[2]} for elem in label]


def predict(image, classifier_index):
    classifier = pretrained_classifiers[int(classifier_index)]["classifier"]
    return classifier.predict(image)


@classifiers.route("/classifiers/classify",
                   methods=['POST', 'GET'])
@login_required
def form_predict():
    form = PredictForm()

    if form.validate_on_submit():
        index = int(form.model.data) - 1

        image_file = save_image(form.image.data, path="tmp")
        path = url_for('static',
                       filename=f"tmp/"
                                f"{image_file}")

        img = Image.open(f"./loki/{path}")
        label = predict(img, int(form.model.data))

        flash("Done!", 'success')

        return render_template('predict.html',
                               title='Classify an image.',
                               image_file=image_file, form=form,
                               label=label, index=index)
    return render_template('predict.html',
                           title='Classify an image.', form=form)


@classifiers.route("/classifiers/upload",
                   methods=['GET', 'POST'])
@login_required
def upload_model():
    """Upload a model.
    This automatically populates the User-Model relationship.
    """
    form = UploadClassifierForm()
    if form.validate_on_submit():
        model_path = save_model(form.model.data)
        classifier = Classifier(name=form.name.data, file_path=model_path,
                                user=current_user)
        db.session.add(classifier)
        db.session.commit()
        flash('Model uploaded! You can now analyze it!', 'success')
        return redirect(url_for('users.account'))

    return render_template('upload_model.html',
                           title='Upload Model',
                           form=form)


@classifiers.route("/classifiers/<int:model_id>")
@login_required
def get_model(model_id):
    model = Classifier.query.get_or_404(model_id)
    reports = Report.query.filter_by(model=model)
    return render_template('model.html', title=model.name,
                           model=model, reports=reports)


@classifiers.route("/classifiers/delete/<int:model_id>", methods=['POST'])
@login_required
def delete_model(model_id):
    model = Classifier.query.get_or_404(model_id)
    if model.user != current_user:
        abort(403)  # forbidden route
    remove_model(model.file_path)
    db.session.delete(model)
    db.session.commit()
    flash('Your model has been deleted!', 'success')
    return redirect(url_for('users.account'))


@classifiers.route('/classifiers/download/<int:model_id>',
                   methods=['GET', 'POST'])
@login_required
def download_model(model_id):
    model = Classifier.query.get_or_404(model_id)
    filepath = model.file_path
    return send_file(filepath, as_attachment=True,
                     attachment_filename=f'{model.name}.h5')
