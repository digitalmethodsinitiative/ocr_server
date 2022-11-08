class OCRServerException(Exception):
	pass

class OCRDetectionException(OCRServerException):
	"""
	General Error during OCR Detection
	"""
	pass

class OCRModelTypeNotAvailableException(OCRServerException):
	"""
	Model Type not available
	"""
	pass

class TextDetectionException(OCRDetectionException):
	"""
	Unable to detect text in image
	"""
	pass
