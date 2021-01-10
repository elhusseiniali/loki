from flask import (Blueprint,
                   render_template, flash, url_for,
                   abort, redirect,
                   send_file)
from loki import db

from flask_login import login_required, current_user

from loki.api.classifiers.forms import PredictForm, UploadClassifierForm
from loki.api.classifiers.utils import save_model, remove_model

from loki.utils import save_image

from loki.models import Classifier, Report
from PIL import Image

from loki.api.classifiers.routes import predict
from loki import MAX_WIDTH, MAX_HEIGHT


classifiers = Blueprint('classifiers', __name__)


@classifiers.route("/classifiers/classify",
                   methods=['POST', 'GET'])
@login_required
def form_predict():
    form = PredictForm()

    if form.validate_on_submit():
        index_model = int(form.model.data)

        img = Image.open(form.image.data)
        width, height = img.size

        ratio = min(MAX_WIDTH / 100, MAX_HEIGHT / 100)

        image, label = predict(img, int(form.model.data), scale=ratio)
        image_file = save_image(image, path="tmp",
                                output_size=(MAX_WIDTH, MAX_HEIGHT))

        flash("Done!", 'success')

        return render_template('predict.html',
                               title='Classify an image.',
                               image_file=image_file, form=form,
                               label=label, index_model=index_model)
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
