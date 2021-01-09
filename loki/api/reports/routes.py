from loki.dao.reports import report_dao
from loki.services.reports import report_service
from loki.schemas.reports import ReportSchema

from flask_restx import Namespace, Resource, reqparse


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
