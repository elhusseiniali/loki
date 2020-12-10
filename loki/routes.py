from flask import render_template, flash, redirect, url_for, request, abort
from loki import app, db

from loki.forms import RegistrationForm, LoginForm, UpdateAccountForm
from loki.forms import VisualizeAttackForm
from loki.forms import UploadClassifierForm, PredictForm

from loki.classifiers import InceptionResNet as IR

from loki.models import User, Classifier, Report

from loki.attacks import gray
from loki.utils import save_image, save_model, remove_model

from flask_login import login_user, current_user, logout_user, login_required


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', title='Home')


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register",
           methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=request.form.get("username"),
                    email=request.form.get("email"),
                    password=request.form.get("password"))
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
            flash("You are logged in!", 'success')
            return redirect(next_page) if next_page \
                else redirect(url_for('home'))
        else:
            flash("Login unsuccessful!", 'danger')

    return render_template('login.html',
                           title='Log in',
                           form=form)


@app.route("/logout",
           methods=['GET'])
@login_required
def logout():
    logout_user()
    flash("You are logged out!", 'success')
    return redirect(url_for('home'))


@app.route("/account",
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
        return redirect(url_for('account'))

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


@app.route("/models/upload",
           methods=['GET', 'POST'])
@login_required
def upload_model():
    """Upload a model. This automatically populates the User-Model relationship.
    """
    form = UploadClassifierForm()
    if form.validate_on_submit():
        model_path = save_model(form.model.data)
        classifier = Classifier(name=form.name.data, file_path=model_path,
                                user=current_user)
        db.session.add(classifier)
        db.session.commit()
        flash('Model uploaded! You can now analyze it!', 'success')
        return redirect(url_for('account'))

    return render_template('upload_model.html',
                           title='Upload Model',
                           form=form)


@app.route("/models/<int:model_id>")
@login_required
def get_model(model_id):
    model = Classifier.query.get_or_404(model_id)
    reports = Report.query.filter_by(model=model)
    return render_template('model.html', title=model.name,
                           model=model, reports=reports)


@app.route("/models/delete/<int:model_id>", methods=['POST'])
@login_required
def delete_model(model_id):
    model = Classifier.query.get_or_404(model_id)
    if model.user != current_user:
        abort(403)  # forbidden route
    remove_model(model.file_path)
    db.session.delete(model)
    db.session.commit()
    flash('Your model has been deleted!', 'success')
    return redirect(url_for('account'))


@app.route("/attacks/visualize",
           methods=['POST', 'GET'])
@login_required
def visualize_attack():
    """Run selected attack on uploaded image.

    TODO
    ----
    - For now, we don't have any logic that goes over what specific
    attack was selected. This can be easily fixed, but because we ran
    out of time, we didn't implement it.

    - The way the path is passed to the attack method is also messy:
    this can be done more elegantly using url_for to avoid problems
    that would happen on deployment (I think Docker is weird with this
    sort of stuff), and anyway it's bad practice to hardcode a path like
    this. I'll add it as an issue after the commit.
    """
    form = VisualizeAttackForm()
    if form.validate_on_submit():
        index = len(form.model.choices) - int(form.model.data)
        image_file = save_image(form.image.data, path="tmp",
                                output_size=(400, 400))

        result_file = gray(f"./loki/static/tmp/"
                           f"{image_file}")
        flash("Attack successully run!", 'success')

        return render_template('visualize_attack.html', form=form,
                               image_file=image_file, result_file=result_file,
                               index=index)
    return render_template('visualize_attack.html', form=form)


@app.route("/models/predict",
           methods=['POST', 'GET'])
@login_required
def predict():
    form = PredictForm()

    if form.validate_on_submit():
        index = int(form.model.data) - 1

        image_file = save_image(form.image.data, path="tmp")
        path = url_for('static',
                       filename=f"tmp/"
                                f"{image_file}")
        classifier = IR()
        label = classifier.predict(path)

        flash("Done!", 'success')

        return render_template('predict.html',
                               title='Classify an image.',
                               image_file=image_file, form=form,
                               label=label, index=index)
    return render_template('predict.html',
                           title='Classify an image.', form=form)
