from flask import render_template, flash, redirect, url_for, request, abort
from loki import app, db
from loki.forms import RegistrationForm, LoginForm, UpdateAccountForm, \
                       DisplayAttackForm
from loki.forms import FRSForm
from loki.models import User, FRS
from loki.utils import save_image, save_model, remove_model

from flask_login import login_user, current_user, logout_user, login_required


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

    page = request.args.get('page', 1, type=int)
    models = FRS.query.filter_by(user=current_user)\
                .order_by(FRS.upload_date.desc())\
                .paginate(page=page, per_page=5)

    return render_template('account.html',
                           title='Account',
                           image_file=image_file, form=form,
                           models=models)


@app.route("/model/upload",
           methods=['GET', 'POST'])
@login_required
def upload_model():
    form = FRSForm()
    if form.validate_on_submit():
        model_path = save_model(form.model.data)
        frs = FRS(name=form.name.data, file_path=model_path,
                  user=current_user)
        db.session.add(frs)
        db.session.commit()
        flash('Model uploaded! You can now analyze it!', 'success')
        return redirect(url_for('account'))

    return render_template('upload_model.html',
                           title='Upload Model',
                           form=form)


@app.route("/model/<int:model_id>")
@login_required
def get_model(model_id):
    model = FRS.query.get_or_404(model_id)
    return render_template('model.html', title=model.name, model=model)


@app.route("/model/delete/<int:model_id>", methods=['POST'])
@login_required
def delete_model(model_id):
    model = FRS.query.get_or_404(model_id)
    if model.user != current_user:
        abort(403)  # forbidden route
    remove_model(model.file_path)
    db.session.delete(model)
    db.session.commit()
    flash('Your model has been deleted!', 'success')
    return redirect(url_for('models'))


@app.route("/display/attack",
           methods=['POST', 'GET'])
def attack_display():
    form = DisplayAttackForm()
    print(form.data)
    if form.validate_on_submit():
        attack = form.attacks.data
        image_file = url_for('static',
                             filename="profile_pictures/default.jpg")
        next_image_file = image_file
        print(attack)
        # image_file = compress_image(form.image.data)
        # next_image_file = launch_attack(image_file=image_file, attack=attack)
        flash("The image has been successfully attacked!", 'success')
        return render_template('attack_display.html', form=form,
                               image_file=image_file,
                               next_image_file=next_image_file)

    return render_template('attack_display.html', form=form)
