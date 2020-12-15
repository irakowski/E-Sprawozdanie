from django import forms
from django.contrib.staticfiles.storage import staticfiles_storage
from django.utils.translation import gettext as _
import os
import xmlschema
from xmlschema.validators import exceptions
from .validators import MimetypeValidator

def handle_upload(file_in_memory):
    xml_text = ''
    for line in file_in_memory:
        xml_text = xml_text + line.decode()
    return xml_text


class UploadFinancialStatementForm(forms.Form):
    """
    Form for uploading XML files. 
    Only allows for XML to be specified for upload throught accept attribute
    Checks file extention with clean_file method
    Validates MIME type of the file throught Mimetypevalidator
    """

    ALLOWED_TYPES = ['xml']
    
    file = forms.FileField(label='XML File Upload:', required=True, 
                           widget=forms.FileInput(attrs={'accept': 'application/xml, text/xml'}), 
                           validators=[MimetypeValidator(['text/xml','application/xml'])]
                           )

    def clean_file(self):
        file = self.cleaned_data.get('file', None)
        content = handle_upload(file)
        #xsd_file = staticfiles_storage.path('esfviewer/files/JednostkaInnaWTysiacach_v1-0.xsd')
        #xsd_file_3 = staticfiles_storage.path('esfviewer/files/JednostkaInnaWTysiacach_v1-2.xsd')
        xsd_file = 'ESFViewer/static/esfviewer/files/JednostkaInnaWTysiacach_v1-0.xsd'
        xsd_file_3 = 'ESFViewer/static/esfviewer/files/JednostkaInnaWTysiacach_v1-2.xsd'
        schema_v10 = xmlschema.XMLSchema(xsd_file)
        schema_v12 = xmlschema.XMLSchema(xsd_file_3)
        try:
            schema_v10.validate(content)
        except exceptions.XMLSchemaChildrenValidationError:
            pass #Signature is ignored
        except exceptions.XMLSchemaException:
            try:
                schema_v12.validate(content)
            except exceptions.XMLSchemaChildrenValidationError as err:
                pass
            except exceptions.XMLSchemaException as e:
                raise forms.ValidationError('Provided XML does not match structure for Inna Jednostka')
        return file
    
    def clean(self):
        super().clean()
        file = self.cleaned_data.get('file', None)
        if not file:
            raise forms.ValidationError(_('Missing file'))
        try:
            extension = os.path.splitext(file.name)[1][1:].lower()
            if extension in self.ALLOWED_TYPES:
                return file
            else:
                raise forms.ValidationError(_('File type is not allowed'))
        except Exception as e:
            raise forms.ValidationError(_('Can not identify file type'))