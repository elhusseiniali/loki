from flask import Blueprint, render_template
from flask_restx import Namespace, Resource, reqparse

from loki.dao.datasets import datasets as set_datasets


datasets = Blueprint('datasets', __name__)
api = Namespace('datasets', description='Operations on datasets')


@api.route('/all')
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
    @api.doc('Get dataset from id')
    def put(self, dataset_id):

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
parser.add_argument('class_id', required=False)


@api.route('/labels/<dataset_id>')
@api.param('dataset_id', 'Dataset identifier')
class Label(Resource):
    @api.expect(parser)
    def put(self, dataset_id):
        """Get labels from dataset.

        Parameters
        ----------
        dataset_id : [int]
            dataset id from set_datasets
        class_id : [int], optional
            class id

        Returns
        -------
        if class_id is given:
            human-readable label for class_id (e.g. "goldfish" for 1)
        else:
            all labels in selected dataset.
        """
        DAO = set_datasets[int(dataset_id)]["DAO"]

        args = parser.parse_args()
        class_id = args['class_id']

        if not class_id:
            return DAO.get_all()
        else:
            return DAO.get_by_id(class_id)
