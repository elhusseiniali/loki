from flask import Blueprint, flash, render_template
from flask_login import login_required
from loki.api.attacks.forms import VisualizeAttackForm

from loki.utils import save_image
from PIL import Image

from loki.api.attacks.routes import run_attack
from loki.api.classifiers.routes import predict
import requests
import base64
import json

attack_views = Blueprint('attack_views', __name__)


@attack_views.route("/attacks/visualize",
                    methods=['POST', 'GET'])
@login_required
def visualize_attack():
    """Run selected attack on uploaded image.
    """
    form = VisualizeAttackForm()
    if form.validate_on_submit():
        index = int(form.model.data) - 1

        img = Image.open(form.image.data)

        classifier_id = int(form.model.data)
        attack_id = int(form.attacks.data)

        image_file = save_image(form.image.data, path="tmp",
                                output_size=(400, 400))

        result_image = run_attack(img, classifier_id, attack_id)
        result_file = save_image(result_image, path="tmp",
                                 output_size=(400, 400))

        preds = []
        if form.classify.data:
            label_before = predict(img, classifier_id)
            label_after = predict(result_image, classifier_id)

            preds.append(label_before)
            preds.append(label_after)

        flash("Attack successully run!", 'success')

        return render_template('visualize_attack.html', form=form,
                               image_file=image_file, result_file=result_file,
                               index=index, preds=preds)
    return render_template('visualize_attack.html', form=form)
