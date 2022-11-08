"""
Handles images and uses OCR models to detect and extract text
"""
from ocr_detection.keras_ocr_model import KerasOCRPipeline

from common.exceptions import TextDetectionException, OCRModelTypeNotAvailableException
from common.helper_functions import get_image_filename

__author__ = "Dale Wahl"
__credits__ = ["Dale Wahl"]
__maintainer__ = "Dale Wahl"
__email__ = "4cat@oilab.eu"


class ImageTextDetector:
    """
    Image Text Detection

    Handles text detection for different loaded models.
    """
    def __init__(self, log):
        self.log = log

        # Load models
        self.keras_ocr = KerasOCRPipeline(self.log)

    def get_model(self, model_type):
        """
        Select model
        """
        # if model_type == 'paddle_ocr':
        #     return self.paddle_ocr
        if model_type == 'keras_ocr':
            return self.keras_ocr
        else:
            raise OCRModelTypeNotAvailableException('Model type "%s" not available' % model_type)

    def process_image(self, image_file, model_type):
        """
        Take image, return text!
        """
        filename = get_image_filename(image_file)
        model = self.get_model(model_type)

        try:
            image = model.preprocess_image(image_file)
        except TextDetectionException as e:
            raise TextDetectionException("Unable to read image %s: %s" % (filename, str(e)))

        annotations = model.annotate_image(image)
        annotations = {"filename": filename,
                       'model_type': model_type,
                       **annotations}

        return annotations
