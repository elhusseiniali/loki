import datetime

from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from flask_restx import Namespace
from loki import db
from loki.api.classifiers.routes import predict
from loki.api.reports.forms import ReportForm
from loki.models import Classifier, Report
from PIL import Image

import base64
import io
import requests

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
    if form.validate_on_submit():
        images = form.images.data
        responses_before = []
        responses_after = []

        for image in images:
            # launch attack
            
            # Classify images
            # Before attack
            BASE_CLASSIFY = "http://localhost:5000/api/1/classifiers/classify"
            im_b64 = base64.b64encode(image.read())
            files = {'image_data': im_b64,
                     'classifier_id': form.model.data}
            response = requests.put(BASE_CLASSIFY, data=files)
            responses_before.append(response[0])

            # After attack
            responses_after.append(response[0])
        # save the report in the database

        return render_template('home.html',
                               title='Visualize Report.',
                               images=images,
                               responses_before=responses_before,
                               responses_after=responses_after)

    return render_template('new_report.html', title='Reports', form=form)
