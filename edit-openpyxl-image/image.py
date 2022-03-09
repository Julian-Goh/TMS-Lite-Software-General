# Copyright (c) 2010-2021 openpyxl

from io import BytesIO

try:
    import numpy as np
except ImportError:
    np = False

try:
    from PIL import Image as PILImage
except ImportError:
    PILImage = False


def _import_image(img):
    if not PILImage:
        raise ImportError('You must install Pillow to fetch image objects')

    if not np:
        raise ImportError('You must install Numpy to fetch image objects')

    if not isinstance(img, PILImage.Image):
        if isinstance(img, np.ndarray) == True:
            img = PILImage.fromarray(img)
        else:
            img = PILImage.open(img)

    return img


class Image(object):
    """Image in a spreadsheet"""

    _id = 1
    _path = "/xl/media/image{0}.{1}"
    anchor = "A1"

    def __init__(self, img):

        self.ref = img
        mark_to_close = isinstance(img, str)
        if mark_to_close == False:
            mark_to_close = isinstance(img, np.ndarray)

        image = _import_image(img)
        # print(image.load())
        self.width, self.height = image.size

        try:
            self.format = image.format.lower()
        except AttributeError:
            self.format = "png"

        if mark_to_close:
            # PIL instances created for metadata should be closed.
            image.close()


    def _data(self):
        """
        Return image data, convert to supported types if necessary
        """
        img = _import_image(self.ref)
        # don't convert these file formats
        if self.format in ['gif', 'jpeg', 'png']:
            try:
                img.fp.seek(0)
                fp = img.fp
            except Exception:
                fp = BytesIO()
                img.save(fp, format="png")
                fp.seek(0)
        else:
            fp = BytesIO()
            img.save(fp, format="png")
            fp.seek(0)

        # print(fp)

        return fp.read()


    @property
    def path(self):
        return self._path.format(self._id, self.format)
