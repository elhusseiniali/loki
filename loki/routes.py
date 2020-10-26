from flask import render_template, flash, redirect, url_for, request
from loki import app, db, bcrypt
from loki.forms import RegistrationForm, LoginForm, ModelForm, RunReportForm
from loki.models import User, FRS
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
        hashed_password = bcrypt.generate_password_hash(form.password.data)\
                                .decode('utf-8')
        user = User(username=form.username.data,
                    email=form.email.data,
                    password=hashed_password)
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
        if user and bcrypt.check_password_hash(user.password,
                                               form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page \
                else redirect(url_for('account'))
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




attacks = [
	{
	'name':"Attack 1",
	'type':"White Box",
	'complexity':"complexity 1",
	'description':"description 1 blablablablablablablabla"
	},
	{
	'name':"Attack 2",
	'type':"White Box",
	'complexity':"complexity 2",
	'description':"description 2 blablablablablablablabla"
	},
	{
	'name':"Attack 3",
	'type':"White Box",
	'complexity':"complexity 3",
	'description':"description 3"
	},
	{
	'name':"Attack 4",
	'type':"Black Box",
	'complexity':"complexity 4",
	'description':"description 4"
	},
	{
	'name':"Attack 5",
	'type':"Black Box",
	'complexity':"complexity 5",
	'description':"description 5"
	},
	{
	'name':"Attack 6",
	'type':"Black Box",
	'complexity':"complexity 6",
	'description':"description 6"
	},
	{
	'name':"Attack 6",
	'type':"Black Box",
	'complexity':"complexity 6",
	'description':"description 6"
	}
]


@app.route("/account",
		   methods=['GET', 'POST'])
@login_required
def account():
	page = request.args.get('page', 1, type=int)
	model_form = ModelForm()
	models = FRS.query.filter_by(author=current_user)\
				.order_by(FRS.date_posted.desc())\
				.paginate(page=page, per_page=5)
	run_report_forms = [RunReportForm() for model in models.items]
	run_report_forms = dict(zip(models.items, run_report_forms))

				
	if model_form.validate_on_submit() and model_form.data:
		print(model_form.data)
		print(model_form.model)
		frs = FRS(name=model_form.name.data, model_file=model_form.model.data.filename, author=current_user)
		db.session.add(frs)
		db.session.commit()
		flash('Your model has been added!','success')
		return redirect(url_for('account'))			
		
	for model in models.items:
		if run_report_forms[model].validate_on_submit():
			pass
			#function(model) #fonction that generates the report and saves it
	return render_template('account.html',
						   title='Account',
						   models=models,
						   model_form=model_form,
						   run_report_forms=run_report_forms,
						   attacks = attacks)
