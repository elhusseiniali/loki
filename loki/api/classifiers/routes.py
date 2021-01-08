from PIL import Image

from loki.api.classifiers.models import pretrained_classifiers


from flask_restx import Namespace, Resource, reqparse

import base64
import io


api = Namespace('classifiers', description='All operations on classifiers.')


@api.route('/all')
class ClassifierList(Resource):
    def get(self):
        """Get a list of all classifiers.
        """
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
@api.response(422, 'Error: ID has to be an integer')
class ClassifierID(Resource):
    def get(self, classifier_id):
        """Get information for a classifier from classifier_id.
        IDs start from 0.
        """
        try:
            return {
                "name": pretrained_classifiers[int(classifier_id)]["name"],
                "paper": pretrained_classifiers[int(classifier_id)]["paper"]
            }
        except IndexError:
            api.abort(404)
        except ValueError:
            api.abort(422)


parser = reqparse.RequestParser()
parser.add_argument('image_data', required=True)
parser.add_argument('classifier_id')


@api.route('/classify')
@api.response(200, 'Success')
@api.response(404, 'Error: Index does not exist')
@api.response(422, 'Error: Check parameters')
class Classify(Resource):
    @api.expect(parser)
    def put(self):
        """Classify image with pre-trained classifier.

        Parameters
        ----------
        -  image_data:
        Base64-encoded image.
        -  classifier_id:
        Classifier identifier. Integer.


        Returns
        -------
        List of JSON, where each JSON has the form:
        {
            "index": class index,
            "label": label (name of class index),
            "percentage": classifier confidence
        }
        """
        args = parser.parse_args()
        im_b64 = args['image_data']

        try:
            im_binary = base64.b64decode(im_b64)

            buf = io.BytesIO(im_binary)
            img = Image.open(buf)

            classifier_id = args['classifier_id']
            label = predict(img, classifier_id)

        except IndexError:
            api.abort(404)
        except ValueError:
            api.abort(422)

        return [{"index": elem[0].item(),
                 "label": elem[1],
                 "percentage": elem[2]} for elem in label]


def predict(image, classifier_index):
    classifier = pretrained_classifiers[int(classifier_index)]["classifier"]
    return classifier.predict(image)
