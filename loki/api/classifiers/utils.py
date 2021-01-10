import os
import secrets
from flask import current_app


def save_model(form_model):
    """Save user-uploaded model file under /static/models.

    Parameters
    ----------
    form_model : [file]

    Returns
    -------
    [str]
        A random hex is generated as the new file name to prevent
        any errors that would arise on the filesystem when filename uniqueness
        is violated.
    """
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_model.filename)
    model_fn = random_hex + f_ext
    model_path = os.path.join(current_app.root_path, 'static/models', model_fn)
    form_model.save(model_path)
    return model_path


def remove_model(model_path):
    """Remove file at model_path.

    Parameters
    ----------
    model_path : [str]
    """
    if os.path.exists(model_path):
        os.remove(model_path)
