import json
from flask import request, jsonify
from werkzeug.utils import secure_filename

from server import app, detector
from server.functions import allowed_file
from common.exceptions import TextDetectionException, OCRModelTypeNotAvailableException


@app.route('/api/detect_text', methods=['POST'])
def upload_photo_api():
    """
    Upload a single photo and receive a json with detected text.

    files = {'image': open('image_1.jpg', 'rb')}
    """
    # Select for model_type for detector
    request_data = request.form.to_dict()
    if request_data is None or 'model_type' not in request_data:
        # Default model_type
        model_type = app.config['DEFAULT_MODEL']
    else:
        model_type = request_data['model_type']

    image = request.files.get('image', None)
    if image and allowed_file(image.filename):
        filename = secure_filename(image.filename)
        app.logger.info(f'Processing {filename}')

        try:
            annotations = detector.process_image(image, model_type)
        except TextDetectionException as e:
            return jsonify({'reason': str(e)}), 400
        except OCRModelTypeNotAvailableException as e:
            return jsonify({'reason': str(e)}), 400
        except Exception as e:
            app.logger.error(str(e))
            return jsonify({'reason': 'Unable to process request'}), 500

        # Check that raw_output is a jsonifable object
        try:
            annotations['raw_output'] = json.dumps(annotations['raw_output'])
        except TypeError as e:
            if 'is not JSON serializable' in str(e):
                app.logger.warning('Model %s returning non JSON serializable objects: %s' % (model_type, str(e)))
            else:
                app.logger.error(e)
            del annotations['raw_output']

        # Return the text annotations
        return annotations, 200
    else:
        app.logger.warning('No image received')
        return jsonify({'reason': 'No image received'}), 400


@app.errorhandler(Exception)
def server_error(err):
    app.logger.exception(err)
    return err, str(err)[:3]
