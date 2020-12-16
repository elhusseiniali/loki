import json
from flask import render_template, flash, redirect, url_for, request, abort
from flask import send_file
from loki import app, db

from loki.forms import RegistrationForm, LoginForm, UpdateAccountForm
from loki.forms import VisualizeAttackForm
from loki.forms import UploadClassifierForm, PredictForm

from loki.classifiers import pretrained_classifiers
from loki.attacks import PyTorchAttack
from loki.attacks import attacks as set_attacks

from loki.models import User, Classifier, Report

# from loki.attacks import gray
from loki.utils import save_image, save_model, remove_model

from flask_login import login_user, current_user, logout_user, login_required

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


@app.route('/models/download/<int:model_id>', methods=['GET', 'POST'])
def download_model(model_id):
    model = Classifier.query.get_or_404(model_id)
    filepath = model.file_path
    return send_file(filepath, as_attachment=True,
                     attachment_filename=f'{model.name}.h5')


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
        index = int(form.model.data) - 1
        classifier = pretrained_classifiers[int(form.model.data)][1]

        img = Image.open(form.image.data)
        label_index = classifier.predict(img, n=1)[0][0].item()
        label = classifier.prep_label(label_index)

        attack = PyTorchAttack(classifier.model,
                               set_attacks[int(form.attacks.data)][1])

        adv = attack.run(classifier.prep_tensor(img,
                                                normalize=False),
                         labels=label)
        result_image = PyTorchAttack.get_image(images=adv,
                                               scale=3.5)
        # img_att = Image.open("ATTACK_IMAGE.jpg")

        image_file = save_image(form.image.data, path="tmp",
                                output_size=(400, 400))
        result_file = save_image(result_image, path="tmp",
                                 output_size=(400, 400))
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
        classifier = pretrained_classifiers[int(form.model.data)][1]

        img = Image.open(f"./loki/{path}")
        label = classifier.predict(img)

        flash("Done!", 'success')

        return render_template('predict.html',
                               title='Classify an image.',
                               image_file=image_file, form=form,
                               label=label, index=index)
    return render_template('predict.html',
                           title='Classify an image.', form=form)

@app.route("/report_test")
def report_test():
    return render_template('report_test.html', title='Home')