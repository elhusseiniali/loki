from loki.schemas.users import UserSchema
from loki.dao import user_dao
from loki.services.users import user_service

from flask_restx import Namespace, Resource
from flask import request


api = Namespace('users', description='User-related operations')
user_schema = UserSchema()


@api.route('/')
class Users(Resource):

    @api.doc(description="Get all users from the database.")
    def get(self):
        all_users = user_dao.get_all()
        return user_schema.dump(all_users, many=True)

    @api.doc(params={"username": "user username",
                     "email": "user email",
                     "password": "user password"},
             description="Add a user to the database.",
             responses={201: "The user was created successfully.",
                        422: "Error: The parameters were"
                             " valid but the request failed.",
                        400: "Error: Bad Request. Check parameters"})
    def post(self):
        username = request.args.get('username')
        email = request.args.get('email')
        password = request.args.get('password')

        if not(username is None) and \
           not(email is None) and \
           not(password is None):
            try:
                user_service.create_user(username=username,
                                         email=email,
                                         password=password)

                return "The user was created successfully.", 201

            except Exception as e:
                api.abort(422, e, status="Could not save information",
                          statusCode="422")

        api.abort(400, "Bad Request. Check parameters.",
                  status="Could not save information", statusCode="400")


@api.route('/user_id=<int:user_id>')
class getUser(Resource):

    @api.doc(description="Get a user by id from the database.",
             responses={404: "The user was not found.",
                        200: "The user was found."})
    def get(self, user_id=None):
        user = user_dao.get_by_id(user_id=user_id)

        if not(user is None):
            return user_schema.dump(user)

        api.abort(404, message="The user was not found.",
                  status="Could not find information", statusCode="404")
