import os
import secrets
from flask import current_app, request
from PIL import Image


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


def save_image(form_image):
    """Compress and save user-uploaded images to the filesystem.

    Parameters
    ----------
    form_image : [image]
        User-uploaded profile picture.

    Returns
    -------
    [image_fn]
        File name of resized image as it is saved on filesystem.
    """
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_image.filename)
    image_fn = random_hex + f_ext
    image_path = os.path.join(current_app.root_path,
                              'static/profile_pictures',
                              image_fn)

    output_size = (125, 125)
    i = Image.open(form_image)
    i.thumbnail(output_size)

    i.save(image_path)

    return image_fn


def save_temp(form_image):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_image.filename)
    image_fn = random_hex + f_ext
    image_path = os.path.join(current_app.root_path,
                              'static/tmp',
                              image_fn)

    i = Image.open(form_image)
    i.save(image_path)

    return image_fn
