![build](https://github.com/elhusseiniali/loki/workflows/build/badge.svg)
[![Coverage Status](https://coveralls.io/repos/github/elhusseiniali/loki/badge.svg?branch=master)](https://coveralls.io/github/elhusseiniali/loki?branch=master)

#  loki
##  Table of contents
*  [Introduction](#introduction)
*  [Setup](#setup)
*  [Features](#features)
*  [Design and Structure](#design-and-structure)
*  [Extra](#extra)

##  Introduction
Loki is a flask app built to provide a friendly UI to use [Foolbox](https://foolbox.readthedocs.io/en/stable/) with some facial recognition systems.
The project aims to provide some user-friendly visualizations for different attacks and some useful metrics on the robustness of facial recognition systems.
It is being developed for the Software Engineering course (M1) given at ENS Paris-Saclay in 2020-2021.

##  Setup
We recommend using Python 3.6 or newer.
You will have to create your own virtual environment [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv) is a great option for that. You will need to install the
requirements using `pip install -r requirements.txt` (use pip3 if you aren't using pyenv). 

If this is your first time running the project, you will need to instantiate an empty database using
`python reset.py`.


You can run the app using `python run.py`. The terminal will show you what address to use to visit the app in a modern browser (usually it is something like localhost:5000/ or localhost:5001/).


You can access the admin panel by going to the `/admin` path (e.g. localhost:5000/admin).
You can access the API doc page by going to the `/api/1` path (e.g. localhost:5000/api/1). This page has Swagger UI documentation for every function in the API, as well as a Postman-like interface to allow you to test it out. Note that the app has to be running for this to actually work.


## Features
1. Classification: We have provided 6 classifiers, pretrained on [the ImageNet dataset](https://ieeexplore.ieee.org/document/5206848). These classifiers are listed on the homepage (localhost:5000/home), and they can be accessed either via the classification view (localhost:5000/classifiers/classify), or via the API. The API has a few extra endpoints to display information on the included classifiers (their names and their research papers). The API endpoint is listed in [Setup](#setup).
2. Attacks: We have included 7 different adversarial attacks. They have all been tested on all the included classifiers. The attacks can be accessed as follows:
..* Directly: via the Visualize Attack view (localhost:5000/attacks/visualize), or via the API (you can run an attack, get a list of all attacks, and get information on a specific attack given its ID).
..* Indirectly: via the New Report view, described next.
3. Reports: We included a view to generate a new report (localhost:5000/reports/new). This basically runs a classifier on a set of images, then runs an attack on the same set to get a set of adversarial images, displays pixel differences between the images before and after the attack, and then displays a confusion matrix to show how the classification changed. Unfortunately, we did not have time to store reports and commit them to the database, so for now, they only live in RAM. Some sample reports (as PDF files) can be found under `loki/static/`. A feature of the reports when generated in-app is that the confusion matrix can be manipulated (because of [Plotly](plotly.com)), e.g. zoom in/out, select some classes to display, et cetera...
4. Datasets: We included an API endpoint to display information on the datasets present (we only have ImageNet, but adding a new one is very easy because of the modular structure we used). Another API endpoint allows the user to get all the labels found in a given dataset, and another one allows the user to get a human-readable label from a class index (e.g. the user inputs class index 1 and gets back 'gold fish').
5. Users: We included basic login/registration views for users, in addition to some basic features (change email, change username, change profile picture). We also included API endpoints to add new users, get a list of all users, and delete users.

## Design and Structure
1. For the API: We used flask blueprints to separate the different components (e.g. one blueprint for classifiers, another for attacks...). We used re-usable classes to allow the different models to interact (e.g. a ClassifierField that can be used in any other form simply by importing it from the classifier blueprint).
2. Data Access Objects: We built DAOs for some of the classes that we have (like datasets, reports, users). This meant that all database access (for users and reports) and all file access (for the datasets) was handled by a DAO. Two example operations are "add" (to add a new object to the database) and "get_by_id" (to fetch an object by its ID). We also made sure that every DAO could only be instantiated once (i.e. we used the Singleton Pattern; the benefit of this is it allows us to avoid race conditions when there are multiple users).
3. Services: on top of the DAOs, we built services to provide an abstraction over the basic operations defined in a DAO, to allow for more complex operations (like updating an object, create a new object, etc...). The services leveraged the DAOs. This provided an extra layer of abstraction, to allow developers who want to use our library/API to do so safely, i.e. we had full control over what sort of operations were exposed to the developers (so the views did not need to import the database directly anymore, and possibly delete everything we had...). Like DAOs, we used the Singleton Pattern for services.
4. Application Factory: our app uses an Application Factory. All of the initialization steps required for the different libraries we use and some application setup steps are taken care of here. This streamlines the creation of the app and allows configurations to be easily imported based on what sort of server we wanted to run on.
5. Configuration: inside `config.py`, we have two configurations: one for testing (i.e. when tests are run), and one to actually use the app. The benefit of this is that all operations that happen when we run our test suite would not affect the database we used while development at all. To build on this and the previous point: if we wanted to deploy to Heroku, we would just create a new configuration class inside `config.py`, and then we would import it in our application factory, and everything would be ready.
6. Errors: we provided a blueprint for custom error handling. For now, this just provides custom HTML pages, but the fact that it is a blueprint means that its modularity can be used to change whatever we want and handle errors however we want.
7. Template inheritance via Jinja: Flask comes with a wonderful templating engine called [Jinja2](https://jinja2docs.readthedocs.io/en/stable/). We used this to define a basic template for all of our HTML pages (`layout.html`), and then every page we created would just inherit the layout we defined. This assured some seamlessness into the design of the entire frontend. 

## Extra
We provided some data to test out the app (some images, found under  `loki/static/data`).
