from loki.api.attacks.models import PyTorchAttack
from loki.api.attacks.models import attacks as set_attacks

from loki.api.classifiers.models import pretrained_classifiers

from PIL import Image

from flask_restx import Namespace, Resource, reqparse

import base64
import io


api = Namespace('attacks', description='Operations on adversarial attacks')


@api.route('/')
class AttackList(Resource):
    @api.doc('Get a list of the names of all attacks.')
    def get(self):
        return [
            {
                "name": attack["name"],
                "paper": attack["paper"]
            } for attack in set_attacks
        ]


@api.route('/<attack_id>')
@api.param('attack_id', 'The attack identifier')
@api.response(200, 'Success: Attack found')
@api.response(404, 'Error: Attack not found')
class Attack(Resource):
    @api.doc('Get an attack from its id.')
    def get(self, attack_id):
        try:
            return {
                "name": set_attacks[int(attack_id)]["name"],
                "paper": set_attacks[int(attack_id)]["paper"]
            }
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
        """Run an attack given classifier_id, image_data, and attack_id.

        Parameters
        ----------
        image_data: [string]
            Base64-encoded image.
        attack_id:  [int]
        classifier_id: [int]

        Returns
        -------
        [image_data]
            Base64-encoded image.
        """
        args = parser.parse_args()
        im_b64 = args['image_data']
        im_binary = base64.b64decode(im_b64)

        buf = io.BytesIO(im_binary)
        img = Image.open(buf)

        classifier_id = args['classifier_id']
        attack_id = args['attack_id']

        result_image = run_attack(img, classifier_id, attack_id)

        im_file = io.BytesIO()
        result_image.save(im_file, format="JPEG")
        im_bytes = im_file.getvalue()

        return {"image_data": base64.b64encode(im_bytes).decode()}


def run_attack(image, classifier_id, attack_id):
    """Run an attack.

    Parameters
    ----------
    image : [PIL Image]
        Some input image.
    classifier_id : [int]
        Classifier identifier in pretrained_classifiers.
    attack_id : [int]
        Attack identifier in set_attacks.

    Returns
    -------
    [PIL Image]
        Image after applying the attack to it.
    """
    classifier = pretrained_classifiers[int(classifier_id)][1]

    # result = classifier.predict(img, n=1)[0][1]
    label_index = classifier.predict(image, n=1)[0][0].item()
    label = classifier.prep_label(label_index)

    attack = PyTorchAttack(classifier.model,
                           set_attacks[int(attack_id)]["attack"])

    adv = attack.run(classifier.prep_tensor(image,
                                            normalize=False),
                     labels=label)
    result_image = PyTorchAttack.get_image(images=adv,
                                           scale=3.5)

    return result_image
