
class Config:
    SECRET_KEY = '60808326457a6384f78964761aaa161c'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    # This is to suppress SQLAlchemy warnings
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASK_ADMIN_SWATCH = 'flatly'
