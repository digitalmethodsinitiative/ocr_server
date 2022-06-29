import os
import uuid

from flask import jsonify, abort, send_file, render_template
from werkzeug.utils import secure_filename

from server import app, ALLOWED_EXTENSIONS

def allowed_file(filename, extensions=ALLOWED_EXTENSIONS):
    """
    Check filenames to ensure they are an allowed extension
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in extensions

def dir_listing(base_dir, req_path, template):
    # Joining the upload folder and the requested path
    abs_path = os.path.join(base_dir, req_path)

    # Return 404 if path doesn't exist
    if not os.path.exists(abs_path):
        return abort(404)

    # Check if path is a file and serve
    if os.path.isfile(abs_path):
        return send_file(abs_path)

    # Show directory contents
    files = os.listdir(abs_path)
    current_dir = req_path.split('/')[-1]
    return render_template(template, files=files, current_dir=current_dir)
