from PIL import Image, ImageOps
import os

"""This file is supposed to have all the attacks we want
to support.
Because of some problems that happened, we couldn't have
an actual attack implemented. Because of this, we wrote a quick
function that changes the input image to a grayscale version of it.

The same design will hold for attacks: we just have to change the
function in routes.py and we would be done.
"""


def gray(image_path):
    """Save grayscale copy of image at image_path.

    Parameters
    ----------
    image_path: [str]

    Returns
    -------
    gray_name: [str]
        Name of the new saved file.
    """
    old_image = Image.open(image_path)
    gray_image = ImageOps.grayscale(old_image)

    image_name = os.path.basename(image_path)
    gray_name = "GRAY" + image_name

    path = image_path.replace(image_name, gray_name)

    gray_image.save(path)

    return gray_name
