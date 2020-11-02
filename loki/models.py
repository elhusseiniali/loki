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

    image_file = db.Column(db.String(30),
                           nullable=False,
                           default='default.jpg')

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
        # check_deliverability is set to False to avoid a deprecation
        # warning with pytest; this is due to a problem
        # with the flask-validator release available on PyPI.
        # We already contacted the developer to update the release
        # and hopefully we can set the check to True afterwards.
        ValidateEmail(User.email,
                      allow_smtputf8=True,
                      check_deliverability=False,
                      throw_exception=True,
                      message="The e-mail is invalid.")


class FRS(db.Model):
    __tablename__ = "FRS"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    name = db.Column(db.String(50), unique=False, nullable=True)
    upload_date = db.Column(db.DateTime,
                            default=datetime.datetime.now)
    # file_path should not be nullable; set to True only for testing
    file_path = db.Column(db.String(50), unique=True, nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship("User", back_populates="models")

    reports = db.relationship("Report", back_populates="model")

    def __init__(self, name, upload_date, user):
        self.name = name
        self.upload_date = upload_date
        self.user = user

    def __repr__(self):
        return(f"FRS('{self.name}') for {self.user},"
               f" uploaded on {self.upload_date}.")


class Report(db.Model):
    __tablename__ = "report"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.DateTime,
                     default=datetime.datetime.now)

    model_id = db.Column(db.Integer, db.ForeignKey("FRS.id"))
    model = db.relationship("FRS", back_populates="reports")

    data = db.Column(db.JSON)

    def __init__(self, date, model):
        self.date = date
        self.model = model

    def __repr__(self):
        return(f"Report for {self.model}, "
               f"generated on {self.date}.")
