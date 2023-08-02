from pathlib import Path
from werkzeug.datastructures import FileStorage
from collections.abc import MutableMapping
import numpy as np

def get_image_filename(image):
    """
    Get filename for different types
    """
    if type(image) == Path:
        filename = image.name
    elif type(image) == FileStorage:
        filename = image.filename
    elif type(image) == str:
        filename = Path(image).name
    else:
        filename = "unknown"
    return filename


def make_jsonifiable(d: MutableMapping):
    """
    Return a dictionary where all nested sets and ndarray have been converted to lists.
    Also checks np.float32 and converts them view their .item() method.

    Note: there is probably other crap I haven't run into yet

    :param MutableMapping d:  Dictionary like object
    :return dict:  A new dictionary with the no nested sets
    """
    iterable_item_types = (tuple, list, set, np.ndarray)
    value_item_types = (np.float32)

    def _check_list(l):
        # Check list for items to update
        new_list = [make_jsonifiable(item) if isinstance(item, MutableMapping) else _check_list(item) if isinstance(item, iterable_item_types) else item.item() if isinstance(item, value_item_types) else item for item in l]

        if isinstance(l, tuple):
            return tuple(new_list)
        else:
            return new_list

    def _sets_to_lists_gen(d):
        # Check dictionary values to update
        for k, v in d.items():
            if isinstance(v, MutableMapping):
                yield k, make_jsonifiable(v)
            elif isinstance(v, iterable_item_types):
                yield k, _check_list(v)
            else:
                yield k, v.item() if isinstance(v, value_item_types) else v

    return dict(_sets_to_lists_gen(d))
