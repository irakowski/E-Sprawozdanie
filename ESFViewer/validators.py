from django.core.exceptions import ValidationError
from django.contrib.staticfiles.storage import staticfiles_storage
import magic


class MimetypeValidator(object):

	def __init__(self, mimetypes):
		self.mimetypes = mimetypes
	
	def __call__(self, value):
		try:
			mime = magic.from_buffer(value.read(1024), mime=True)
			if not mime in self.mimetypes:
				raise ValidationError('%s is not an acceptable file type' % mime)
		except AttributeError as e:
			raise ValidationError('This value could not be validated for file type' % value)