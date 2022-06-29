import os

from flask import request, jsonify
from werkzeug.utils import secure_filename

from server import app, detector
from server.functions import allowed_file
from common.exceptions import TextDetectionException

@app.route('/api/detect_text', methods=['POST'])
def upload_photo_api():
    """
    Upload a single photo and receive a json with detected text.

    files = {'image': open('image_1.jpg', 'rb')}
    """
    image = request.files.get('image', None)
    if image and allowed_file(image.filename):
        filename = secure_filename(image.filename)
        app.logger.info(f'Processing {filename}')

        try:
            annotations = detector.process_image(image)
        except TextDetectionException as e:
            return jsonify({'reason': str(e)}), 400

        # Remove the raw_output which is not a jsonifable object
        # TODO modify and return?
        del annotations['raw_output']

        # Return the text annotations
        return annotations, 200
    else:
        app.logger.warning('No image received')
        return jsonify({'reason': 'No image received'}), 400
