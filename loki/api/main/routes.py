from flask import Blueprint, render_template
from loki.dao.datasets import datasets
from loki.api.classifiers.models import pretrained_classifiers
from loki.api.attacks.models import attacks
main = Blueprint('main', __name__)


@main.route("/")
@main.route("/home")
def home():
    return render_template('home.html', title='Home',
                           datasets=datasets,
                           classifiers=pretrained_classifiers,
                           attacks=attacks,
                           )


@main.route("/about")
def about():
    return render_template('about.html', title='About')
