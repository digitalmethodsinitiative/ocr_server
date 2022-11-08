from pathlib import Path
from werkzeug.datastructures import FileStorage


def get_image_filename(image):
    """
    Get filename for different types
    """
    if type(image) == Path:
        filename = image.name
    elif type(image) == FileStorage:
        filename = image.filename
    else:
        filename = 'unknown'
    return filename
