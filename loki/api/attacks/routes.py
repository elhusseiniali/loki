from flask import Blueprint, flash, render_template
from flask_login import login_required

from loki.api.attacks.forms import VisualizeAttackForm
from loki.api.attacks.models import PyTorchAttack
from loki.api.attacks.models import attacks as set_attacks

from loki.api.classifiers.models import pretrained_classifiers

from loki.utils import save_image

from PIL import Image


attacks = Blueprint('attacks', __name__)


@attacks.route("/attacks/visualize",
               methods=['POST', 'GET'])
@login_required
def visualize_attack():
    """Run selected attack on uploaded image.
    """
    form = VisualizeAttackForm()
    if form.validate_on_submit():
        index = int(form.model.data) - 1
        classifier = pretrained_classifiers[int(form.model.data)][1]

        img = Image.open(form.image.data)
        label_index = classifier.predict(img, n=1)[0][0].item()
        label = classifier.prep_label(label_index)

        attack = PyTorchAttack(classifier.model,
                               set_attacks[int(form.attacks.data)][1])

        adv = attack.run(classifier.prep_tensor(img,
                                                normalize=False),
                         labels=label)
        result_image = PyTorchAttack.get_image(images=adv,
                                               scale=3.5)

        image_file = save_image(form.image.data, path="tmp",
                                output_size=(400, 400))
        result_file = save_image(result_image, path="tmp",
                                 output_size=(400, 400))
        flash("Attack successully run!", 'success')

        return render_template('visualize_attack.html', form=form,
                               image_file=image_file, result_file=result_file,
                               index=index)
    return render_template('visualize_attack.html', form=form)
