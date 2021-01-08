import os
from django import forms
from django.contrib.staticfiles.storage import staticfiles_storage
from django.utils.translation import gettext as _
from xmlschema.validators import exceptions
from . import validators

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
                           validators=[validators.MimetypeValidator(['text/xml','application/xml'])]
                           )

    def clean(self):
        """Extra form-wide cleaning after Field.clean() has been
        called on every field."""
        cleaned_data = super().clean()
        file = cleaned_data.get('file', None)
        if not file:
            raise forms.ValidationError(_('Missing file'))
        try:
            extension = os.path.splitext(file.name)[1][1:].lower()
            if extension in self.ALLOWED_TYPES:
                return file
            else:
                raise forms.ValidationError(_('File type is not allowed'))
        except Exception as e:
            raise forms.ValidationError(_('Cannot identify file type'))
        return file

    def clean_file(self):
        """
        Validate uploaded file against any parsing Errors and xsd schema 
        """
        file = self.cleaned_data.get('file', None)
        content = handle_upload(file)
        try:
            xml = validators.DocumentPreProcessing(content)
        except ValueError as e:
            raise forms.ValidationError(_('Can\'t parse provided XML'))
        
        if not xml.validate_against_xsd():
            raise forms.ValidationError(_('Document doesn\'t match available schemas'))
        
        return file