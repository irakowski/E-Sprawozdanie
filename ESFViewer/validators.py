from django.core.exceptions import ValidationError
import magic
import xmlschema
from pathlib import Path
from xmlschema.validators import exceptions
from esprawozdanie import settings

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


def xsd_check(xml_text):
    valid = True
    xsd_file = str(Path.home().joinpath('Downloads', 'JednostkaInnaWTysiacach.xsd'))
    xsd_file_3 = str(Path.home().joinpath('Downloads','JednostkaInnaWTysiacach(1)_v1-2.xsd'))
    schema_old = xmlschema.XMLSchema(xsd_file)
    schema_new = xmlschema.XMLSchema(xsd_file_3)
    try:
        schema_old.validate(xml_text)
    except exceptions.XMLSchemaChildrenValidationError as err:
        #Expected Reason: Unexpected child with tag '{http://www.w3.org/2000/09/xmldsig#}Signature' at position 8.
        pass
    except exceptions.XMLSchemaException as error:
        valid = False
        try:
            schema_new.validate(xml_text)
            valid = True
        except exceptions.XMLSchemaChildrenValidationError as err:
            valid = True
            pass
        except exceptions.XMLSchemaException as e:
            valid = False

    return valid