"""
Handles images and uses OCR models to detect and extract text
"""
import json
import keras_ocr
import threading
import time
import traceback
from pathlib import Path
from werkzeug.datastructures import FileStorage

from common.exceptions import TextDetectionException

__author__ = "Dale Wahl"
__credits__ = ["Dale Wahl"]
__maintainer__ = "Dale Wahl"
__email__ = "4cat@oilab.eu"


class ImageTextDetector():
    """
    Image Text Detection

    This processor uses Optical Character Recognition (OCR) to first detect
    areas of an image that may contain text with the pretrained Character-Region
    Awareness For Text (CRAFT) detection model and then attempts to predict the
    text inside each area using Keras' implementation of a Convolutional
    Recurrent Neural Network (CRNN) for text recognition. Once words are
    predicted, an algorythm attempts to sort them into likely groupings based
    on locations within the original image.
    """
    def __init__(self, log):
        # Load models
        # keras-ocr will automatically download pretrained
        # weights for the detector and recognizer.
        self.pipeline = keras_ocr.pipeline.Pipeline()
        self.log = log

    def process_image(self, image_file):
        """
        Take image, return text!
        """
        filename = self.get_image_filename(image_file)
        try:
            image = self.preprocess_image(image_file)
        except Exception as e:
            raise TextDetectionException("Unable to read image %s: %s" % (filename, str(e)))

        annotations = self.annotate_image(image)
        annotations = {"filename": filename, **annotations}

        return annotations

    def preprocess_image(self, image_file):
        """
        Do any preprocessing of image that is needed.
        """
        self.log.debug("Reading image %s" % self.get_image_filename(image_file))
        if type(image_file) == Path:
            preprocessed_image = keras_ocr.tools.read(str(image_file))
        elif type(image_file) == FileStorage:
            preprocessed_image = keras_ocr.tools.read(image_file)
        else:
            # Might as well try...
            preprocessed_image = keras_ocr.tools.read(image_file)
        return preprocessed_image

    def annotate_image(self, image):
        """
        Get text from models

        :param Path image_file:  Path to file to annotate
        :param keras_ocr.pipeline pipeline:  Pipeline to run images through
        :return dict:  List of word groupings
        """
        self.log.debug("Making predictions")
        predictions = self.pipeline.recognize([image])[0]

        if predictions:
            self.log.debug("Grouping text")
            text_groups = self.create_text_groups(predictions)
            self.log.debug("Removing position information")
            text = self.remove_positional_information(text_groups)
            return {'simplified_text' : text, 'raw_output': predictions}
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
        texts = [SimpleBox(text) for text in text_from_image]
        # could sort texts by finding min of right bottom point (x + y) or, like, pythagorean theorem

        row_groups = []
        while texts:
            # grab first word
            text = texts[0]

            # collect all text on same "line"
            temp_row = [j for j in texts if abs(text.bottom - j.bottom) <= text.height/2]

           # sort the list in place in order of left to right
            temp_row.sort(key=lambda x: x.left, reverse=False)

            # Find large breaks within words
            # Initialize new list with first word
            temp_row_2 = [temp_row[0]]
            # Loop through rest of words in temp_row
            for index, word in enumerate(temp_row[1:]):
                # Is word close to previous?
                if abs(word.left - temp_row[index].right) < text.height/2:
                    temp_row_2.append(word)
                else:
                    break

            # add word group to collection
            row_groups.append(temp_row_2)
            # remove those words from possible words
            [texts.pop(texts.index(word)) for word in temp_row_2]

        # Now to check if rows are near each other... somehow...
        rows = [BigBox(row) for row in row_groups]

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
        text['groupings'] = [[[word.word for word in line.original] for line in group] for group in text_groups]
        text['raw_text'] = '\n\n'.join(['\n'.join([' '.join([word.word for word in line.original]) for line in group]) for group in text_groups])
        return text

    def get_image_filename(self, image):
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

class SimpleBox():
    """
    This class reorganizes words to find location attributes
    """
    def __init__(self, stupid_box):
        self.word = stupid_box[0]
        self.top = min([i[1] for i in stupid_box[1]])
        self.left = min([i[0] for i in stupid_box[1]])
        self.bottom = max([i[1] for i in stupid_box[1]])
        self.right = max([i[0] for i in stupid_box[1]])
        self.height = self.bottom - self.top

class BigBox():
    """
    Similarly to SimpleBox, this represents a grouping of many SimpleBoxes
    """
    def __init__(self, list_of_simple_boxes):
        self.original = list_of_simple_boxes
        self.top = min([i.top for i in list_of_simple_boxes])
        self.left = min([i.left for i in list_of_simple_boxes])
        self.bottom = max([i.bottom for i in list_of_simple_boxes])
        self.right = max([i.right for i in list_of_simple_boxes])
        self.height = self.bottom - self.top
        self.center = ((self.right - self.left)/2) + self.left
