from flask import Blueprint
from flask_restx import Api

from loki.api.attacks.routes import api as attacks
from loki.api.classifiers.routes import api as classifiers
from loki.api.users.routes import api as users
from loki.api.datasets.routes import api as datasets
from loki.api.reports.routes import api as reports


blueprint = Blueprint('api', __name__)
api = Api(blueprint)

api.add_namespace(attacks)
api.add_namespace(classifiers)
api.add_namespace(users)
api.add_namespace(datasets)
api.add_namespace(reports)
