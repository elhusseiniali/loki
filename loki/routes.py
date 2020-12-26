from loki import api

from flask_restx import Resource


@api.route('/hello')
class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}


@api.route('/classifier/predict/<int:classifier_id>')
class ClassifierRoute(Resource):
    def get(self, classifier_id):
        return {'classifier': classifier_id}
