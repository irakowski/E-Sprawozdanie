from django.shortcuts import render
from django.views import generic
from . import forms
import xml.etree.ElementTree as ET
# Create your views here.

class LandingPage(generic.TemplateView):
    template_name = 'esfviewer/index.html'

from .xml_parse import parse_txt
class FormView(generic.FormView):
    form_class = forms.UploadFinancialStatementForm
    template_name = 'esfviewer/upload_form.html'
    #success_url = "thanks"

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            file_in_memory = form.cleaned_data.get('file')
            str_text = ''
            for line in file_in_memory:
                str_text = str_text + line.decode()
            data = parse_txt(str_text)
            return render(self.request, 'esfviewer/output.html',
                       {"data": data})