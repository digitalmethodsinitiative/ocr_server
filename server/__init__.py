from flask import Flask, abort, request
import logging
import os
import yaml

from ocr_detection.image_handler import ImageTextDetector

def update_config(config_filepath='config.yml'):
    # Import config options
    with open(config_filepath) as file:
        config_data = yaml.load(file, Loader=yaml.FullLoader)
    return config_data

# Import config options
config_data = update_config()

# Flask application instance
app = Flask(__name__)

# Set up logging if run by gunicorn
if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

# Log file
logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")
file_handler = logging.FileHandler(config_data.get('LOG_NAME'))
file_handler.setFormatter(logFormatter)
app.logger.addHandler(file_handler)
levels = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
    "FATAL": logging.FATAL
}
app.logger.setLevel(levels[config_data.get('LOG_LEVEL', 'INFO')])

# # Test logs
# app.logger.debug('this is a DEBUG message')
# app.logger.info('this is an INFO message')
# app.logger.warning('this is a WARNING message')
# app.logger.error('this is an ERROR message')
# app.logger.critical('this is a CRITICAL message')

# Config app
app.secret_key = config_data.get('FLASK_SECRET_KEY')
# Set upload folder
path = os.getcwd()
app.config['IMAGE_FOLDER'] = os.path.join(path, 'images')

# Limit size of upload; 16 * 1024 * 1024 is 16 megabytes
#app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Allowed upload extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


@app.before_request
def limit_remote_addr():
    """
    Checks the incoming IP address and compares with whitelist
    """
    config_data = update_config()
    trusted_proxies = config_data.get('TRUSTED_PROXIES')
    ip_whitelist = config_data.get('IP_WHITELIST')

    if ip_whitelist:
        # # Allow all to view plots
        # if "/plots/" in request.path:
        #     return

        # Check that whitelist exists
        route = request.access_route + [request.remote_addr]
        remote_addr = next((addr for addr in reversed(route) if addr not in trusted_proxies), request.remote_addr)
        app.logger.debug('remote_address: '+str(remote_addr))
        if remote_addr not in ip_whitelist:
            abort(403)  # Forbidden
    else:
        # No whitelist = access for all
        return

# Set default OCR model
app.config['DEFAULT_MODEL'] = config_data.get('DEFAULT_MODEL', 'paddleocr')

# Instantiate our OCR detector
detector = ImageTextDetector(app.logger)

# Import flask API endpoints
import server.api

if __name__ == "__main__":
    # Flask started directly
    print('Starting server...')
    app.run(host='0.0.0.0', debug=True)
else:
    # Gunicorn starting server
    app.logger.info('Starting server...')
