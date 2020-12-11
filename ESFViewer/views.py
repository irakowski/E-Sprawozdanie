from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.http import HttpResponse
from . import forms
import xml.etree.ElementTree as ET
import xmlschema
from .validators import xsd_check
# Create your views here.
from .desc import description_dict, rzis, zmiany, rachunek

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
            xml_text = ''
            for line in file_in_memory:
                xml_text = xml_text + line.decode()
            #check xml matches its schema for this type
            valid = xsd_check(xml_text)
            if not valid:
                return HttpResponse("File does not match financial statements structure")
            else:
                #parsing
                data = parse_txt(xml_text)
                return render(self.request, 'esfviewer/output.html', 
                    {"data": data, "desc" : description_dict, 'rzis':rzis, 'zmiany': zmiany, 'rachunek': rachunek})
        return render(self.request, self.template_name, {'form': form})