"""
Handles images and uses OCR models to detect and extract text
"""
import os

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
    def __init__(self, logger, temp_image_dir=None):
        self.log = logger
        self.temp_image_dir = temp_image_dir

        # Load models
        # We are loading here as it can be time consuming in general and, for the first run, needs to download models
        self.keras_ocr = None
        self.paddle_ocr = None

    def get_model(self, model_type):
        """
        Select model
        """
        if model_type == 'paddle_ocr':
            if self.paddle_ocr is None:
                from ocr_detection.paddle_ocr_model import PaddlesOCRPipeline
                self.paddle_ocr = PaddlesOCRPipeline(self.log)
            return self.paddle_ocr
        if model_type == 'keras_ocr':
            if self.keras_ocr is None:
                from ocr_detection.keras_ocr_model import KerasOCRPipeline
                self.keras_ocr = KerasOCRPipeline(self.log)
            return self.keras_ocr
        else:
            raise OCRModelTypeNotAvailableException('Model type "%s" not available' % model_type)

    def process_image(self, image_file, model_type, local=False):
        """
        Take image, return text!

        :param image_file:  Image file to process
        :param model_type:  Model to use
        :param local:  If True, image_file is a local file path; False, it is a requests file stream
        """
        filename = get_image_filename(image_file)
        model = self.get_model(model_type)
        results = {"filename": filename,
                   'model_type': model_type}

        if model_type == 'paddle_ocr' and not local:
            if self.temp_image_dir:
                # Must download image first
                image_file.save(os.path.join(self.temp_image_dir, filename))
                image_file = os.path.join(self.temp_image_dir, filename)
            else:
                raise TextDetectionException('Paddle OCR requires a temporary image download folder to be set')

        try:
            image = model.preprocess_image(image_file)
        except TextDetectionException as e:
            annotations = {"success": False, "error": str(e)}
            results.update(annotations)
            return results

        try:
            annotations = model.annotate_image(image)
            annotations["success"] = True
        except TextDetectionException as e:
            # No text found
            annotations = {"success": False, "error": str(e)}

        results.update(annotations)
        return results
