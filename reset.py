from loki import create_app, db

app = create_app()

db.init_app(app)

with app.app_context():
    db.drop_all()
    db.create_all()
