"""
paddle_ocr python package used to detect text in images
"""
from paddleocr import PaddleOCR
from pathlib import Path
import os

from common.exceptions import TextDetectionException
from common.helper_functions import get_image_filename

__author__ = "Dale Wahl"
__credits__ = ["Dale Wahl"]
__maintainer__ = "Dale Wahl"
__email__ = "4cat@oilab.eu"


class PaddlesOCRPipeline:
    """
    This processor uses the PaddleOCR package (https://github.com/PaddlePaddle/PaddleOCR#readme)
    to extract text from images.
    """
    def __init__(self, log):
        ## Paddleocr supports Chinese, English, French, German, Korean and Japanese.
        # You can set the parameter `lang` as `ch`, `en`, `fr`, `german`, `korean`, `japan`
        # to switch the language model in order.
        # TODO: how do we want to handle language parameter? Perhaps only load other language models if requested
        # TODO: download can cause Gunicorn timeout! It seems the worker restarts and picks up download on where it left off, but we may want to spin off a process for the first run to trigger downloads!
        self.ocr = PaddleOCR(use_angle_cls=True, lang='en') # need to run only once to download and load model into memory
        self.log = log

    def preprocess_image(self, image_file):
        """
        Do any preprocessing of image that is needed.
        """
        # No additional preprocessing
        return image_file

    def annotate_image(self, image):
        """
        Get text from models

        :param Path image_file:  Path to file to annotate
        :param keras_ocr.pipeline pipeline:  Pipeline to run images through
        :return dict:  List of word groupings
        """
        self.log.debug("Making predictions")
        # Currently making cls=False; found that cls=True can cause poor predictions for left to right text
        predictions = self.ocr.ocr(str(image), cls=False)

        # Remove temp image
        #

        if predictions[0]:
            self.log.debug("Grouping text")
            text_groups = self.create_text_groups(predictions[0])
            self.log.debug("Removing position information")
            text = self.remove_positional_information(text_groups)
            return {'simplified_text': text, 'raw_output': predictions}
        else:
            raise TextDetectionException("No predictions returned")

    def create_text_groups(self, text_from_image):
        """
        This function cycles through predicted words and groups them based on
        their location on the image. It first finds words likely to be in a
        horizontal row, orders theses and checks to see if there are any large
        spaces between them (breaking them appart if there are). It then
        examines each group to see if there is another row closely following and
        groups them together.

        Through testing, using the height of a word seems to generally allow for
        accurate groupings however the size of text does not always correspond
        so neatly with the spacing between words and lines. Also of note: this
        method of grouping will not work with non horizontal words/rows.
        """
        # Now to check if rows are near each other... somehow...
        rows = [BigBox(row) for row in text_from_image]

        text_groups = []

        while rows:
            matching_row = rows[0]

            group = [matching_row]
            for new_row in rows[1:]:
                # is top of new_row near bottom of our row?
                if (new_row.top - matching_row.bottom) < (matching_row.height*.75):
                    # and is center of row within the margins of our row?
                    if  matching_row.left < new_row.center < matching_row.right:
                        group.append(new_row)
                        matching_row = new_row

            text_groups.append(group)
            # remove those rows from possible rows
            [rows.pop(rows.index(row)) for row in group]

        return text_groups

    def remove_positional_information(self, text_groups):
        """
        Takes the result from create_text_groups and returns only the text.

        TODO: build this object in the create_text_groups function to prevent
        this double loop.
        """
        text = {}
        text['groupings'] = [[line.original[1][0] for line in group] for group in text_groups]
        text['raw_text'] = '\n\n'.join(['\n'.join([line.original[1][0] for line in group]) for group in text_groups])
        return text


class BigBox():
    """
    Similarly to SimpleBox, this represents a grouping of many SimpleBoxes
    """
    def __init__(self, grouped_row):
        self.original = grouped_row

        bounding_box = grouped_row[0]
        self.top = min([i[1] for i in bounding_box])
        self.left = min([i[0] for i in bounding_box])
        self.bottom = max([i[1] for i in bounding_box])
        self.right = max([i[0] for i in bounding_box])
        self.height = self.bottom - self.top
        self.center = ((self.right - self.left)/2) + self.left
