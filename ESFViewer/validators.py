import magic
import re
import xml.etree.ElementTree as ET
import xmlschema
from django.core.exceptions import ValidationError
from django.contrib.staticfiles.storage import staticfiles_storage
from django.utils.translation import gettext as _
from esprawozdanie.settings import STATIC_ROOT


class MimetypeValidator:
	"""Validates uploaded file to match XML mimetype"""
	
	def __init__(self, mimetypes):
		self.mimetypes = mimetypes
	
	def __call__(self, value):
		try:
			#identifies file types by checking their headers.
			mime = magic.from_buffer(value.read(2048), mime=True)
			if not mime in self.mimetypes:
				raise ValidationError(_('%(mime)s is not an acceptable file type'), params={'mime': mime})
		except AttributeError as e:
			raise ValidationError(_('%(value)s could not be validated for file type'), params={'value': value})


class DocumentPreProcessing:
	
	"""Pre-processing file to validate against xsd"""

	AVAILABLE_TYPES = (
		'JednostkaInnaWTysiacach',
		'JednostkaInnaWZlotych', 
		'JednostkaMalaWZlotych', 
		'JednostkaMalaWTysiacach', 
		'JednostkaMikroWZlotych', 
		'JednostkaMikroWTysiacach', 
		'JednostkaOpWZlotych', 
		'JednostkaOpWTysiacach'
	)
    
	def __init__(self, xml_string):
		
		self.xml_string = xml_string
		#Checking for parsing Errors
		try:
			root = ET.fromstring(self.xml_string)
		except ET.ParseError as e:
			raise ValueError('Cannot build object from the invalid file')

		#checking if parsing of a given document is supported                
		if self.get_doc_type() in self.AVAILABLE_TYPES and not None:
			self.doc_type = self.get_doc_type()
		else:
			raise ValueError('Invalid document type')
        
		#verifying document schema
		if self.get_schema_version() is not None:
			self.schema_version = self.get_schema_version()
		else:
			raise ValueError('Unsupported Schema Version')
	
	def get_root(self):
		return ET.fromstring(self.xml_string)
	
	def get_doc_type(self):
		"""
		Searches XML-root for document type declaration
		Returns None if no mathes found
		"""
		root = str(self.get_root())
		pattern = r'/(\w+)}'
		doc_type = re.search(pattern, root)
		if doc_type is not None:
			return doc_type.group(1)
		return None
		
	def get_schema_version(self):
		"""
		constraints: First node must be
		'Naglowek', where the schema-version is defined.
		"""
		root = self.get_root()
		wersja = {}
		for child in root[0]:
			if child.attrib:
				wersja = child.attrib
		return wersja.get('wersjaSchemy', None)
	
	def get_xsd_file_path(self):
		"""
		Creates a path for xsd, given document_type and schema_version
		"""
		version = self.get_schema_version()
		doc_type = self.get_doc_type()
		##Requires checking against more casses
		if version == '1-0E':
			xsd_file = doc_type + '(1)_v1-0.xsd'
		else:
			xsd_file = doc_type + '(1)_v'+ version + '.xsd'
            
        #path = STATIC_ROOT + 'esfviewer/files/' + xsd_file
		path = '/home/michael/Desktop/venvs/e-sprawozdanie/E-Sprawozdanie/ESFViewer/static/esfviewer/files/' + xsd_file
		return path
		
	def validate_against_xsd(self):
		"""
		Returns True if xml document is valid against its xsd's, 
		False otherwise
		Catches any XMLShema errors, returning False as a validation result
		"""
		try:
			schema = xmlschema.XMLSchema(self.get_xsd_file_path())
		except:
			return False
		return schema.is_valid(self.xml_string)