from flask import Blueprint, render_template, request
from flask_login import current_user, login_required

from loki.models import Report, Classifier
from flask_restx import Namespace
from loki.api.reports.forms import ReportForm


reports = Blueprint('reports', __name__)
api = Namespace('reports', description='All operations on reports.')


@reports.route("/reports/all",
               methods=['POST', 'GET'])
@login_required
def all_reports():
    models = Classifier.query.filter_by(user=current_user)\
                             .order_by(Classifier.upload_date.desc())\
                             .all()

    list_id = [model.id for model in models]
    page = request.args.get('page', 1, type=int)
    reports = Report.query.filter(Report.id.in_(list_id))\
                          .paginate(page=page, per_page=5)

    return render_template('reports.html', title='Reports',
                           reports=reports)


@reports.route("/reports/new",
               methods=['POST', 'GET'])
@login_required
def new_report():
    form = ReportForm()
    return render_template('new_report.html', title='Reports', form=form)
