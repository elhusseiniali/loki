from flask import Blueprint, flash, render_template
from flask_login import login_required

from loki.api.attacks.forms import VisualizeAttackForm
from loki.api.attacks.models import PyTorchAttack
from loki.api.attacks.models import attacks as set_attacks

from loki.api.classifiers.models import pretrained_classifiers

from loki.utils import save_image

from PIL import Image

from flask_restx import Namespace, Resource, reqparse

import base64
import io


attacks = Blueprint('attacks', __name__)
api = Namespace('attacks', description='Operations on adversarial attacks')


@api.route('/')
class AttackList(Resource):
    @api.doc('Get a list of the names of all attacks.')
    def get(self):
        return [attack[0] for attack in set_attacks]


@api.route('/<attack_id>')
@api.param('attack_id', 'The attack identifier')
@api.response(200, 'Success: Attack found')
@api.response(404, 'Error: Attack not found')
class Attack(Resource):
    @api.doc('Get an attack from its id.')
    def get(self, attack_id):
        try:
            return set_attacks[int(attack_id)][0]
        except Exception:
            api.abort(404)


parser = reqparse.RequestParser()
parser.add_argument('image_data', required=True)
parser.add_argument('attack_id')
parser.add_argument('classifier_id')


@api.route('/run/')
class RunAttack(Resource):
    @api.expect(parser)
    def put(self):
        args = parser.parse_args()
        im_b64 = args['image_data']
        im_binary = base64.b64decode(im_b64)

        buf = io.BytesIO(im_binary)
        img = Image.open(buf)

        classifier_id = args['classifier_id']
        attack_id = args['attack_id']

        result_image = run_attack(img, classifier_id, attack_id)
        end = save_image(result_image, path="tmp")
        return str(type(end))


@attacks.route("/attacks/visualize",
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
        flash("Attack successully run!", 'success')

        return render_template('visualize_attack.html', form=form,
                               image_file=image_file, result_file=result_file,
                               index=index)
    return render_template('visualize_attack.html', form=form)


def run_attack(image, classifier_id, attack_id):
    classifier = pretrained_classifiers[int(classifier_id)][1]

    # result = classifier.predict(img, n=1)[0][1]
    label_index = classifier.predict(image, n=1)[0][0].item()
    label = classifier.prep_label(label_index)

    attack = PyTorchAttack(classifier.model,
                           set_attacks[int(attack_id)][1])

    adv = attack.run(classifier.prep_tensor(image,
                                            normalize=False),
                     labels=label)
    result_image = PyTorchAttack.get_image(images=adv,
                                           scale=3.5)

    return result_image
