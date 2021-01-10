import datetime

from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from flask_restx import Namespace
from loki import db
from loki.api.reports.forms import ReportForm
from loki.models import Classifier, Report

import base64
import json
import requests
from PIL import Image
import io
import numpy as np


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
        original_images = []
        result_images = []
        difference_images = []
        original_labels = []
        result_labels = []

        for image in images:
            # Launch attack
            BASE_ATTACK = "http://localhost:5000/api/1/attacks/run"
            im = image.read()
            im_b64 = base64.b64encode(im)
            files = {'image_data': im_b64,
                     'attack_id': form.attacks.data,
                     'classifier_id': form.model.data}
            response = requests.put(BASE_ATTACK, data=files)
            images_dict = json.loads(response.text)
            original_image, result_image, difference_image = \
                images_dict['original_image'], images_dict['result_image'], \
                images_dict['difference_image']

            original_images.append("data:image/jpeg;base64," +
                                   original_image.encode().decode("utf-8"))
            result_images.append("data:image/jpeg;base64," +
                                 result_image.encode().decode("utf-8"))
            difference_images.append("data:image/jpeg;base64," +
                                     difference_image.encode().decode("utf-8"))

            # Classify images
            # Before attack
            BASE_CLASSIFY = "http://localhost:5000/api/1/classifiers/classify"
            files = {'image_data': im_b64,
                     'classifier_id': form.model.data}
            response = requests.put(BASE_CLASSIFY, data=files)
            preds = json.loads(response.text)
            original_labels.append(preds[0]['label'])

            # After attack
            im_b64 = result_image.encode()
            files = {'image_data': im_b64,
                     'classifier_id': form.model.data}
            response = requests.put(BASE_CLASSIFY, data=files)
            preds = json.loads(response.text)
            result_labels.append(preds[0]['label'])

        # Data for the confusion matrix
        BASE_CONFUSION = "http://localhost:5000/api/1/reports/confusion_matrix"
        str_original_labels = ",".join(original_labels)
        str_result_labels = ",".join(result_labels)
        data = {
            "y_before": str_original_labels,
            "y_after": str_result_labels
        }
        response = requests.put(BASE_CONFUSION, data=data)
        confusion_matrix = response.json()
        classes = list(set(original_labels + result_labels))
        X_values = ['Bird', 'Cat', 'Dog', 'Mouse']
        # save the report in the database
        return render_template('visualize_report.html',
                               title='Visualize Report.',
                               len=len(images),
                               images=images,
                               original_images=original_images,
                               result_images=result_images,
                               difference_images=difference_images,
                               original_labels=original_labels,
                               result_labels=result_labels,
                               X_values=X_values,
                               confusion_matrix=confusion_matrix,
                               classes=classes
                               )

    return render_template('new_report.html', title='Reports', form=form)
