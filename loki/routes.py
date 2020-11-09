from flask import render_template, flash, redirect, url_for, request
from loki import app, db
from loki.forms import RegistrationForm, LoginForm, UpdateAccountForm
from loki.models import User

from flask_login import login_user, current_user, logout_user, login_required

import secrets
import os
from PIL import Image


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', title='Home')


@app.route("/about")
def about():
    return render_template('about.html')


@app.route("/register",
           methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,
                    email=form.email.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()

        flash('Account created! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html',
                           title='Register',
                           form=form)


@app.route("/login",
           methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.verify_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page \
                else redirect(url_for('home'))
        else:
            flash("Login unsuccessful!", 'danger')

    return render_template('login.html',
                           title='Log in',
                           form=form)


@app.route("/logout",
           methods=['GET'])
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_image(form_image):
    """Compress and save user-uploaded images to the filesystem.

    Parameters
    ----------
    form_image : [image]
        User-uploaded profile picture.

    Returns
    -------
    [image_fn]
        File name of resized image as it is saved on filesystem.
    """
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_image.filename)
    image_fn = random_hex + f_ext
    image_path = os.path.join(app.root_path,
                              'static/profile_pictures',
                              image_fn)

    output_size = (125, 125)
    i = Image.open(form_image)
    i.thumbnail(output_size)

    i.save(image_path)

    return image_fn


@app.route("/account",
           methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()

    if form.validate_on_submit():
        if form.image.data:
            image_file = save_image(form.image.data)
            current_user.image_file = image_file

        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Your account has been successfully updated!", 'success')
        return redirect(url_for('account'))

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file = url_for('static',
                         filename=f"profile_pictures/"
                                  f"{current_user.image_file}")
    return render_template('account.html',
                           title='Account',
                           image_file=image_file, form=form)
