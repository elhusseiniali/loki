from loki import db, login_manager, bcrypt
from flask_login import UserMixin
from sqlalchemy.ext.hybrid import hybrid_property
from flask_validator import ValidateEmail

import datetime


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)

    _password = db.Column(db.String(128), nullable=False)

    models = db.relationship("FRS", back_populates="user")

    def __init__(self,
                 username, email,
                 password):
        self.username = username
        self.email = email

        self.password = password

    def __repr__(self):
        return (f"User('{self.username}': '{self.email}')")

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        self._password = bcrypt.generate_password_hash(password)

    def verify_password(self, password):
        return bcrypt.check_password_hash(self._password, password)

    @classmethod
    def __declare_last__(cls):
        # Check available validators:
        # https://flask-validator.readthedocs.io/en/latest/
        ValidateEmail(User.email,
                      allow_smtputf8=True,
                      check_deliverability=True,
                      throw_exception=True,
                      message="The e-mail is invalid.")


class FRS(db.Model):
    __tablename__ = "FSR"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    name = db.Column(db.String(50), unique=False, nullable=True)
    upload_date = db.Column(db.DateTime,
                            default=datetime.datetime.now)
    # file_path should not be nullable; set to True only for testing
    file_path = db.Column(db.String(50), unique=True, nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship("User", back_populates="models")
