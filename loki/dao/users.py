from loki.models import User
from loki import db


class UserDAO():
    __instance__ = None

    def __init__(self):
        if UserDAO.__instance__ is None:
            UserDAO.__instance__ = self
        else:
            raise Exception("You cannot create another UserDAO class")

    @staticmethod
    def get_instance():
        if not UserDAO.__instance__:
            UserDAO()
        return UserDAO.__instance__

    def add(self, user):
        db.session.add(user)
        db.session.commit()

    def get_all(self):
        return db.session.query(User).all()

    def get_by_id(self, user_id):
        return db.session.query(User).get(user_id)

    def get_by_username(self, username):
        return db.session.query(User).filter_by(username=username).first()

    def get_by_email(self, email):
        return db.session.query(User).filter_by(email=email).first()

    def get_models(self, user_id):
        user = self.get_by_id(user_id=user_id)
        return user.models


user_dao = UserDAO()
