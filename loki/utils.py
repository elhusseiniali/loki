import os
import secrets
from flask import current_app, request

def save_model(form_model):
	random_hex = secrets.token_hex(8)
	_, f_ext = os.path.splitext(form_model.filename)
	model_fn = random_hex + f_ext
	model_path = os.path.join(current_app.root_path, 'static/models', model_fn)
	form_model.save(model_path)
	return model_path

def remove_model(model_path):
	if os.path.exists(model_path):
	  os.remove(model_path)