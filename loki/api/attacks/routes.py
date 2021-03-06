from loki.api.attacks.models import PyTorchAttack
from loki.api.attacks.models import attacks as set_attacks

from loki.api.classifiers.models import pretrained_classifiers
from loki.api.utils import get_image_from_tensor

from PIL import Image

from flask_restx import Namespace, Resource, reqparse

import base64
import io

import numpy as np


api = Namespace('attacks', description='Operations on adversarial attacks')


@api.route('/all')
@api.response('200', 'Success')
class AttackList(Resource):
    """Resource to get a list of all attacks.
    """
    def get(self):
        """Get a list of all the attacks.

        Returns
        -------
        List of JSON, where
            every JSON has the form
            {
                "name": attack name,
                "paper": attack research paper
            }
        """
        return [
            {
                "name": attack["name"],
                "paper": attack["paper"]
            } for attack in set_attacks
        ]


@api.route('/<attack_id>')
@api.param('attack_id', 'The attack identifier')
@api.response('200', 'Success: Attack found')
@api.response('404', 'Error: Attack not found')
@api.response('422', 'Error: Index has to be an integer')
class Attack(Resource):
    """Resource to get information on a specific attack.
    """
    @api.doc('Get an attack from its id.')
    def get(self, attack_id):
        """Get the name of an attack and its research paper.
        IDs start from 0.

        Returns
        -------
        JSON
            with the form
            {
                "name": attack name,
                "paper": attack research paper
            }
        Responses
        ---------
        - 200:
            The attack information was found.
        - 404:
            The ID passed was out of bounds.
        - 422:
            The ID was not an int.
        """
        try:
            return {
                "name": set_attacks[int(attack_id)]["name"],
                "paper": set_attacks[int(attack_id)]["paper"]
            }
        except IndexError:
            api.abort(404)
        except ValueError:
            api.abort(422)


parser = reqparse.RequestParser()
parser.add_argument('image_data', required=True)
parser.add_argument('attack_id', type=int, required=True)
parser.add_argument('classifier_id', type=int, required=True)


@api.route('/run')
@api.response(200, 'Success')
@api.response(404, 'Error: Index out of bounds')
@api.response(422, 'Error: Check parameters')
class RunAttack(Resource):
    """Resource to run an attack.
    """
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
        - original_image: [str]
            Base64-encoded image after it is prepared
            for the classifier, before applying the attack.
        - result_image: [str]
            Base64-encoded image after applying
            the attack.
        - difference_image: [str]
            Base64-encoded image of the pixel difference
            between result_image and original_image.

        Responses
        ---------
        - 200:
            The attack was run.
        - 404:
            One of the IDs passed was out of bounds.
        - 422:
            One of the parameters was wrong. This means
            that something that was not an int was passed as
            one of the IDs, or invalid Base64 data was passed
            for the image.
        """
        args = parser.parse_args()
        im_b64 = args['image_data']
        try:
            im_binary = base64.b64decode(im_b64)

            buf = io.BytesIO(im_binary)
            img = Image.open(buf)

            classifier_id = args['classifier_id']
            attack_id = args['attack_id']

            (original_image,
             result_image,
             difference_image,
             is_adv,
             epsilons) = run_attack(img,
                                    classifier_id,
                                    attack_id,
                                    scale=4)

            original_file = io.BytesIO()
            original_image.save(original_file, format="JPEG")
            original_bytes = original_file.getvalue()

            result_file = io.BytesIO()
            result_image.save(result_file, format="JPEG")
            result_bytes = result_file.getvalue()

            difference_file = io.BytesIO()
            difference_image.save(difference_file, format="PNG")
            difference_bytes = difference_file.getvalue()

            return {
                "original_image":
                    base64.b64encode(original_bytes).decode(),
                "result_image":
                    base64.b64encode(result_bytes).decode(),
                "difference_image":
                    base64.b64encode(difference_bytes).decode()
            }
        except IndexError:
            api.abort(404)
        except ValueError:
            api.abort(422)


def run_attack(image, classifier_id, attack_id, robust=False, scale=1):
    """Run an attack.

    Parameters
    ----------
    image : [PIL Image]
        Some input image.
    classifier_id : [int]
        Classifier identifier in pretrained_classifiers.
    attack_id : [int]
        Attack identifier in set_attacks.
    robust : [bool]

        .If this is passed, the attack is run with 20
        different epsilons.
            This allows us to study the robustness of the model
            to the attack.
            If the model's accuracy varies wildly, then
            the model is not robust. If it remains mostly
            uniform, then the model is robust.

        .If this is True, is_adv will change:
            It will have the shape [20, N], where N is the
            number of images passed in image.
            this means that is_adv[i][j] will be the bool
            for the i-th epsilon, on the j-th attack.
    scale : [int]
        The scale to use to output the images.
        Images after an attack will be compressed to 100x100.
        A desired output of 400x400 would require a scale of 4.
        The resizing is done in a way that preserves aspect ratios.

    Returns
    -------
    - original_image
        [PIL Image]
            Image before applying the attack to it,
            after the pre-processing needed to classify
            it.
    - result_image
        [PIL Image]
            Image after running the attack.
    - difference_image
        [PIL Image]
            Image of the pixel differences between result_image
            and original_image.
    - is_adv
        [torch.Tensor]
            Explained in PyTorchAttack.run.
    - epsilons
        [float or np.array]
            The epsilons used to run the attack.
            This depends only on whether or not
            a robustness analysis was requested.
    """
    classifier = pretrained_classifiers[int(classifier_id)].classifier

    # result = classifier.predict(img, n=1)[0][1]
    label_index = classifier.predict(image, n=1)[0][0].item()
    label = classifier.prep_label(label_index)
    original_image = classifier.prep_tensor(image,
                                            normalize=False)
    if robust:
        epsilons = np.linspace(0.0, 0.005, num=20)
    else:
        epsilons = 0.03

    attack = PyTorchAttack(classifier.model,
                           set_attacks[int(attack_id)]["attack"])

    adv, is_adv = attack.run(original_image,
                             labels=label,
                             epsilons=epsilons)
    if robust:
        adv = adv[0]

    difference_tensor = adv - original_image

    result_image = get_image_from_tensor(images=adv, scale=scale)
    original_image = get_image_from_tensor(images=original_image,
                                           scale=scale)
    difference = get_image_from_tensor(images=difference_tensor,
                                       scale=scale, bounds=(-0.1, 0.1),
                                       ext='PNG')

    return original_image, result_image, difference, is_adv, epsilons
