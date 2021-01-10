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
import numpy as np

from loki import MAX_WIDTH, MAX_HEIGHT

attack_views = Blueprint('attack_views', __name__)


@attack_views.route("/attacks/visualize",
                    methods=['POST', 'GET'])
@login_required
def visualize_attack():
    """Run selected attack on uploaded image.
    """
    form = VisualizeAttackForm()
    if form.validate_on_submit():
        index_model = int(form.model.data)
        index_attack = int(form.attacks.data)
        img = Image.open(form.image.data)

        width, height = img.size

        classifier_id = int(form.model.data)
        attack_id = int(form.attacks.data)

        ratio = min(MAX_WIDTH / 100, MAX_HEIGHT / 100)

        (original_image,
         result_image,
         _, _, _) = run_attack(img, classifier_id,
                               attack_id, scale=ratio)

        result_file = save_image(result_image, path="tmp",
                                 output_size=(MAX_WIDTH, MAX_HEIGHT))
        original_file = save_image(original_image, path="tmp",
                                   output_size=(MAX_WIDTH, MAX_HEIGHT))

        # Get predictions before and after running
        # the attack
        preds = []
        probs = []
        size = 5  # top 5 predictions
        if form.classify.data:
            _, original_label = predict(img, classifier_id)
            _, result_label = predict(result_image, classifier_id)

            preds.append([original_label[i][1] for i in range(size)])
            preds.append([result_label[i][1] for i in range(size)])
            probs.append([np.round(original_label[i][2] / 100, 4)
                         for i in range(size)])
            probs.append([np.round(result_label[i][2] / 100, 4)
                         for i in range(size)])

        flash("Attack successully run!",
              'success')

        return render_template('visualize_attack.html', form=form,
                               image_file=original_file,
                               result_file=result_file,
                               index_model=index_model,
                               index_attack=index_attack,
                               preds=preds,
                               probs=probs, size=size)
    return render_template('visualize_attack.html', form=form)
