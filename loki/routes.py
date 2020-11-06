from flask import render_template, flash, redirect, url_for, request, abort
from loki import app, db
from loki.forms import RegistrationForm, LoginForm, UpdateAccountForm
from loki.forms import FRSForm, ReportForm
from loki.models import User, FRS, Report
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
        if user.verify_password(form.password.data):
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


@login_required
def models():
    page = request.args.get('page', 1, type=int)
    models = FRS.query.filter_by(user=current_user)\
                .order_by(FRS.upload_date.desc())\
                .paginate(page=page, per_page=5)

    return render_template('models.html',
                           models=models,
                           title='My models')


@app.route("/model/new",
           methods=['GET', 'POST'])
@login_required
def new_model():
    form = FRSForm()
    if form.validate_on_submit():
        model_path = save_model(form.model.data)
        frs = FRS(name=form.name.data, user=current_user, file_path=model_path)
        db.session.add(frs)
        db.session.commit()
        flash('Model uploaded! You can now launch report for it !', 'success')
        return redirect(url_for('new_report'))

    return render_template('new_model.html',
                           title='New Model',
                           form=form)


@app.route("/model/<int:model_id>")
@login_required
def model(model_id):
    model = FRS.query.get_or_404(model_id)
    return render_template('model.html', title=model.name, model=model)


@app.route("/model/<int:model_id>/delete", methods=['POST'])
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


@app.route("/reports",
           methods=['GET', 'POST'])
@login_required
def reports():
    page = request.args.get('page', 1, type=int)
    reports = Report.query.filter_by(user=current_user)\
                    .order_by(Report.date.desc())\
                    .paginate(page=page, per_page=5)
    return render_template('reports.html',
                           reports=reports,
                           title='My reports')


@app.route("/report/new",
           methods=['GET', 'POST'])
@login_required
def new_report():
    form = ReportForm()
    if form.validate_on_submit():
        # new_report = aux(form.data) function that creates the pdf report
        # form.model.data = id of the model
        # save it in the database
        model = FRS.query.filter_by(id=form.model.data).first()
        report = Report(model=model, user=current_user)
        db.session.add(report)
        db.session.commit()
        flash("Report created!", 'success')
        return redirect(url_for('history'))

    return render_template('new_report.html',
                           title='New Report',
                           form=form)


@app.route("/report/<int:report_id>")
@login_required
def report(report_id):
    report = Report.query.get_or_404(report_id)
    return render_template('report.html', report=report)


@app.route("/report/<int:report_id>/delete", methods=['POST'])
@login_required
def delete_report(report_id):
    report = FRS.query.get_or_404(report_id)
    if report.user != current_user:
        abort(403)  # forbidden route
    # remove_report(report.file_path)
    db.session.delete(report)
    db.session.commit()
    flash('Your report has been deleted!', 'success')
    return redirect(url_for('reports'))
