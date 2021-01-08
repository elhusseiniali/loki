from loki.schemas.users import UserSchema
from loki.dao.users import user_dao
from loki.services.users import user_service

from flask_restx import Namespace, Resource, reqparse


api = Namespace('users', description='User-related operations')
user_schema = UserSchema()


@api.route('/all')
@api.response('200', 'Success')
class Users(Resource):
    def get(self):
        """An endpoint to get all users from the database.

        Parameters
        ----------
        None

        Returns
        -------
        [JSON]
            dict of the form {"users": [list-of-users]}
        """
        all_users = user_dao.get_all()
        return user_schema.dump(all_users, many=True)


parser = reqparse.RequestParser()
parser.add_argument('username', required=True)
parser.add_argument('email', required=True)
parser.add_argument('password', required=True)


@api.route('/add')
@api.response('201', 'Success: The user was created successfully.')
@api.response('400', 'Error: Bad request. Check parameters.')
@api.response('422', 'Error: The request failed.')
class AddUser(Resource):
    @api.expect(parser)
    def post(self):
        """Add a new user.

        Parameters
        ----------
        - username:
            Usernames have to be unique.
        - email:
            Emails have to be unique.
        - password:
            Passwords are automatically hashed when they are stored.
        """
        args = parser.parse_args()
        username = args['username']
        email = args['email']
        password = args['password']

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


@api.route('/<int:user_id>')
@api.param('user_id', 'User identifier', required=True)
@api.response('200', 'Success: User found.')
@api.response('404', 'Error: User not found.')
class getUser(Resource):
    def put(self, user_id):
        """Get user by id.

        Parameters
        ----------
        - user_id : [int]

        Returns
        -------
        [JSON]
            dict with the structure:
            {
                "user": {
                    "username": username,
                    "email": email,
                    "password": hashed password,
                    "image_path": name of profile picture
                }
            }
        """
        user = user_dao.get_by_id(user_id=user_id)
        if user:
            return user_schema.dump(user)

        api.abort(404, message="The user was not found.",
                  status="Could not find information", statusCode="404")
