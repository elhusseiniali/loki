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
        return [dataset['name'] for dataset in set_datasets]


parser = reqparse.RequestParser()
parser.add_argument('class_id', required=False)


@api.route('/<dataset_id>')
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
