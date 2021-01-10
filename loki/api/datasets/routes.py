from flask import Blueprint, render_template
from flask_restx import Namespace, Resource, reqparse

from loki.dao.datasets import datasets as set_datasets


datasets = Blueprint('datasets', __name__)
api = Namespace('datasets', description='Operations on datasets')


@api.route('/all')
@api.response(200, 'Success')
class DatasetList(Resource):
    @api.doc('Get a list of all datasets')
    def get(self):
        """Get a list of the names of all datasets in set_datasets.
        """
        return [
            {
                "name": dataset['name'],
                "paper": dataset['paper']
            } for dataset in set_datasets
        ]


@api.route('/<dataset_id>')
@api.param('dataset_id', 'Dataset identifier')
@api.response(200, 'Success: Dataset found')
@api.response(404, 'Error: Dataset not found')
@api.response(422, 'Error: Check parameters')
class Dataset(Resource):
    def put(self, dataset_id):
        """Get dataset from dataset_id

        Parameters
        ----------
        - dataset_id : [int]

        Responses
        ---------
        - 200:
            The dataset information was found.
        - 404:
            The ID passed was out of bounds.
        - 422:
            The ID was not an int.
        """
        try:
            return {
                "name": set_datasets[int(dataset_id)]["name"],
                "paper": set_datasets[int(dataset_id)]["paper"]
            }
        except IndexError:
            api.abort(404)
        except ValueError:
            api.abort(422)


parser = reqparse.RequestParser()
parser.add_argument('class_id', required=True)


@api.route('/labels/<dataset_id>')
@api.param('dataset_id', 'Dataset identifier', required=True)
@api.response('200', 'Success')
@api.response('404', 'Error: index out of bounds.')
@api.response('422', 'Error: indices have to be integers.')
class Label(Resource):
    @api.expect(parser)
    def put(self, dataset_id):
        """Get label corresponding to class_id from dataset.

        Parameters
        ----------
        dataset_id : [int]
            dataset id from set_datasets
        class_id : [int]
            class id

        Returns
        -------
        human-readable label for class_id (e.g. "goldfish" for 1)

        Responses
        ---------
        - 200:
            The label was found.
        - 404:
            The ID passed was out of bounds.
        - 422:
            The ID was not an int.

        """
        try:
            DAO = set_datasets[int(dataset_id)]["DAO"]
        except IndexError:
            api.abort(404)
        except ValueError:
            api.abort(422)

        args = parser.parse_args()
        class_id = args['class_id']

        try:
            return DAO.get_by_id(class_id)
        except IndexError:
            api.abort(404)
        except ValueError:
            api.abort(422)

    def get(self, dataset_id):
        """Get all labels from dataset.

        Responses
        ---------
        - 200:
            The information was found.
        - 404:
            The ID passed was out of bounds.
        - 422:
            The ID was not an int.
        """
        try:
            DAO = set_datasets[int(dataset_id)]["DAO"]
        except IndexError:
            api.abort(404)
        except ValueError:
            api.abort(422)

        return DAO.get_all()
