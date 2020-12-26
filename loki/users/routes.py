from flask import Blueprint
import json
from flask import render_template, flash, redirect, url_for, request, abort
from flask import send_file
from loki import app, db, api, mail

from loki.users.forms import (RegistrationForm, LoginForm,
                              UpdateAccountForm)
from flask_login import login_user, current_user, logout_user, login_required

from loki.models import User, Classifier
from loki.utils import save_image

from flask_mail import Message

users = Blueprint('users', __name__)


@users.route("/register",
             methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,
                    email=form.email.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()

        flash('Account created! You can now log in.', 'success')
        return redirect(url_for('users.login'))

    return render_template('register.html',
                           title='Register',
                           form=form)


@users.route("/login",
             methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.verify_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page \
                else redirect(url_for('main.home'))
        else:
            flash("Login unsuccessful!", 'danger')

    return render_template('login.html',
                           title='Log in',
                           form=form)


@users.route("/logout",
             methods=['GET'])
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@users.route("/account",
             methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()

    if form.validate_on_submit():
        if form.image.data:
            image_file = save_image(form.image.data, path="profile_pictures")
            current_user.image_file = image_file

        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Your account has been successfully updated!", 'success')
        return redirect(url_for('users.account'))

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file = url_for('static',
                         filename=f"profile_pictures/"
                                  f"{current_user.image_file}")

    page = request.args.get('page', 1, type=int)
    models = Classifier.query.filter_by(user=current_user)\
                             .order_by(Classifier.upload_date.desc())\
                             .paginate(page=page, per_page=5)

    return render_template('account.html',
                           title='Account',
                           image_file=image_file, form=form,
                           models=models)
