from loki.dao.reports import report_dao
from loki.services.reports import report_service
from loki.schemas.reports import ReportSchema

from flask_restx import Namespace, Resource, reqparse
from sklearn.metrics import confusion_matrix
import json


api = Namespace('reports', description='Report-related operations')
report_schema = ReportSchema()


@api.route('/all')
@api.response('200', 'Success')
class Reports(Resource):
    def get(self):
        all_reports = report_dao.get_all()
        return report_schema.dump(all_reports, many=True)


@api.route('/<int:report_id>')
@api.param('report_id', 'Report identifier', required=True)
@api.response('200', 'Success: Report found')
@api.response('404', 'Error: Report not found')
@api.response('422', 'Error: report_id has to be an int')
class getReport(Resource):
    def put(self, report_id):
        try:
            report = report_dao.get_by_report_id(report_id)
            return report_schema.dump(report)

        except IndexError:
            api.abort(404)
        except ValueError:
            api.abort(422)


parser = reqparse.RequestParser()
parser.add_argument('y_before', action='split', required=True)
parser.add_argument('y_after', action='split', required=True)


@api.route('/confusion_matrix')
@api.response(200, 'Success')
@api.response(422, 'Error: The request failed')
class ConfusionMatrix(Resource):
    @api.expect(parser)
    def put(self):
        """Generate confusion matrix from two lists of labels.

        Parameters
        ----------
        - y_before
        - y_after
        [Lists] of labels

        Returns
        -------
        List of lists representing the confusion matrix.
        """
        args = parser.parse_args()
        y_before = args['y_before']
        y_after = args['y_after']
        labels = list(set(y_before + y_after))
        try:
            cm = confusion_matrix(y_before, y_after, labels=labels)
            return cm.tolist()
        except Exception as e:
            api.abort(422, e, status="Something went wrong")
