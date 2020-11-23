from django import forms

class UploadFinancialStatementForm(forms.Form):
    
    title = forms.CharField(max_length=150)
    file = forms.FileField(widget=forms.FileInput(attrs={'accept': 'application/xml, text/xml'}))

    ALLOWED_TYPES = ['xml', 'xsd']

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