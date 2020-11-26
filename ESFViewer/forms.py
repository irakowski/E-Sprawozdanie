from django import forms
import os
from .validators import MimetypeValidator


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
                           validators=[MimetypeValidator('text/xml')]
                           )

    def clean_file(self):
        file = self.cleaned_data.get('file', None)
        if not file:
            raise forms.ValidationError('Missing file')
        try:
            extension = os.path.splitext(file.name)[1][1:].lower()
            if extension in self.ALLOWED_TYPES:
                return file
            else:
                raise forms.ValidationError('File types is not allowed')
        except Exception as e:
            raise forms.ValidationError('Can not identify file type')