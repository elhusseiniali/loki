from flask import Blueprint
from flask_restx import Api

from loki.api.attacks.routes import api as attacks
from loki.api.classifiers.routes import api as classifiers


blueprint = Blueprint('api', __name__)
api = Api(blueprint)

api.add_namespace(attacks)
api.add_namespace(classifiers)
