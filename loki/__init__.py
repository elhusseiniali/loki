from flask import Flask

from flask_sqlalchemy import SQLAlchemy

from flask_bcrypt import Bcrypt
from flask_login import LoginManager

from flask_restx import Api

from flask_mail import Mail


app = Flask(__name__)
app.config['SECRET_KEY'] = '60808326457a6384f78964761aaa161c'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
# This is to suppress SQLAlchemy warnings
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

api = Api(app)

login_manager = LoginManager(app)
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'

app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USER_TLS'] = True
app.config['MAIL_USERNAME'] = "username"
app.config['MAIL_PASSWORD'] = "password"

mail = Mail(app)


#   Below import is necessary, even if the linter complains about it.
#   This is because the linter cannot distinguish between imports in a script
#   and imports in a package. The order of the imports is also important.
#   These two imports *had* to happen after initializing db.
from loki import routes
from loki.models import User, Classifier, Report

from flask_admin import Admin
from loki.admin_views import UserView, ClassifierView, ReportView


# set optional bootswatch theme
app.config['FLASK_ADMIN_SWATCH'] = 'flatly'

admin = Admin(app, name='Loki Admin', template_mode='bootstrap3')
# Add administrative views here
admin.add_view(UserView(User, db.session))
admin.add_view(ClassifierView(Classifier, db.session))
admin.add_view(ReportView(Report, db.session))


from loki.users.routes import users
from loki.main.routes import main
from loki.classifiers.routes import classifiers
from loki.attacks.routes import attacks


app.register_blueprint(users)
app.register_blueprint(main)
app.register_blueprint(classifiers)
app.register_blueprint(attacks)
