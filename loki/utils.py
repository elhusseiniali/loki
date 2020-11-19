import os
import secrets
from flask import current_app, request
from PIL import Image


def save_model(form_model):
    """Save model file under /static/models.

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


def save_image(source_image, path, output_size=(125, 125)):
    """Compress and save user-uploaded images to the filesystem.

    Parameters
    ----------
    source_image : [image]
        User-uploaded image.
    path: [string]
        Base dir to save image.
    output_size : tuple, optional
        Desired output size, default is (125, 125).

    Returns
    -------
    [image_fn]
        File name of resized image as it is saved on filesystem.
    """
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(source_image.filename)

    image_fn = random_hex + f_ext
    image_path = os.path.join(current_app.root_path,
                              'static/' + path,
                              image_fn)

    i = compress_image(source_image, output_size)
    i.save(image_path)

    return image_fn


def compress_image(image, output_size=(125, 125)):
    """Compress input image.

    Parameters
    ----------
    image : [image]
        Any valid image.
    output_size : tuple, optional
        Desired output size, default is (125, 125).

    Returns
    -------
    [i]
        Compressed image.
    """
    i = Image.open(image)
    i.thumbnail(output_size)
    return i
