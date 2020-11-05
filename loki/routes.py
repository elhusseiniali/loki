from flask import render_template, flash, redirect, url_for, request
from loki import app, db, bcrypt
from loki.forms import RegistrationForm, LoginForm, ReportForm, FRSForm
from loki.models import User, Report, FRS

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

        flash(f'Account created! You can now log in.', 'success')
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

attacks=['attack1','attack2','attack3','attack4','attack5','attack6','attack7']


@app.route("/logout",
           methods=['GET'])
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/history",
           methods=['GET', 'POST'])
@login_required
def history():
	page = request.args.get('page', 1, type=int)
	models = FRS.query.filter_by(user=current_user)\
				.order_by(FRS.upload_date.desc())\
				.paginate(page=page, per_page=5)
	
	return render_template('history.html',
						   title='History',
						   models=models,
						   attacks = attacks)
@app.route("/models",
           methods=['GET', 'POST'])
@login_required
def models():	
	return render_template('models.html',
						   title='My models')
						   
@app.route("/reports",
           methods=['GET', 'POST'])
@login_required
def reports():	
	return render_template('reports.html',
						   title='My models')
						   						   
						   
@app.route("/report",
		   methods=['GET', 'POST'])
@login_required						   
def report():
	form = ReportForm()
	if form.validate_on_submit():
		print(form.data)
		#new_report = aux(form.data) function that creates the pdf report
		#form.model.data = id of the model
		#save it in the database
		flash("Report created!", 'success')
		return redirect(url_for('history'))

	return render_template('new_report.html',
						   title='New Report',
						   attacks=attacks,
						   form=form)
						   
						   
@app.route("/new_model",
           methods=['GET', 'POST'])
@login_required
def new_model():
	form = FRSForm()
	if form.validate_on_submit():
		#new_report = aux(form.data) function that creates the pdf report
		frs = FRS(name=form.name.data, user=current_user)
		db.session.add(frs)
		db.session.commit()

		flash(f'Model uploaded! You can now launch report for it !', 'success')
		return redirect(url_for('report'))
		
		
	return render_template('new_model.html',
						   title='New Model',
						   form = form)

