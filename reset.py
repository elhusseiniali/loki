from loki import create_app, db


if __name__ == '__main__':
    app = create_app()
    db.init_app(app)

    with app.app_context():
        db.drop_all()
        db.create_all()
