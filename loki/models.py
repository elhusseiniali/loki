from datetime import datetime
from loki import db, login_manager
from flask_login import UserMixin
from sqlalchemy_utils import EmailType


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(EmailType)
    password = db.Column(db.String(60), nullable=False)
    models = db.relationship('FRS', backref='author', lazy=True)
    
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

    def __repr__(self):
        return (f"User('{self.username}')")
        
class FRS(db.Model): #Facial Recognition System
	id = db.Column(db.Integer, primary_key=True) 
	name = db.Column(db.String(100), nullable=False)
	date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	model_file = db.Column(db.String(20), nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) #'user.id' refers to the column name
	
        
	def __repr__(self):
		return f"User('{self.title}', '{self.date_posted}')"